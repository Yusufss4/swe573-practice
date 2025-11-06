"""
User model for the application.
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User database model."""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    username: str = Field(unique=True, index=True, max_length=100, nullable=False)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
