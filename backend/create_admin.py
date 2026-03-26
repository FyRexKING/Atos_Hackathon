#!/usr/bin/env python3
"""
Script to create an admin user for the AI Support Ticket System.
Run this script to create your first admin user.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, User, UserRole
from app.core.auth import get_password_hash

def create_admin_user():
    """Create an admin user interactively."""
    print("Create Admin User for AI Support Ticket System")
    print("=" * 50)

    # Get user input
    email = input("Enter admin email: ").strip()
    username = input("Enter admin username: ").strip()
    full_name = input("Enter admin full name: ").strip()
    password = input("Enter admin password: ").strip()

    if not all([email, username, full_name, password]):
        print("Error: All fields are required!")
        return

    # Create admin user
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()

        if existing_user:
            print(f"Error: User with email '{email}' or username '{username}' already exists!")
            return

        # Create new admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            role=UserRole.ADMIN
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("\n✅ Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role.value}")
        print("\nYou can now login to the admin dashboard!")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()