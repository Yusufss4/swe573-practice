from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


class ReportReason(str, Enum):
    """Predefined reasons for reporting content.
    
    SRS Requirements:
    - FR-11.1: Users can report inappropriate content or behavior
    """
    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE = "inappropriate"
    SCAM = "scam"
    MISINFORMATION = "misinformation"
    OTHER = "other"


class ReportStatus(str, Enum):
    """Status of report resolution.
    
    SRS Requirements:
    - FR-11.2: Moderators review and take action
    - FR-11.4: Reports and resolutions logged
    """
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportAction(str, Enum):
    """Actions taken by moderators."""
    NONE = "none"
    WARNING = "warning"
    CONTENT_REMOVED = "content_removed"
    USER_SUSPENDED = "user_suspended"
    USER_BANNED = "user_banned"


class Report(SQLModel, table=True):
    """Report of inappropriate content or behavior.
    
    SRS Requirements:
    - FR-11: Reporting and moderation system
    - FR-11.4: Reports and resolutions logged for transparency
    - NFR-8: Admin and moderator actions logged for audit
    - Database schema requirement (§3.5.1): reason, status, moderator action
    """

    __tablename__ = "reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Reporter
    reporter_id: int = Field(foreign_key="users.id", index=True)
    
    # Reported item references (one will be set)
    reported_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    reported_offer_id: Optional[int] = Field(default=None, foreign_key="offers.id")
    reported_need_id: Optional[int] = Field(default=None, foreign_key="needs.id")
    reported_comment_id: Optional[int] = Field(default=None, foreign_key="forum_comments.id")
    reported_forum_topic_id: Optional[int] = Field(default=None, foreign_key="forum_topics.id")
    reported_rating_id: Optional[int] = Field(default=None, foreign_key="ratings.id")
    
    # Report details
    reason: ReportReason = Field(index=True)
    description: str = Field(max_length=1000)
    
    # Status tracking
    status: ReportStatus = Field(default=ReportStatus.PENDING, index=True)
    
    # Moderator handling
    moderator_id: Optional[int] = Field(default=None, foreign_key="users.id")
    moderator_action: ReportAction = Field(default=ReportAction.NONE)
    moderator_notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps (FR-11.4, NFR-8)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    reviewed_at: Optional[datetime] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
