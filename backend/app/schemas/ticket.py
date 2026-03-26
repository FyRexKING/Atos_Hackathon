"""
Pydantic schemas for ticket system.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TicketInput(BaseModel):
    """Input schema for ticket creation."""
    title: str = Field(..., min_length=5, max_length=200, description="Ticket title")
    description: str = Field(..., min_length=10, max_length=2000, description="Ticket description")


class ClassificationOutput(BaseModel):
    """Classification output from Gemini."""
    category: str = Field(..., description="Ticket category: auth, billing, infra, ui, api")
    priority: str = Field(..., description="Priority level: low, medium, high")
    impact: str = Field(..., description="Impact level: low, medium, high")


class SimilarTicket(BaseModel):
    """Represents a similar ticket in the database."""
    ticket_id: int
    title: str
    category: str
    similarity_score: float
    status: str


class SimilarityOutput(BaseModel):
    """Similarity search results."""
    similar_tickets: List[SimilarTicket] = Field(default=[], description="Top 3 similar tickets")
    avg_similarity: float = Field(default=0.0, description="Average similarity score")


class ConfidenceOutput(BaseModel):
    """Confidence scoring details."""
    score: float = Field(..., description="Overall confidence score (0-1)")
    similarity_weight: float
    category_match_weight: float
    impact_penalty_weight: float


class ResolutionOutput(BaseModel):
    """Auto-resolution details."""
    resolution: str
    explanation: str


class TicketResponse(BaseModel):
    """Complete ticket processing response."""
    ticket_id: Optional[int] = None
    title: str
    classification: ClassificationOutput
    similarity: SimilarityOutput
    confidence: ConfidenceOutput
    decision: str = Field(..., description="auto_resolve or human_review")
    explanation: str = Field(..., description="Human-readable explanation of decision")
    resolution: Optional[ResolutionOutput] = None
    status: str = Field(..., description="pending_review or resolved")


class TicketDB(BaseModel):
    """Database model for stored ticket."""
    id: Optional[int] = None
    title: str
    description: str
    category: str
    priority: str
    impact: str
    confidence_score: float
    decision: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    human_resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    # AI Analysis fields
    ai_explanation: Optional[str] = None
    similarity_data: Optional[dict] = None
    confidence_breakdown: Optional[dict] = None

    # Admin Action fields
    assigned_team: Optional[str] = None
    rejection_message: Optional[str] = None
    resolution_source: Optional[str] = None

    class Config:
        from_attributes = True
