"""Schemas for Active Items Dashboard API.

SRS Requirements:
- FR-14: Active Items Dashboard
- FR-14.1: Display user's active offers
- FR-14.2: Display user's active needs
- FR-14.3: Display applications submitted (pending/accepted)
- FR-14.4: Display accepted participations (user is participant)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ActiveOfferResponse(BaseModel):
    """Schema for active offer in dashboard.
    
    Excludes expired/completed offers per FR-14.
    """
    id: int
    title: str
    description: str
    status: str
    capacity: int
    accepted_count: int
    is_remote: bool
    location_name: Optional[str]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ActiveNeedResponse(BaseModel):
    """Schema for active need in dashboard.
    
    Excludes expired/completed needs per FR-14.
    """
    id: int
    title: str
    description: str
    status: str
    capacity: int
    accepted_count: int
    is_remote: bool
    location_name: Optional[str]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ApplicationResponse(BaseModel):
    """Schema for application submitted by user.
    
    Shows where user has applied to help (participant records).
    Includes pending and accepted statuses per FR-14.3.
    """
    id: int  # Participant ID
    offer_id: Optional[int]
    need_id: Optional[int]
    item_title: str  # Title of the offer/need applied to
    item_type: str  # "offer" or "need"
    item_creator_id: int  # Creator of the offer/need
    status: str  # Participant status (pending/accepted)
    role: str  # Participant role (provider/requester)
    hours_contributed: float
    message: Optional[str]
    selected_slot: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ParticipationResponse(BaseModel):
    """Schema for accepted participation (user is participant).
    
    Shows active exchanges where user is accepted as participant.
    Excludes completed participations per FR-14.4.
    """
    id: int  # Participant ID
    offer_id: Optional[int]
    need_id: Optional[int]
    item_title: str  # Title of the offer/need
    item_type: str  # "offer" or "need"
    item_creator_id: int  # Creator of the offer/need
    status: str  # Participant status (accepted)
    role: str  # Participant role (provider/requester)
    hours_contributed: float
    message: Optional[str]
    selected_slot: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ActiveOffersListResponse(BaseModel):
    """Schema for paginated active offers list."""
    items: list[ActiveOfferResponse]
    total: int
    skip: int
    limit: int


class ActiveNeedsListResponse(BaseModel):
    """Schema for paginated active needs list."""
    items: list[ActiveNeedResponse]
    total: int
    skip: int
    limit: int


class ApplicationsListResponse(BaseModel):
    """Schema for paginated applications list."""
    items: list[ApplicationResponse]
    total: int
    skip: int
    limit: int


class ParticipationsListResponse(BaseModel):
    """Schema for paginated participations list."""
    items: list[ParticipationResponse]
    total: int
    skip: int
    limit: int


class DashboardStatsResponse(BaseModel):
    """Schema for platform-wide statistics (FR-11.5).
    
    Used by moderator dashboard to show overview metrics:
    - Service exchange counts
    - Activity levels
    - Hours exchanged
    """
    total_offers: int
    total_needs: int
    active_offers: int
    active_needs: int
    completed_exchanges: int
    total_hours_exchanged: float
    active_users: int
