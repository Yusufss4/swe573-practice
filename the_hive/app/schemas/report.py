"""
Report schemas for content moderation.

SRS Requirements:
- FR-11: Reporting and moderation system
- FR-11.1: Users can report inappropriate content
- FR-11.2: Moderators review and take action
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.report import ReportReason, ReportStatus, ReportAction


class ReportCreate(BaseModel):
    """Schema for creating a new report."""
    
    # What is being reported (one must be provided)
    reported_user_id: Optional[int] = None
    reported_offer_id: Optional[int] = None
    reported_need_id: Optional[int] = None
    reported_comment_id: Optional[int] = None
    reported_forum_topic_id: Optional[int] = None
    
    reason: ReportReason
    description: str = Field(min_length=10, max_length=1000)


class ReportUpdate(BaseModel):
    """Schema for moderator to update report status."""
    
    status: ReportStatus
    moderator_action: ReportAction
    moderator_notes: Optional[str] = Field(None, max_length=1000)


class ReportedItemDetails(BaseModel):
    """Details about the reported item."""
    
    type: str  # "user", "offer", "need", "comment", "forum_topic"
    id: int
    title: Optional[str] = None  # For offers/needs/forum_topics
    content: Optional[str] = None  # For comments/descriptions
    creator_username: Optional[str] = None


class ReporterInfo(BaseModel):
    """Information about the person who made the report."""
    
    id: int
    username: str
    full_name: Optional[str] = None


class ModeratorInfo(BaseModel):
    """Information about the moderator who handled the report."""
    
    id: int
    username: str
    full_name: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for report response with full details."""
    
    id: int
    
    # Reporter info
    reporter: ReporterInfo
    
    # Reported item
    reported_item: ReportedItemDetails
    
    # Report details
    reason: ReportReason
    description: str
    
    # Status
    status: ReportStatus
    
    # Moderator handling (if reviewed)
    moderator: Optional[ModeratorInfo] = None
    moderator_action: ReportAction
    moderator_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class ReportListResponse(BaseModel):
    """Paginated list of reports."""
    
    reports: list[ReportResponse]
    total: int
    pending_count: int
    under_review_count: int
    resolved_count: int
    page: int
    page_size: int


class ReportStatsResponse(BaseModel):
    """Statistics for moderator dashboard."""
    
    total_reports: int
    pending: int
    under_review: int
    resolved: int
    dismissed: int
    
    # By report type
    user_reports: int
    offer_reports: int
    need_reports: int
    comment_reports: int
    forum_topic_reports: int
    
    # By reason
    spam_reports: int
    harassment_reports: int
    inappropriate_reports: int
    scam_reports: int
    misinformation_reports: int
    other_reports: int
