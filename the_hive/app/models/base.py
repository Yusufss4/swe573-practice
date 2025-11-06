"""
Example base model for the application.

This file shows how to create SQLModel models. Import your models
in migrations/env.py for Alembic autogeneration.
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for adding timestamp fields to models."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# Example: Uncomment when you want to create your first model
# class User(TimestampMixin, table=True):
#     """User model example."""
#     
#     id: Optional[int] = Field(default=None, primary_key=True)
#     email: str = Field(unique=True, index=True, max_length=255)
#     username: str = Field(unique=True, index=True, max_length=100)
#     hashed_password: str = Field(max_length=255)
#     is_active: bool = Field(default=True)
#     is_superuser: bool = Field(default=False)
