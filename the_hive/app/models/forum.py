from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


class TopicType(str, Enum):
    """Type of forum topic.
    
    SRS Requirements:
    - FR-15.1: Support discussions and events
    """
    DISCUSSION = "discussion"
    EVENT = "event"


class ForumTopic(SQLModel, table=True):
    """Forum topic for discussions and events.
    
    SRS Requirements:
    - FR-15: Basic forum with moderation hooks
    - FR-15.1: Create/list topics (types: discussion, event)
    - FR-15.2: Search by tag/keyword
    - FR-15.3: Link optional Offer/Need to events
    - FR-15.4: Events ordered by recency
    - FR-15.5: Links visible both ways (bidirectional)
    """

    __tablename__ = "forum_topics"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Topic type (discussion or event)
    topic_type: TopicType = Field(index=True)
    
    # Creator
    creator_id: int = Field(foreign_key="users.id", index=True)
    
    # Content
    title: str = Field(max_length=200)
    content: str = Field(max_length=5000)
    
    # Optional links to Offer/Need (for events) (FR-15.3, FR-15.5)
    linked_offer_id: Optional[int] = Field(default=None, foreign_key="offers.id", index=True)
    linked_need_id: Optional[int] = Field(default=None, foreign_key="needs.id", index=True)
    
    # Event-specific fields
    event_start_time: Optional[datetime] = Field(default=None, index=True)
    event_end_time: Optional[datetime] = Field(default=None)
    event_location: Optional[str] = Field(default=None, max_length=255)
    
    # Moderation hooks (FR-15 - basic moderation)
    is_moderated: bool = Field(default=False)
    is_approved: bool = Field(default=True)  # Auto-approved unless flagged
    moderation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Visibility
    is_visible: bool = Field(default=True, index=True)
    is_pinned: bool = Field(default=False)  # Moderators can pin important topics
    
    # Engagement tracking
    view_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    
    # Timestamps (FR-15.4 - ordered by recency)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    moderated_at: Optional[datetime] = Field(default=None)


class ForumComment(SQLModel, table=True):
    """Comment on a forum topic.
    
    SRS Requirements:
    - FR-15: Comments on forum topics
    - FR-15: Moderation hooks for comments
    """

    __tablename__ = "forum_comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Topic reference
    topic_id: int = Field(foreign_key="forum_topics.id", index=True)
    
    # Author
    author_id: int = Field(foreign_key="users.id", index=True)
    
    # Content
    content: str = Field(max_length=2000)
    
    # Moderation hooks
    is_moderated: bool = Field(default=False)
    is_approved: bool = Field(default=True)
    moderation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Soft delete (SRS FR-11.3: Moderators can remove comments)
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    
    # Visibility
    is_visible: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    moderated_at: Optional[datetime] = Field(default=None)


class ForumTopicTag(SQLModel, table=True):
    """Association table linking forum topics to tags.
    
    SRS Requirements:
    - FR-15.2: Search by tag
    - FR-8.1: Semantic tags for categorization
    """

    __tablename__ = "forum_topic_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="forum_topics.id", index=True)
    tag_id: int = Field(foreign_key="tags.id", index=True)
