"""
Admin API Routes - For managing ticket assignments, recommendations, and escalations.
Allows admins to:
- View ticket recommendations and action plans
- Assign tickets to teams
- View suggested solutions
- Make manual decisions on escalated tickets
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db, Ticket, RecommendedSolution, User, UserRole
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin/recommendations", tags=["admin", "recommendations"])


# Response Models
class SolutionStep(BaseModel):
    step: int
    action: str
    details: str
    priority: str


class ActionPlanResponse(BaseModel):
    total_steps: int
    estimated_time: str
    difficulty: str
    steps: List[SolutionStep]


class SuggestedSolution(BaseModel):
    rank: int
    type: str  # 'historical_match', 'kb_article', 'ai_suggestion'
    title: str
    confidence: float
    solution: str
    action_steps: List[str]
    source: str


class ExplainabilityResponse(BaseModel):
    reasoning_chain: str
    confidence_breakdown: dict
    recommended_team: str


class RecommendationsResponse(BaseModel):
    ticket_id: int
    confidence_score: float
    is_high_impact: bool
    is_new_issue_type: bool
    action_plan: ActionPlanResponse
    suggested_solutions: List[SuggestedSolution]
    explainability: ExplainabilityResponse


class AssignTicketRequest(BaseModel):
    assigned_to_team: str
    admin_notes: Optional[str] = None


class ResponseRequest(BaseModel):
    resolution_text: str


@router.get("/ticket/{ticket_id}", response_model=RecommendationsResponse)
async def get_ticket_recommendations(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive recommendations for a ticket requiring human review.
    Only admins and agents can view this.
    """
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get recommendations from ticket's similarity_data
    rec_data = ticket.similarity_data.get("recommendations", {}) if ticket.similarity_data else {}
    action_plan_data = rec_data.get("action_plan", {})
    
    # Convert action plan steps to SolutionStep objects
    steps = []
    for step_data in action_plan_data.get("steps", []):
        steps.append(SolutionStep(
            step=step_data.get("step", 0),
            action=step_data.get("action", ""),
            details=step_data.get("details", ""),
            priority=step_data.get("priority", "medium")
        ))
    
    action_plan = ActionPlanResponse(
        total_steps=action_plan_data.get("total_steps", 0),
        estimated_time=action_plan_data.get("estimated_time", ""),
        difficulty=action_plan_data.get("difficulty", ""),
        steps=steps
    )
    
    # Convert suggested solutions
    suggested_solutions = []
    for idx, sol in enumerate(rec_data.get("suggested_solutions", [])):
        suggested_solutions.append(SuggestedSolution(
            rank=idx + 1,
            type=sol.get("type", "ai_suggestion"),
            title=sol.get("title", ""),
            confidence=sol.get("confidence", 0.0),
            solution=sol.get("solution", ""),
            action_steps=sol.get("action_steps", []),
            source=sol.get("source", "")
        ))
    
    # Build explainability
    explainability_data = rec_data.get("explainability", {})
    explainability = ExplainabilityResponse(
        reasoning_chain=explainability_data.get("reasoning_chain", ""),
        confidence_breakdown=explainability_data.get("confidence_breakdown", {}),
        recommended_team=explainability_data.get("recommended_team", "General Support Team")
    )
    
    return RecommendationsResponse(
        ticket_id=ticket.id,
        confidence_score=ticket.confidence_score,
        is_high_impact=rec_data.get("is_high_impact", False),
        is_new_issue_type=rec_data.get("is_new_issue_type", False),
        action_plan=action_plan,
        suggested_solutions=suggested_solutions,
        explainability=explainability
    )


@router.post("/ticket/{ticket_id}/assign")
async def assign_ticket_to_team(
    ticket_id: int,
    assign_request: AssignTicketRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin assigns a ticket to a specific team.
    Updates the ticket with team assignment and notes.
    """
    
    # Check permissions - only admins can assign
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can assign tickets")
    
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket with assignment
    ticket.assigned_team = assign_request.assigned_to_team
    ticket.status = "assigned"
    
    # Store admin notes
    if assign_request.admin_notes:
        if ticket.ai_explanation:
            ticket.ai_explanation += f"\n\nAdmin Notes: {assign_request.admin_notes}"
        else:
            ticket.ai_explanation = f"Admin Notes: {assign_request.admin_notes}"
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Ticket #{ticket_id} assigned to {assign_request.assigned_to_team}",
        "ticket_id": ticket.id
    }


@router.post("/ticket/{ticket_id}/resolve-manually")
async def resolve_ticket_manually(
    ticket_id: int,
    response_request: ResponseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin or agent manually resolves a ticket with custom resolution.
    Marks ticket as resolved with admin-provided solution.
    """
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket as resolved
    from datetime import datetime
    ticket.status = "resolved"
    ticket.human_resolution = response_request.resolution_text
    ticket.resolution_source = "admin"
    ticket.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Ticket #{ticket_id} resolved by admin",
        "ticket_id": ticket.id,
        "resolution_type": "manual_admin_resolution"
    }


@router.post("/ticket/{ticket_id}/reject")
async def reject_and_escalate(
    ticket_id: int,
    assign_request: AssignTicketRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject the AI recommendations and escalate to a different team.
    Stores rejection reason for audit trail.
    """
    
    # Check permissions - only admins
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can reject/escalate")
    
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket
    ticket.status = "assigned"
    ticket.assigned_team = assign_request.assigned_to_team
    ticket.rejection_message = assign_request.admin_notes or "Escalated by admin"
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Ticket #{ticket_id} escalated to {assign_request.assigned_to_team}",
        "ticket_id": ticket.id,
        "escalation_reason": assign_request.admin_notes
    }


@router.get("/ticket/{ticket_id}/solutions", response_model=List[SuggestedSolution])
async def get_recommended_solutions(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all recommended solutions for a ticket from the database.
    Includes solutions from KB articles, historical tickets, and AI suggestions.
    """
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all recommended solutions
    solutions = db.query(RecommendedSolution).filter(
        RecommendedSolution.ticket_id == ticket_id
    ).order_by(RecommendedSolution.id).all()
    
    if not solutions:
        raise HTTPException(status_code=404, detail="No solutions found for this ticket")
    
    return [
        SuggestedSolution(
            rank=idx + 1,
            type=sol.solution_type,
            title=f"{sol.solution_type.replace('_', ' ').title()} Solution",
            confidence=sol.relevance_score,
            solution=sol.solution_content,
            action_steps=sol.action_steps or [],
            source=f"Solution #{sol.id}"
        )
        for idx, sol in enumerate(solutions)
    ]
@router.get("/pending-tickets")
async def get_pending_tickets_with_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pending tickets that need admin review with their recommendations.
    Filtered by priority and impact for admin dashboard.
    """
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get pending tickets
    tickets = db.query(Ticket).filter(
        Ticket.status == "pending_review"
    ).order_by(
        Ticket.created_at.desc()
    ).all()
    
    pending_with_rec = []
    for ticket in tickets:
        rec_data = ticket.similarity_data.get("recommendations", {}) if ticket.similarity_data else {}
        pending_with_rec.append({
            "ticket_id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "confidence_score": ticket.confidence_score,
            "recommended_team": rec_data.get("recommended_team", "General Support Team"),
            "is_high_impact": rec_data.get("is_new_issue_type", False),
            "created_at": ticket.created_at.isoformat()
        })
    
    return pending_with_rec
