"""
Database configuration and session management.

This module provides SQLModel engine, session factory, and FastAPI dependencies
for database access using PostgreSQL via psycopg (version 3).
"""
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine, text
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Convert postgresql:// to postgresql+psycopg:// for psycopg3 driver
database_url = str(settings.DATABASE_URL)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Create database engine with psycopg driver
engine = create_engine(
    database_url,
    echo=settings.DEBUG,  # Log SQL statements in debug mode
    pool_pre_ping=True,  # Verify connections before using them
    # Use NullPool for testing to avoid connection issues
    # In production, you can remove this to use default pooling
    poolclass=NullPool if settings.is_development else None,
)


def init_db() -> None:
    """
    Initialize the database.
    
    Creates all tables defined in SQLModel models.
    
    Note: In production, use Alembic migrations instead of create_all().
    This function is mainly for testing and development.
    """
    from sqlmodel import SQLModel
    
    logger.info("Initializing database tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized")


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    This is a FastAPI dependency that provides a database session
    for the duration of a request. The session is automatically
    closed after the request completes.
    
    Usage:
        @app.get("/items")
        def get_items(session: SessionDep):
            items = session.exec(select(Item)).all()
            return items
    
    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Type alias for FastAPI dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
