"""
Schemas for Offer CRUD operations.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class OfferBase(BaseModel):
    """Base schema for Offer with common fields."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    is_remote: bool = False
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)
    capacity: int = Field(default=1, ge=1)
    
    @field_validator('location_lat', 'location_lon', 'location_name')
    @classmethod
    def validate_location(cls, v, info):
        """Validate that non-remote offers have location."""
        # This will be checked at the model level
        return v


class OfferCreate(OfferBase):
    """Schema for creating a new Offer."""
    tags: list[str] = Field(..., min_length=1, max_length=10)
    available_slots: Optional[list[str]] = None  # ISO datetime strings
    
    @field_validator('available_slots')
    @classmethod
    def validate_slots(cls, v):
        """Validate that available slots are in the future."""
        if v:
            now = datetime.utcnow()
            for slot_str in v:
                try:
                    slot = datetime.fromisoformat(slot_str.replace('Z', '+00:00'))
                    if slot < now:
                        raise ValueError(f"Slot {slot_str} is in the past")
                except ValueError as e:
                    raise ValueError(f"Invalid datetime format: {slot_str}") from e
        return v


class OfferUpdate(BaseModel):
    """Schema for updating an Offer."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    is_remote: Optional[bool] = None
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)
    capacity: Optional[int] = Field(None, ge=1)
    tags: Optional[list[str]] = Field(None, min_length=1, max_length=10)
    available_slots: Optional[list[str]] = None


class OfferExtend(BaseModel):
    """Schema for extending an Offer's end date."""
    days: int = Field(..., ge=1, le=365, description="Number of days to extend")


class OfferResponse(BaseModel):
    """Schema for Offer response."""
    id: int
    creator_id: int
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
    available_slots: Optional[list[str]] = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class OfferListResponse(BaseModel):
    """Schema for paginated Offer list."""
    items: list[OfferResponse]
    total: int
    skip: int
    limit: int
