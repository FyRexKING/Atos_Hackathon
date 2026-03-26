"""
Admin API routes for user and system management.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.auth import get_current_user
from app.db.database import get_db, User, UserRole, Ticket

router = APIRouter(prefix="/api/admin", tags=["admin"])


# Request schemas for ticket actions
class AssignTicketRequest(BaseModel):
    """Request to assign ticket to a team."""
    team: str
    note: str = ""


class RejectTicketRequest(BaseModel):
    """Request to reject a ticket with a message."""
    message: str


class ApproveAIResolutionRequest(BaseModel):
    """Request to approve AI resolution."""
    note: str = ""

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    users = db.query(User).all()
    return {"users": users, "count": len(users)}

@router.post("/users/{user_id}/promote")
async def promote_user_to_admin(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Promote a user to admin role (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="User is already an admin")

    user.role = UserRole.ADMIN
    db.commit()
    db.refresh(user)

    return {"message": f"User {user.username} promoted to admin", "user": user}


# ============ TICKET ACTION ENDPOINTS ============

@router.post("/ticket/{ticket_id}/assign")
async def assign_ticket_to_team(
    ticket_id: int,
    request: AssignTicketRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign ticket to a specific team (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.assigned_team = request.team
    ticket.status = "assigned"
    ticket.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "message": f"Ticket assigned to {request.team}",
        "ticket": ticket
    }


@router.post("/ticket/{ticket_id}/reject")
async def reject_ticket(
    ticket_id: int,
    request: RejectTicketRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject ticket with custom message sent to client (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.rejection_message = request.message
    ticket.status = "rejected"
    ticket.resolution_source = "admin"
    ticket.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "message": "Ticket rejected - message sent to client",
        "ticket": ticket
    }


@router.post("/ticket/{ticket_id}/approve-ai")
async def approve_ai_resolution(
    ticket_id: int,
    request: ApproveAIResolutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve and finalize AI resolution (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.decision != "auto_resolve":
        raise HTTPException(status_code=400, detail="Ticket was not auto-resolved by AI")

    ticket.status = "resolved"
    ticket.resolution_source = "ai"
    ticket.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "message": "AI resolution approved and finalized",
        "ticket": ticket
    }