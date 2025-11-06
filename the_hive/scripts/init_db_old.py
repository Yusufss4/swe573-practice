"""
Initialize database tables.

This script creates all database tables defined in SQLModel models.
Run this before starting the application for the first time.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.db import engine
from app.core.logging import setup_logging, get_logger
from sqlmodel import SQLModel

# Import all models to register them with SQLModel
from app.models.user import User

setup_logging()
logger = get_logger(__name__)


#!/usr/bin/env python
"""Database initialization script for The Hive.

This script:
1. Creates all database tables from SQLModel models
2. Seeds basic data (1 user + 1 offer) for sanity checks
3. Validates foreign key constraints

SRS Requirements:
- Database schema from §3.5.1
- User starting balance: 5 hours (FR-7.1)
- Offer default expiration: 7 days
- Capacity default: 1
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
from sqlmodel import SQLModel, Session, select

from app.core.db import engine, check_db_connection
from app.core.config import settings

# Import all models to ensure they're registered with SQLModel
from app.models import (
    User,
    UserRole,
    Tag,
    Offer,
    OfferStatus,
    Need,
    NeedStatus,
    OfferTag,
    NeedTag,
    Participant,
    LedgerEntry,
    Transfer,
    TransactionType,
    Comment,
    Report,
)


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully")


