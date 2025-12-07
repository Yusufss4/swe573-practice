"""
Notification model for real-time user notifications.
# SRS FR-N.1: Users receive real-time notifications for important events
# SRS FR-N.2: Notifications include participant actions, exchange completion, and ratings
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    """Notification type enumeration for different events."""
    # Handshake events
    APPLICATION_RECEIVED = "application_received"  # Someone applied to your offer/need
    APPLICATION_ACCEPTED = "application_accepted"  # Your application was accepted
    APPLICATION_DECLINED = "application_declined"  # Your application was declined
    PARTICIPANT_CANCELLED = "participant_cancelled"  # Participant cancelled
    
    # Exchange events
    EXCHANGE_AWAITING_CONFIRMATION = "exchange_awaiting_confirmation"  # Other party confirmed, waiting for you
    EXCHANGE_COMPLETED = "exchange_completed"  # Exchange marked as completed
    
    # Rating events
    RATING_RECEIVED = "rating_received"  # You received a rating


class Notification(SQLModel, table=True):
    """
    Notification model for user notifications.
    # SRS FR-N.3: Store notification details including type, user, related item, and read status
    """
    __tablename__ = "notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User who receives the notification
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Notification type
    type: NotificationType = Field(index=True)
    
    # Title for the notification
    title: str = Field(max_length=255)
    
    # Message content
    message: str = Field(max_length=500)
    
    # Related entity IDs (nullable, depends on notification type)
    related_offer_id: Optional[int] = Field(default=None, foreign_key="offers.id")
    related_need_id: Optional[int] = Field(default=None, foreign_key="needs.id")
    related_user_id: Optional[int] = Field(default=None, foreign_key="users.id")  # User who triggered the notification
    related_participant_id: Optional[int] = Field(default=None, foreign_key="participants.id")
    related_rating_id: Optional[int] = Field(default=None, foreign_key="ratings.id")
    
    # Read status
    is_read: bool = Field(default=False, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(default=None)
