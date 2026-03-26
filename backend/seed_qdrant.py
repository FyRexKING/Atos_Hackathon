#!/usr/bin/env python3
"""
Script to seed Qdrant vector database with embeddings from sample tickets.
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import SessionLocal, Ticket
from app.services.similarity import SimilarityService

def seed_vector_db():
    """Seed Qdrant with embeddings from existing tickets."""
    load_dotenv()

    # Initialize similarity service
    similarity_service = SimilarityService()

    # Get all tickets from database
    db = SessionLocal()
    try:
        tickets = db.query(Ticket).all()
        print(f"Found {len(tickets)} tickets in database")

        # Seed each ticket
        for ticket in tickets:
            try:
                # Store embedding in Qdrant (upsert handles existing points)
                success = similarity_service.store_embedding(
                    ticket.id,
                    ticket.title,
                    ticket.description
                )
                if success:
                    print(f"✓ Seeded ticket #{ticket.id}: {ticket.title[:50]}...")
                else:
                    print(f"✗ Failed to seed ticket #{ticket.id}")
            except Exception as e:
                print(f"Error seeding ticket #{ticket.id}: {e}")

        print("Vector database seeding completed!")

    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_vector_db()