"""
Schemas for Need CRUD operations.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.time_slot import AvailableTimeSlot
from app.schemas.auth import UserPublic


class NeedBase(BaseModel):
    """Base schema for Need with common fields."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    is_remote: bool = False
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)
    capacity: int = Field(default=1, ge=1)


class NeedCreate(NeedBase):
    """Schema for creating a new Need."""
    tags: list[str] = Field(..., min_length=1, max_length=10)
    available_slots: Optional[list[AvailableTimeSlot]] = Field(
        None,
        description="Available time slots grouped by date"
    )


class NeedUpdate(BaseModel):
    """Schema for updating a Need."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    is_remote: Optional[bool] = None
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)
    capacity: Optional[int] = Field(None, ge=1)
    tags: Optional[list[str]] = Field(None, min_length=1, max_length=10)
    available_slots: Optional[list[AvailableTimeSlot]] = Field(
        None,
        description="Available time slots grouped by date"
    )


class NeedExtend(BaseModel):
    """Schema for extending a Need's end date."""
    days: int = Field(..., ge=1, le=365, description="Number of days to extend")


class NeedResponse(BaseModel):
    """Schema for Need response."""
    id: int
    creator_id: int
    creator: UserPublic
    title: str
    description: str
    is_remote: bool
    location_lat: Optional[float]
    location_lon: Optional[float]
    location_name: Optional[str]
    start_date: datetime
    end_date: datetime
    capacity: int
    accepted_count: int
    status: str
    available_slots: Optional[list[AvailableTimeSlot]] = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class NeedListResponse(BaseModel):
    """Schema for paginated Need list."""
    items: list[NeedResponse]
    total: int
    skip: int
    limit: int
