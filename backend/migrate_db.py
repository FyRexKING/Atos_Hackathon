#!/usr/bin/env python3
"""
Database migration script to add AI analysis fields to tickets table.
Run this script to update the database schema for existing installations.
"""
import sqlite3
import os
from pathlib import Path
''
def migrate_database():
    """Add AI analysis columns to tickets table."""
    # Get database path
    db_path = Path(__file__).parent / "tickets.db"
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [row[1] for row in cursor.fetchall()]
        # Add new columns if they don't exist
        if 'ai_explanation' not in columns:
            print("Adding ai_explanation column...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN ai_explanation TEXT")
        if 'similarity_data' not in columns:
            print("Adding similarity_data column...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN similarity_data JSON")
        if 'confidence_breakdown' not in columns:
            print("Adding confidence_breakdown column...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN confidence_breakdown JSON")
        if 'assigned_team' not in columns:
            print("Adding assigned_team column...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN assigned_team TEXT")
        if 'rejection_message' not in columns:
            print("Adding rejection_message column...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN rejection_message TEXT")
        if 'resolution_source' not in columns:
            print("Adding resolution_source column...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN resolution_source TEXT DEFAULT 'pending'")
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()
if __name__ == "__main__":
    migrate_database()