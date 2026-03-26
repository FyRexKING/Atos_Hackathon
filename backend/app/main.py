"""
Main FastAPI application for AI-powered support ticket system.
"""
from dotenv import load_dotenv
import os

# Load environment variables FIRST - before any other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db, add_sample_tickets, create_default_admin
from app.routes.ticket import router as ticket_router
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.recommendations import router as recommendations_router

# Initialize FastAPI app
app = FastAPI(
    title="AI Support Ticket System",
    description="Production-ready backend for AI-powered support ticket classification with Human-in-the-Loop",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(ticket_router)
app.include_router(admin_router)
app.include_router(recommendations_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    create_default_admin()
    add_sample_tickets()
    print("[OK] Database initialized")
    print("[OK] Sample tickets added")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Support Ticket System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /api/ticket": "Create and process a ticket",
            "GET /api/ticket/{ticket_id}": "Get ticket by ID",
            "GET /api/tickets/pending": "Get pending tickets",
            "PATCH /api/ticket/{ticket_id}/resolve": "Resolve ticket (human)",
            "PATCH /api/ticket/{ticket_id}/reject": "Reject ticket (human)",
            "GET /api/stats": "Get system statistics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Support Ticket System"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "False") == "True"
    )
