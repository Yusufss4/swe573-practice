"""
Notification schemas for API requests and responses.
# SRS FR-N.1: Define notification data transfer objects
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Response model for notification data."""
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    
    # Related entities
    related_offer_id: Optional[int] = None
    related_need_id: Optional[int] = None
    related_user_id: Optional[int] = None
    related_participant_id: Optional[int] = None
    related_rating_id: Optional[int] = None
    
    # Read status
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    """Response model for list of notifications with pagination."""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class MarkAsReadRequest(BaseModel):
    """Request to mark notification as read."""
    pass  # No body needed, ID comes from URL
