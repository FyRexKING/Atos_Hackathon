"""
Database configuration and models using SQLAlchemy.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

# Import quality ticket seeding
from seed_quality_tickets import add_quality_tickets_to_db

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickets.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    CLIENT = "client"
    AGENT = "agent"  # Support agents


class User(Base):
    """SQLAlchemy model for users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.value})>"


class Ticket(Base):
    """SQLAlchemy model for tickets in database."""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # auth, billing, infra, ui, api
    priority = Column(String(50), nullable=False)  # low, medium, high
    impact = Column(String(50), nullable=False)    # low, medium, high
    confidence_score = Column(Float, nullable=False)
    decision = Column(String(20), nullable=False)  # auto_resolve, human_review
    status = Column(String(20), nullable=False)    # pending_review, resolved, rejected
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution = Column(Text, nullable=True)
    human_resolution = Column(Text, nullable=True)

    # AI Analysis fields
    ai_explanation = Column(Text, nullable=True)  # AI's explanation of the decision
    similarity_data = Column(JSON, nullable=True)  # JSON with similar tickets and scores
    confidence_breakdown = Column(JSON, nullable=True)  # JSON with confidence weights

    # Admin Action fields
    assigned_team = Column(String(100), nullable=True)  # Team assigned to the ticket
    rejection_message = Column(Text, nullable=True)  # Custom rejection message to client
    resolution_source = Column(String(20), nullable=True, default='pending')  # 'ai', 'admin', 'pending'

    # Add user relationship
    user_id = Column(Integer, nullable=True)  # Link to user who created ticket

    def __repr__(self):
        return f"<Ticket(id={self.id}, title={self.title}, status={self.status})>"


class KnowledgeBase(Base):
    """SQLAlchemy model for Knowledge Base articles."""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, unique=True)
    content = Column(Text, nullable=False)  # Full article content
    category = Column(String(50), nullable=False)  # auth, billing, infra, ui, api, general
    tags = Column(JSON, nullable=True)  # List of tags for quick search
    solution_steps = Column(JSON, nullable=True)  # List of step-by-step solutions
    related_categories = Column(JSON, nullable=True)  # Categories this applies to
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title={self.title}, category={self.category})>"


class RecommendedSolution(Base):
    """Solutions recommended by AI for escalated tickets."""
    __tablename__ = "recommended_solutions"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, nullable=False)  # Link to ticket
    solution_type = Column(String(50), nullable=False)  # 'kb_article', 'historical_match', 'ai_suggestion'
    solution_content = Column(Text, nullable=False)  # The recommended solution
    relevance_score = Column(Float, nullable=False)  # 0-1 confidence in this solution
    action_steps = Column(JSON, nullable=True)  # Step-by-step actions
    reference_id = Column(Integer, nullable=True)  # Reference to KB ID or historical ticket ID
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<RecommendedSolution(id={self.id}, ticket_id={self.ticket_id})>"


def get_db():
    """Dependency for getting database session in FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def add_sample_tickets():
    """Add sample tickets for testing."""
    db = SessionLocal()
    try:
        # Check if samples already exist
        existing = db.query(Ticket).count()
        if existing > 0:
            return

        sample_tickets = [
            Ticket(
                title="Cannot login to account",
                description="I've tried multiple times but keep getting an authentication error. The email and password are correct.",
                category="auth",
                priority="high",
                impact="high",
                confidence_score=0.85,
                decision="auto_resolve",
                status="resolved",
                resolution="User password was reset successfully. Session cleared. User can now login."
            ),
            Ticket(
                title="Billing discrepancy in invoice",
                description="The monthly invoice shows double the expected amount. I was charged twice for the same service.",
                category="billing",
                priority="high",
                impact="medium",
                confidence_score=0.78,
                decision="human_review",
                status="pending_review"
            ),
            Ticket(
                title="API returning 500 errors",
                description="The /api/users endpoint is returning 500 Internal Server Error consistently.",
                category="api",
                priority="high",
                impact="high",
                confidence_score=0.72,
                decision="human_review",
                status="pending_review"
            ),
            Ticket(
                title="UI button not responsive",
                description="The submit button on the contact form doesn't respond to clicks on Safari browser.",
                category="ui",
                priority="medium",
                impact="low",
                confidence_score=0.65,
                decision="human_review",
                status="pending_review"
            ),
            Ticket(
                title="Database connection timeout",
                description="Infrastructure service experiencing database connection timeouts. Affecting production environment.",
                category="infra",
                priority="high",
                impact="high",
                confidence_score=0.88,
                decision="human_review",
                status="pending_review"
            ),
        ]

        db.add_all(sample_tickets)
        db.commit()
        print(f"✓ Added {len(sample_tickets)} sample tickets to database")
        
        # Also add quality tickets for better learning
        add_quality_tickets_to_db(db)
    except Exception as e:
        print(f"Error adding sample tickets: {e}")
        db.rollback()
    finally:
        db.close()


def create_default_admin():
    """Create default admin user if it doesn't exist."""
    from app.core.auth import get_password_hash

    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            return

        # Create default admin user
        hashed_password = get_password_hash("admin123")
        admin_user = User(
            email="admin@support.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=hashed_password,
            role=UserRole.ADMIN
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Default admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@support.com")

    except Exception as e:
        print(f"Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()
