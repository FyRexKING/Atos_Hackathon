"""
API routes for ticket management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.ticket import TicketInput, TicketResponse
from app.services.pipeline import TicketPipeline
from app.db.database import get_db, Ticket, UserRole
from app.routes.auth import get_current_user
from app.db.database import User

router = APIRouter(prefix="/api", tags=["tickets"])

# Initialize pipeline
pipeline = TicketPipeline()


@router.post("/ticket", response_model=TicketResponse)
async def create_ticket(
    ticket_input: TicketInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TicketResponse:
    """
    Create and process a support ticket. Only clients and admins can create.
    """
    if current_user.role not in [UserRole.CLIENT, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Unable to create ticket with this role")

    try:
        response = pipeline.process_ticket(ticket_input, db, current_user)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")


@router.get("/ticket/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a ticket by ID.

    Args:
        ticket_id: ID of the ticket
        current_user: Authenticated user
        db: Database session

    Returns:
        Ticket details

    Raises:
        HTTPException: If ticket not found or access denied
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check permissions
    if current_user.role.value == "client" and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ticket


@router.get("/tickets/pending")
async def get_pending_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tickets pending human review (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")

    tickets = db.query(Ticket).filter(Ticket.status == "pending_review").all()
    return {"tickets": tickets, "count": len(tickets)}


@router.get("/admin/tickets")
async def get_all_tickets_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to view all tickets and pipeline analysis details.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")

    tickets = db.query(Ticket).all()
    
    # Enrich tickets with creator info
    enriched_tickets = []
    for ticket in tickets:
        ticket_dict = {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'category': ticket.category,
            'priority': ticket.priority,
            'impact': ticket.impact,
            'confidence_score': ticket.confidence_score,
            'decision': ticket.decision,
            'status': ticket.status,
            'created_at': ticket.created_at,
            'resolved_at': ticket.resolved_at,
            'resolution': ticket.resolution,
            'human_resolution': ticket.human_resolution,
            'ai_explanation': ticket.ai_explanation,
            'similarity_data': ticket.similarity_data,
            'confidence_breakdown': ticket.confidence_breakdown,
            'assigned_team': ticket.assigned_team,
            'rejection_message': ticket.rejection_message,
            'resolution_source': ticket.resolution_source,
            'user_id': ticket.user_id,
            'created_by': None
        }
        
        # Get creator info if user_id exists
        if ticket.user_id:
            creator = db.query(User).filter(User.id == ticket.user_id).first()
            if creator:
                ticket_dict['created_by'] = {
                    'id': creator.id,
                    'name': creator.full_name,
                    'email': creator.email
                }
        
        enriched_tickets.append(ticket_dict)
    
    return {"tickets": enriched_tickets, "count": len(enriched_tickets)}



@router.get("/tickets/my")
async def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's tickets (clients only).
    Returns all ticket details including resolution, rejection message, and assignment info.
    """
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Access denied")

    tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).all()
    
    # Enrich tickets with all fields
    enriched_tickets = []
    for ticket in tickets:
        ticket_dict = {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'category': ticket.category,
            'priority': ticket.priority,
            'impact': ticket.impact,
            'confidence_score': ticket.confidence_score,
            'decision': ticket.decision,
            'status': ticket.status,
            'created_at': ticket.created_at,
            'resolved_at': ticket.resolved_at,
            'resolution': ticket.resolution,
            'human_resolution': ticket.human_resolution,
            'ai_explanation': ticket.ai_explanation,
            'similarity_data': ticket.similarity_data,
            'confidence_breakdown': ticket.confidence_breakdown,
            'assigned_team': ticket.assigned_team,
            'rejection_message': ticket.rejection_message,
            'resolution_source': ticket.resolution_source,
            'user_id': ticket.user_id
        }
        enriched_tickets.append(ticket_dict)
    
    return {"tickets": enriched_tickets, "count": len(enriched_tickets)}


@router.patch("/ticket/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: int,
    body: dict,
    db: Session = Depends(get_db)
):
    """
    Mark a ticket as resolved by human (human-in-the-loop).

    Args:
        ticket_id: ID of the ticket
        body: Request body with resolution
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: If ticket not found
    """
    resolution = body.get("resolution")
    if not resolution:
        raise HTTPException(status_code=400, detail="Resolution is required")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = "resolved"
    ticket.human_resolution = resolution
    ticket.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket resolved",
        "ticket": ticket
    }


@router.patch("/ticket/{ticket_id}/reject")
async def reject_ticket(
    ticket_id: int,
    body: dict,
    db: Session = Depends(get_db)
):
    """
    Mark a ticket as rejected (human-in-the-loop).

    Args:
        ticket_id: ID of the ticket
        body: Request body with reason
        db: Database session

    Returns:
        Updated ticket

    Raises:
        HTTPException: If ticket not found
    """
    reason = body.get("reason")
    if not reason:
        raise HTTPException(status_code=400, detail="Reason is required")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = "rejected"
    ticket.human_resolution = f"Rejected: {reason}"

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket rejected",
        "ticket": ticket
    }


@router.get("/tickets/auto-resolved")
async def get_auto_resolved_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all auto-resolved tickets (admin only).
    Shows tickets that were automatically resolved by the AI system.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")

    tickets = db.query(Ticket).filter(
        Ticket.decision == "auto_resolve",
        Ticket.status == "resolved"
    ).order_by(Ticket.resolved_at.desc()).all()
    
    enriched_tickets = []
    for ticket in tickets:
        ticket_dict = {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'category': ticket.category,
            'priority': ticket.priority,
            'impact': ticket.impact,
            'confidence_score': ticket.confidence_score,
            'decision': ticket.decision,
            'status': ticket.status,
            'created_at': ticket.created_at,
            'resolved_at': ticket.resolved_at,
            'resolution': ticket.resolution,
            'ai_explanation': ticket.ai_explanation,
            'similarity_data': ticket.similarity_data,
            'confidence_breakdown': ticket.confidence_breakdown,
            'resolution_source': ticket.resolution_source,
            'created_by': None
        }
        
        # Get creator info
        if ticket.user_id:
            creator = db.query(User).filter(User.id == ticket.user_id).first()
            if creator:
                ticket_dict['created_by'] = {
                    'id': creator.id,
                    'name': creator.full_name,
                    'email': creator.email
                }
        
        enriched_tickets.append(ticket_dict)
    
    return {
        "auto_resolved_tickets": enriched_tickets,
        "count": len(enriched_tickets)
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get ticket statistics.

    Returns:
        Statistics on ticket processing
    """
    total = db.query(Ticket).count()
    resolved = db.query(Ticket).filter(Ticket.status == "resolved").count()
    pending = db.query(Ticket).filter(Ticket.status == "pending_review").count()
    rejected = db.query(Ticket).filter(Ticket.status == "rejected").count()

    # Calculate average confidence for auto-resolved tickets
    auto_resolved = db.query(Ticket).filter(
        Ticket.decision == "auto_resolve"
    ).all()
    avg_confidence = (
        sum(t.confidence_score for t in auto_resolved) / len(auto_resolved)
        if auto_resolved else 0
    )

    return {
        "total_tickets": total,
        "resolved": resolved,
        "pending_review": pending,
        "rejected": rejected,
        "auto_resolved": len(auto_resolved),
        "avg_confidence": float(avg_confidence)
    }
