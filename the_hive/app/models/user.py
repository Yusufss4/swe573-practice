"""
User model for the application.
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


# Preset avatar options - insect/nature themed for "The Hive"
PRESET_AVATARS = [
    # Insects
    "bee",
    "butterfly", 
    "ladybug",
    "ant",
    "cricket",
    "caterpillar",
    "snail",
    "spider",
    "mosquito",
    # Nature/animals
    "bird",
    "owl",
    "turtle",
    "frog",
    "rabbit",
    "fox",
    "bear",
    "wolf",
    "deer",
    "squirrel",
    # Plants
    "flower",
    "sunflower",
    "tree",
    "leaf",
    "mushroom",
    "cactus",
]


class User(SQLModel, table=True):
    """User model for authentication and profile management.
    
    SRS Requirements:
    - FR-1.1: Unique username, email, password
    - FR-7.1: Initial balance of 5 hours
    - NFR-5: Password stored as salted hash
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=50)
    password_hash: str = Field(max_length=255)  # NFR-5: salted hash
    full_name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)  # FR-2.4
    
    # Profile image: either preset name or custom base64 data URL
    # Using sa_column for TEXT type to store large base64 images (up to ~700KB encoded)
    profile_image: Optional[str] = Field(default=None, sa_column=Column(Text))
    profile_image_type: str = Field(default="preset")  # "preset" or "custom"
    
    # SRS: User role for permissions
    role: UserRole = Field(default=UserRole.USER, index=True)
    
    # SRS FR-7.1: TimeBank balance (starts at 5 hours)
    balance: float = Field(default=5.0)
    
    # Approximate location fields (SRS: NFR-7 - generalized location)
    location_lat: Optional[float] = Field(default=None)
    location_lon: Optional[float] = Field(default=None)
    location_name: Optional[str] = Field(default=None, max_length=255)  # e.g., "Brooklyn, NY"
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tags: list["UserTag"] = Relationship(back_populates="user")


class UserTag(SQLModel, table=True):
    """Association table for user profile tags."""
    
    __tablename__ = "user_tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    tag_name: str = Field(max_length=50, index=True)
    
    user: Optional[User] = Relationship(back_populates="tags")
