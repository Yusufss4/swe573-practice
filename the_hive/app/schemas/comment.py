"""
Schemas for comment operations.

SRS Requirements:
- FR-10.1: Comments only after completed exchange
- FR-10.2: Basic content moderation
- FR-10.3: Comments visible on profiles
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""
    recipient_id: int = Field(..., description="User receiving the comment")
    participant_id: int = Field(..., description="Completed participant/exchange record")
    content: str = Field(..., min_length=10, max_length=1000, description="Comment text")
    
    @validator('content')
    def validate_content(cls, v):
        """Basic content validation."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        
        # Check minimum meaningful length
        if len(v.strip()) < 10:
            raise ValueError("Comment must be at least 10 characters")
        
        return v.strip()


class CommentResponse(BaseModel):
    """Schema for comment response."""
    id: int
    from_user_id: int  # Match the model field name
    from_username: Optional[str] = None
    to_user_id: int  # Match the model field name
    to_username: Optional[str] = None
    participant_id: Optional[int]
    content: str
    is_approved: bool
    timestamp: datetime  # Match the model field name
    
    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    """Schema for paginated comment list."""
    items: list[CommentResponse]
    total: int
    skip: int
    limit: int


class CommentFilter(BaseModel):
    """Schema for filtering comments."""
    recipient_id: Optional[int] = None
    commenter_id: Optional[int] = None
    min_rating: Optional[int] = Field(None, ge=1, le=5)
    exclude_flagged: bool = True
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
