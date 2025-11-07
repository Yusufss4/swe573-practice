#!/usr/bin/env python
"""Migration to add timezone field to users table.

This migration adds the timezone column to the users table
to support timezone-aware time slot handling.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, text

from app.core.db import engine, check_db_connection


def upgrade():
    """Add timezone column to users table."""
    print("Adding timezone column to users table...")
    
    with Session(engine) as session:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'timezone'
        """)
        result = session.exec(check_query).first()
        
        if result:
            print("✅ Column 'timezone' already exists in users table")
            return
        
        # Add column with default value
        alter_query = text("""
            ALTER TABLE users 
            ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC' NOT NULL
        """)
        session.exec(alter_query)
        session.commit()
        print("✅ Column 'timezone' added successfully (default: UTC)")


def main():
    """Run the migration."""
    print("=" * 60)
    print("Migration: Add timezone to users")
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
    print("\nNote: All existing users now have timezone='UTC' as default.")
    print("Users can update their timezone through profile settings.")


if __name__ == "__main__":
    main()
