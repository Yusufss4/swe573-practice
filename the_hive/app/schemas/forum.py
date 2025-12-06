"""
Schemas for forum operations.

SRS Requirements:
- FR-15: Basic forum with moderation hooks
- FR-15.1: Create/list topics (types: discussion, event)
- FR-15.2: Search by tag/keyword
- FR-15.3: Link optional Offer/Need to events
- FR-15.4: Events ordered by recency
- FR-15.5: Links visible both ways (bidirectional)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ForumTopicCreate(BaseModel):
    """Schema for creating a new forum topic."""
    topic_type: str = Field(..., description="Type: 'discussion' or 'event'")
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=10)
    
    # Event-specific fields (optional)
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None
    event_location: Optional[str] = Field(None, max_length=255)
    
    # Optional links to Offer/Need (FR-15.3)
    linked_offer_id: Optional[int] = None
    linked_need_id: Optional[int] = None
    
    @field_validator('topic_type')
    @classmethod
    def validate_topic_type(cls, v):
        """Validate topic type is discussion or event."""
        if v not in ['discussion', 'event']:
            raise ValueError("topic_type must be 'discussion' or 'event'")
        return v
    
    @field_validator('event_end_time')
    @classmethod
    def validate_event_times(cls, v, info):
        """Validate event end time is after start time."""
        if v is not None and 'event_start_time' in info.data:
            start = info.data.get('event_start_time')
            if start and v <= start:
                raise ValueError("event_end_time must be after event_start_time")
        return v
    
    @field_validator('linked_need_id')
    @classmethod
    def validate_no_double_link(cls, v, info):
        """Validate that only one link (offer or need) is set."""
        if v is not None and info.data.get('linked_offer_id') is not None:
            raise ValueError("Cannot link both offer and need to the same topic")
        return v


class ForumTopicUpdate(BaseModel):
    """Schema for updating a forum topic."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    tags: Optional[list[str]] = Field(None, max_length=10)
    
    # Event-specific fields
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None
    event_location: Optional[str] = Field(None, max_length=255)
    
    @field_validator('event_end_time')
    @classmethod
    def validate_event_times(cls, v, info):
        """Validate event end time is after start time."""
        if v is not None and 'event_start_time' in info.data:
            start = info.data.get('event_start_time')
            if start and v <= start:
                raise ValueError("event_end_time must be after event_start_time")
        return v


class LinkedItemInfo(BaseModel):
    """Schema for linked offer/need information (FR-15.5)."""
    id: int
    type: str  # 'offer' or 'need'
    title: str
    creator_id: int
    creator_username: Optional[str] = None


class ForumTopicResponse(BaseModel):
    """Schema for forum topic response."""
    id: int
    topic_type: str
    creator_id: int
    creator_username: Optional[str] = None
    creator_display_name: Optional[str] = None
    creator_profile_image: Optional[str] = None
    creator_profile_image_type: Optional[str] = None
    title: str
    content: str
    tags: list[str] = []
    
    # Event-specific fields
    event_start_time: Optional[datetime] = None
    event_end_time: Optional[datetime] = None
    event_location: Optional[str] = None
    
    # Linked items (FR-15.3, FR-15.5)
    linked_offer_id: Optional[int] = None
    linked_need_id: Optional[int] = None
    linked_item: Optional[LinkedItemInfo] = None
    
    # Moderation
    is_approved: bool
    is_visible: bool
    is_pinned: bool
    
    # Engagement
    view_count: int
    comment_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ForumTopicListResponse(BaseModel):
    """Schema for paginated forum topic list."""
    items: list[ForumTopicResponse]
    total: int
    skip: int
    limit: int


class ForumCommentCreate(BaseModel):
    """Schema for creating a forum comment."""
    content: str = Field(..., min_length=1, max_length=2000)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Basic content validation."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class ForumCommentUpdate(BaseModel):
    """Schema for updating a forum comment."""
    content: str = Field(..., min_length=1, max_length=2000)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Basic content validation."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class ForumCommentResponse(BaseModel):
    """Schema for forum comment response."""
    id: int
    topic_id: int
    author_id: int
    author_username: Optional[str] = None
    author_display_name: Optional[str] = None
    author_profile_image: Optional[str] = None
    author_profile_image_type: Optional[str] = None
    content: str
    is_approved: bool
    is_visible: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ForumCommentListResponse(BaseModel):
    """Schema for paginated forum comment list."""
    items: list[ForumCommentResponse]
    total: int
    skip: int
    limit: int


class ForumSearchParams(BaseModel):
    """Schema for forum search parameters (FR-15.2)."""
    keyword: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = Field(None, max_length=10)
    topic_type: Optional[str] = None  # Filter by 'discussion' or 'event'
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    
    @field_validator('topic_type')
    @classmethod
    def validate_topic_type(cls, v):
        """Validate topic type if provided."""
        if v is not None and v not in ['discussion', 'event']:
            raise ValueError("topic_type must be 'discussion' or 'event'")
        return v
