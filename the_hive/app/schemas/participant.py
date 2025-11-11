"""
Schemas for Participant operations.

SRS Requirements:
- FR-5: Handshake mechanism
- FR-5.1: Offer help with optional message
- FR-5.5: Accept multiple participants up to capacity
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.auth import UserPublic


class ParticipantCreate(BaseModel):
    """Schema for creating a new participant (offering help)."""
    message: Optional[str] = Field(None, max_length=500, description="Optional message when offering help")
    selected_slot: Optional[datetime] = Field(None, description="Preferred time slot")


class ParticipantAccept(BaseModel):
    """Schema for accepting a participant."""
    participant_id: int = Field(..., description="ID of the participant to accept")
    hours: float = Field(..., gt=0, description="Hours for this exchange")


class ParticipantResponse(BaseModel):
    """Schema for Participant response."""
    id: int
    offer_id: Optional[int]
    need_id: Optional[int]
    user_id: int
    user: UserPublic
    role: str
    status: str
    hours_contributed: float
    message: Optional[str]
    selected_slot: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ParticipantListResponse(BaseModel):
    """Schema for paginated Participant list."""
    items: list[ParticipantResponse]
    total: int
    skip: int
    limit: int
