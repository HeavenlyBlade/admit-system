"""
Seed data script for ADMIT system.
Populates initial KB categories and creates default admin user.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.database import get_db_context
from models.schemas import KBCategory, AdminUser
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_categories():
    """Create initial KB categories for all departments"""
    print("Seeding KB categories...")
    
    categories = [
        # IBED Categories
        {"name": "Admission Requirements", "department": "IBED"},
        {"name": "Enrollment Steps", "department": "IBED"},
        {"name": "Programs Offered", "department": "IBED"},
        {"name": "Tuition and Payment", "department": "IBED"},
        {"name": "Scholarships", "department": "IBED"},
        {"name": "Contact Information", "department": "IBED"},
        
        # SHS Categories
        {"name": "Admission Requirements", "department": "SHS"},
        {"name": "Enrollment Steps", "department": "SHS"},
        {"name": "Programs Offered", "department": "SHS"},
        {"name": "Tuition and Payment", "department": "SHS"},
        {"name": "Scholarships", "department": "SHS"},
        {"name": "Contact Information", "department": "SHS"},
        
        # HED Categories
        {"name": "Admission Requirements", "department": "HED"},
        {"name": "Enrollment Steps", "department": "HED"},
        {"name": "Programs Offered", "department": "HED"},
        {"name": "Tuition and Payment", "department": "HED"},
        {"name": "Scholarships", "department": "HED"},
        {"name": "Contact Information", "department": "HED"},
        
        # TESDA Categories
        {"name": "Admission Requirements", "department": "TESDA"},
        {"name": "Enrollment Steps", "department": "TESDA"},
        {"name": "Programs Offered", "department": "TESDA"},
        {"name": "Tuition and Payment", "department": "TESDA"},
        {"name": "Scholarships", "department": "TESDA"},
        {"name": "Contact Information", "department": "TESDA"},
        
        # General Categories
        {"name": "About SACLI", "department": "GENERAL"},
        {"name": "Campus Facilities", "department": "GENERAL"},
        {"name": "Student Services", "department": "GENERAL"},
    ]
    
    async with get_db_context() as db:
        # Check if categories already exist
        result = await db.execute(select(KBCategory))
        existing = result.scalars().first()
        
        if existing:
            print("  ⚠ Categories already exist, skipping...")
            return
        
        # Insert categories
        for cat_data in categories:
            category = KBCategory(**cat_data)
            db.add(category)
        
        await db.commit()
        print(f"  ✓ Created {len(categories)} KB categories")


async def seed_admin_user():
    """Create default admin user account"""
    print("Creating default admin user...")
    
    # Default credentials (should be changed after first login)
    username = "admin"
    password = "admin123"  # CHANGE THIS IN PRODUCTION!
    
    async with get_db_context() as db:
        # Check if admin user already exists
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == username)
        )
        existing_admin = result.scalars().first()
        
        if existing_admin:
            print(f"  ⚠ Admin user '{username}' already exists, skipping...")
            return
        
        # Hash password and create admin user
        password_hash = pwd_context.hash(password)
        admin_user = AdminUser(
            username=username,
            password_hash=password_hash,
            role="admin"
        )
        
        db.add(admin_user)
        await db.commit()
        
        print(f"  ✓ Created admin user: {username}")
        print(f"  ⚠ Default password: {password}")
        print(f"  ⚠ IMPORTANT: Change this password immediately in production!")


async def seed_sample_kb_entries():
    """Create sample KB entries with dummy embeddings"""
    print("Creating sample KB entries...")
    
    # Note: This requires embeddings service to be implemented
    # For now, we'll skip this and let admin users add KB entries via dashboard
    print("  ⚠ Skipping sample KB entries (add via admin dashboard)")
    print("  ℹ After implementing embedding service, KB entries can be added through:")
    print("    - Admin dashboard UI")
    print("    - KB parser utility (utils/kb_parser.py)")


async def seed_database():
    """Main seed function"""
    print("=" * 60)
    print("ADMIT Database Seeding")
    print("=" * 60)
    
    await seed_categories()
    await seed_admin_user()
    await seed_sample_kb_entries()
    
    print("\n" + "=" * 60)
    print("Database seeding completed!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Start the server: uvicorn main:app --reload")
    print("  2. Login to admin dashboard with:")
    print("     Username: admin")
    print("     Password: admin123")
    print("  3. Add knowledge base content through the admin interface")


if __name__ == "__main__":
    asyncio.run(seed_database())
