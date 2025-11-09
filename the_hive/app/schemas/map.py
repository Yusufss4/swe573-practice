"""Schemas for Map Feed API.

SRS Requirements:
- FR-9: Map view for discovering offers/needs
- NFR-7: Privacy - approximate coordinates only (never exact addresses)

This module provides DTOs for map pins with privacy-preserving location data.
Coordinates are rounded to ~1km precision to protect user privacy.
"""
from typing import Optional

from pydantic import BaseModel, Field


class MapPinResponse(BaseModel):
    """Schema for a map pin (minimal data for display).
    
    Privacy: Coordinates are approximate (rounded to ~1km).
    SRS FR-9: Map view with location-based discovery.
    SRS NFR-7: No exact addresses exposed.
    """
    id: int
    type: str = Field(..., description="'offer' or 'need'")
    title: str
    is_remote: bool
    approximate_lat: Optional[float] = Field(
        None,
        description="Approximate latitude (rounded to ~1km for privacy)"
    )
    approximate_lon: Optional[float] = Field(
        None,
        description="Approximate longitude (rounded to ~1km for privacy)"
    )
    location_name: Optional[str] = Field(
        None,
        description="Approximate location name (e.g., 'Brooklyn, NY')"
    )
    tags: list[str] = Field(default_factory=list, description="Associated tags")
    distance_km: Optional[float] = Field(
        None,
        description="Distance from user location in kilometers (if user location provided)"
    )
    
    model_config = {"from_attributes": True}


class MapFeedResponse(BaseModel):
    """Schema for paginated map feed."""
    items: list[MapPinResponse]
    total: int
    skip: int
    limit: int
    user_lat: Optional[float] = Field(
        None,
        description="User's latitude used for distance sorting"
    )
    user_lon: Optional[float] = Field(
        None,
        description="User's longitude used for distance sorting"
    )