def seed_basic_data():
    """Seed database with basic test data.
    
    Creates:
    - 1 test user with 5 hour starting balance
    - 1 tag
    - 1 active offer linked to the user and tag
    """
    print("\nSeeding basic data...")
    
    with Session(engine) as session:
        # Create a test user (FR-7.1: starts with 5 hours)
        user = User(
            email="alice@example.com",
            username="alice",
            password_hash="$2b$12$dummy.hash.for.testing",  # Dummy hash
            full_name="Alice Wonder",
            description="Test user for The Hive",
            role=UserRole.USER,
            balance=5.0,  # SRS: starting balance
            location_lat=40.7128,
            location_lon=-74.0060,
            location_name="New York, NY",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"✅ Created user: {user.username} (ID: {user.id}, Balance: {user.balance}h)")
        
        # Create an initial ledger entry for the starting balance
        ledger_entry = LedgerEntry(
            user_id=user.id,  # type: ignore
            debit=0.0,
            credit=5.0,
            balance=5.0,
            transaction_type=TransactionType.INITIAL,
            description="Initial TimeBank balance",
        )
        session.add(ledger_entry)
        session.commit()
        print(f"✅ Created initial ledger entry for {user.username}")
        
        # Create a tag
        tag = Tag(
            name="tutoring",
            description="Educational tutoring services",
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
        print(f"✅ Created tag: {tag.name} (ID: {tag.id})")
        
        # Create an offer (SRS: 7-day default, capacity=1)
        offer = Offer(
            creator_id=user.id,  # type: ignore
            title="Python Programming Tutoring",
            description="Offering help with Python basics and web development",
            is_remote=True,
            location_lat=40.7128,
            location_lon=-74.0060,
            location_name="New York, NY",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            capacity=1,  # SRS default
            accepted_count=0,
            status=OfferStatus.ACTIVE,
        )
        session.add(offer)
        session.commit()
        session.refresh(offer)
        print(f"✅ Created offer: {offer.title} (ID: {offer.id}, Capacity: {offer.capacity})")
        
        # Link offer to tag
        offer_tag = OfferTag(
            offer_id=offer.id,  # type: ignore
            tag_id=tag.id,  # type: ignore
        )
        session.add(offer_tag)
        session.commit()
        print(f"✅ Linked offer to tag: {tag.name}")
        
        # Update tag usage count
        tag.usage_count = 1
        session.add(tag)
        session.commit()
        
    print("\n✅ Seed data created successfully")


def validate_schema():
    """Perform basic validation of the schema."""
    print("\nValidating schema...")
    
    with Session(engine) as session:
        # Check that we can query the seeded data
        user = session.exec(select(User).where(User.username == "alice")).first()
        if not user:
            raise ValueError("❌ User not found - seed failed")
        
        offer = session.exec(select(Offer).where(Offer.creator_id == user.id)).first()
        if not offer:
            raise ValueError("❌ Offer not found - FK constraint may be broken")
        
        tag = session.exec(select(Tag).where(Tag.name == "tutoring")).first()
        if not tag:
            raise ValueError("❌ Tag not found - seed failed")
        
        offer_tag = session.exec(
            select(OfferTag).where(
                OfferTag.offer_id == offer.id,
                OfferTag.tag_id == tag.id
            )
        ).first()
        if not offer_tag:
            raise ValueError("❌ OfferTag association not found - FK constraint may be broken")
        
        ledger = session.exec(select(LedgerEntry).where(LedgerEntry.user_id == user.id)).first()
        if not ledger:
            raise ValueError("❌ Ledger entry not found - FK constraint may be broken")
        
    print("✅ Schema validation passed - FK constraints are valid")


def main():
    """Main initialization routine."""
    print("=" * 60)
    print("The Hive - Database Initialization")
    print("=" * 60)
    
    # Check database connection
    print("\nChecking database connection...")
    if not check_db_connection():
        print("❌ Database connection failed")
        sys.exit(1)
    print("✅ Database connection successful")
    
    # Create tables
    create_tables()
    
    # Seed basic data
    seed_basic_data()
    
    # Validate schema
    validate_schema()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now start the application with:")
    print("  uv run uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()


def create_tables():
    """Create all database tables."""
    engine = create_engine_with_url_fix(settings.DATABASE_URL)
    
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully")
    
    return engine


def seed_basic_data(engine):
    """Seed database with basic test data.
    
    Creates:
    - 1 test user with 5 hour starting balance
    - 1 tag
    - 1 active offer linked to the user and tag
    """
    print("\nSeeding basic data...")
    
    with Session(engine) as session:
        # Create a test user (FR-7.1: starts with 5 hours)
        user = User(
            email="alice@example.com",
            username="alice",
            password_hash="$2b$12$dummy.hash.for.testing",  # Dummy hash
            full_name="Alice Wonder",
            description="Test user for The Hive",
            role=UserRole.USER,
            balance=5.0,  # SRS: starting balance
            location_lat=40.7128,
            location_lon=-74.0060,
            location_name="New York, NY",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"✅ Created user: {user.username} (ID: {user.id}, Balance: {user.balance}h)")
        
        # Create an initial ledger entry for the starting balance
        ledger_entry = LedgerEntry(
            user_id=user.id,
            debit=0.0,
            credit=5.0,
            balance=5.0,
            transaction_type="initial",
            description="Initial TimeBank balance",
        )
        session.add(ledger_entry)
        session.commit()
        print(f"✅ Created initial ledger entry for {user.username}")
        
        # Create a tag
        tag = Tag(
            name="tutoring",
            description="Educational tutoring services",
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
        print(f"✅ Created tag: {tag.name} (ID: {tag.id})")
        
        # Create an offer (SRS: 7-day default, capacity=1)
        offer = Offer(
            creator_id=user.id,
            title="Python Programming Tutoring",
            description="Offering help with Python basics and web development",
            is_remote=True,
            location_lat=40.7128,
            location_lon=-74.0060,
            location_name="New York, NY",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            capacity=1,  # SRS default
            accepted_count=0,
            status=OfferStatus.ACTIVE,
        )
        session.add(offer)
        session.commit()
        session.refresh(offer)
        print(f"✅ Created offer: {offer.title} (ID: {offer.id}, Capacity: {offer.capacity})")
        
        # Link offer to tag
        offer_tag = OfferTag(
            offer_id=offer.id,
            tag_id=tag.id,
        )
        session.add(offer_tag)
        session.commit()
        print(f"✅ Linked offer to tag: {tag.name}")
        
        # Update tag usage count
        tag.usage_count = 1
        session.add(tag)
        session.commit()
        
    print("\n✅ Seed data created successfully")


def validate_schema():
    """Perform basic validation of the schema."""
    print("\nValidating schema...")
    
    engine = create_engine_with_url_fix(settings.DATABASE_URL)
    
    with Session(engine) as session:
        # Check that we can query the seeded data
        user = session.query(User).filter(User.username == "alice").first()
        if not user:
            raise ValueError("❌ User not found - seed failed")
        
        offer = session.query(Offer).filter(Offer.creator_id == user.id).first()
        if not offer:
            raise ValueError("❌ Offer not found - FK constraint may be broken")
        
        tag = session.query(Tag).filter(Tag.name == "tutoring").first()
        if not tag:
            raise ValueError("❌ Tag not found - seed failed")
        
        offer_tag = session.query(OfferTag).filter(
            OfferTag.offer_id == offer.id,
            OfferTag.tag_id == tag.id
        ).first()
        if not offer_tag:
            raise ValueError("❌ OfferTag association not found - FK constraint may be broken")
        
        ledger = session.query(LedgerEntry).filter(LedgerEntry.user_id == user.id).first()
        if not ledger:
            raise ValueError("❌ Ledger entry not found - FK constraint may be broken")
        
    print("✅ Schema validation passed - FK constraints are valid")


def main():
    """Main initialization routine."""
    print("=" * 60)
    print("The Hive - Database Initialization")
    print("=" * 60)
    
    # Check database connection
    print("\nChecking database connection...")
    if not check_db_connection():
        print("❌ Database connection failed")
        sys.exit(1)
    print("✅ Database connection successful")
    
    # Create tables
    engine = create_tables()
    
    # Seed basic data
    seed_basic_data(engine)
    
    # Validate schema
    validate_schema()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now start the application with:")
    print("  uv run uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    init_db()
