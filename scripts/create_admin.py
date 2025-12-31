# ============================================================================
# scripts/create_admin.py - Create Admin User
# ============================================================================

"""
Create an admin user
Run: python scripts/create_admin.py
"""

import asyncio
import sys
import os
from getpass import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import AsyncSessionLocal
from core.models import User
from core.auth.password import PasswordManager
from sqlalchemy import select


async def create_admin():
    """Create admin user interactively"""
    
    print("🔐 Create Admin User")
    print("=" * 50)
    
    email = input("Email: ")
    name = input("Name: ")
    password = getpass("Password: ")
    password_confirm = getpass("Confirm Password: ")
    
    if password != password_confirm:
        print("❌ Passwords don't match!")
        return
    
    # Validate password
    is_strong, message = PasswordManager.validate_password_strength(password)
    if not is_strong:
        print(f"❌ {message}")
        return
    
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return
        
        # Create user
        password_hash = PasswordManager.hash_password(password)
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
            email_verified=True
        )
        
        db.add(user)
        await db.commit()
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   ID: {user.id}")


if __name__ == "__main__":
    asyncio.run(create_admin())
