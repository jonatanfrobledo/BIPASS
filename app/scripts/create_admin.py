#!/usr/bin/env python3
"""
Script to create an admin user for BIPASS API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session
from app.db.session import engine
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash


def create_admin_user():
    """Create an admin user"""
    with Session(engine) as session:
        # Check if admin already exists
        admin_email = "admin@bipass.com"
        existing_admin = session.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"Admin user with email {admin_email} already exists!")
            return
        
        # Create admin user
        admin_user = User(
            name="BIPASS Administrator",
            email=admin_email,
            password_hash=get_password_hash("admin123"),  # Change this password!
            role=UserRole.ADMIN
        )
        
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: admin123")
        print("Please change the password after first login!")


if __name__ == "__main__":
    create_admin_user()