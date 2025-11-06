"""
User schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: str = Field(min_length=3, max_length=255, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    username: str = Field(min_length=3, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    email: Optional[str] = Field(default=None, min_length=3, max_length=255, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
