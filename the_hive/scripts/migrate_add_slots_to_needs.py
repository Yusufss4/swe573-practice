#!/usr/bin/env python
"""Migration to add available_slots to needs table.

This migration adds the available_slots column to the needs table
to support scheduling for both offers and needs.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, text

from app.core.db import engine, check_db_connection


def upgrade():
    """Add available_slots column to needs table."""
    print("Adding available_slots column to needs table...")
    
    with Session(engine) as session:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'needs' 
            AND column_name = 'available_slots'
        """)
        result = session.exec(check_query).first()
        
        if result:
            print("✅ Column 'available_slots' already exists in needs table")
            return
        
        # Add column
        alter_query = text("""
            ALTER TABLE needs 
            ADD COLUMN available_slots TEXT
        """)
        session.exec(alter_query)
        session.commit()
        print("✅ Column 'available_slots' added successfully")


def main():
    """Run the migration."""
    print("=" * 60)
    print("Migration: Add available_slots to needs")
    print("=" * 60)
    
    # Check database connection
    print("\nChecking database connection...")
    if not check_db_connection():
        print("❌ Database connection failed")
        sys.exit(1)
    print("✅ Database connection successful")
    
    # Run upgrade
    upgrade()
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
