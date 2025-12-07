from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel


class NeedStatus(str, Enum):
    """Status enumeration for Needs."""
    ACTIVE = "active"
    FULL = "full"  # Capacity reached
    EXPIRED = "expired"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Need(SQLModel, table=True):
    """Need model representing service requests from users.
    
    SRS Requirements:
    - FR-3.1: Title, description, tags, location, duration, remote/in-person, capacity
    - FR-3.2: Can renew/extend, not shorten
    - FR-3.3: Auto-archive after expiration
    - FR-3.6: Track accepted participants vs capacity
    - FR-4.1: Available time slots for scheduling
    - SRS Constraints: 7-day default validity, capacity default 1
    """

    __tablename__ = "needs"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Owner reference
    creator_id: int = Field(foreign_key="users.id", index=True)
    
    # Core content fields (FR-3.1)
    title: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    
    # Location fields (SRS: approximate only, NFR-7)
    is_remote: bool = Field(default=False)
    location_lat: Optional[float] = Field(default=None)
    location_lon: Optional[float] = Field(default=None)
    location_name: Optional[str] = Field(default=None, max_length=255)
    
    # Temporal fields (SRS: 7-day default)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=7)
    )
    
    # Capacity tracking (SRS: default 1, FR-3.6)
    capacity: int = Field(default=1, ge=1)  # Minimum 1
    accepted_count: int = Field(default=0)
    
    # TimeBank hours (SRS: FR-7.2 - hours for this exchange)
    hours: float = Field(default=1.0, gt=0, description="TimeBank hours for this need")
    
    # Status
    status: NeedStatus = Field(default=NeedStatus.ACTIVE, index=True)
    
    # Availability calendar data (FR-4.1)
    # Stored as JSON array of time slot objects
    available_slots: Optional[str] = Field(default=None)  # JSON string
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = Field(default=None)  # SRS FR-11.3: Track moderation removal
