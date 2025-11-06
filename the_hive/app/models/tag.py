from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    """Semantic tag model for categorizing Offers and Needs.
    
    SRS Requirements:
    - FR-8.1: Semantic tags to describe Offers and Needs
    - FR-8.3: Users can create new tags freely
    - FR-8.4: Simple hierarchy inspired by WikiData
    """

    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Simple hierarchy: parent tag for categorization
    parent_id: Optional[int] = Field(default=None, foreign_key="tags.id")
    
    # Usage tracking
    usage_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
