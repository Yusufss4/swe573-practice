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


def init_db():
    """Create all database tables."""
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
