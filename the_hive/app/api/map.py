"""Map Feed API endpoints.

SRS Requirements:
- FR-9: Map view for discovering local offers/needs
- FR-9.1: Display offers/needs on map with approximate locations
- FR-9.2: Filter by tags
- FR-9.3: Sort by distance from user location
- NFR-7: Privacy - approximate coordinates only (rounded to ~1km)

This module provides location-based discovery with privacy protection.
Exact addresses are never stored or exposed - only approximate coordinates.
"""
import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, or_, func

from app.core.db import get_session
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.associations import OfferTag, NeedTag
from app.models.tag import Tag
from app.schemas.map import MapPinResponse, MapFeedResponse

router = APIRouter(prefix="/map", tags=["Map"])


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of point 1 (degrees)
        lon1: Longitude of point 1 (degrees)
        lat2: Latitude of point 2 (degrees)
        lon2: Longitude of point 2 (degrees)
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def approximate_coordinate(coord: float, precision: int = 2) -> float:
    """Round coordinate to approximate precision for privacy.
    
    Rounding to 2 decimal places gives ~1.1km precision:
    - At equator: 1° ≈ 111km, 0.01° ≈ 1.11km
    - At 45° latitude: 0.01° longitude ≈ 0.78km
    
    Args:
        coord: Exact coordinate (latitude or longitude)
        precision: Number of decimal places (default 2 for ~1km)
    
    Returns:
        Approximate coordinate rounded to specified precision
    
    SRS NFR-7: Privacy protection through coordinate approximation
    """
    return round(coord, precision)


@router.get("/feed", response_model=MapFeedResponse)
def get_map_feed(
    session: Annotated[Session, Depends(get_session)],
    user_lat: Optional[float] = Query(None, description="User's latitude for distance sorting"),
    user_lon: Optional[float] = Query(None, description="User's longitude for distance sorting"),
    tags: Optional[str] = Query(None, description="Comma-separated tag names to filter by"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> MapFeedResponse:
    """Get map feed with active offers/needs for location-based discovery.
    
    Returns only ACTIVE offers and needs with approximate coordinates.
    
    Privacy (SRS NFR-7):
    - Coordinates are rounded to ~1km precision
    - Exact addresses never stored or exposed
    - Only location_name (e.g., "Brooklyn, NY") shown
    
    Features (SRS FR-9):
    - Distance sorting if user location provided
    - Tag filtering
    - Includes both offers and needs
    - Remote items included (no distance)
    
    Args:
        user_lat: User's latitude for distance calculation
        user_lon: User's longitude for distance calculation  
        tags: Comma-separated tags to filter by
        skip: Pagination offset
        limit: Max results per page
    
    Returns:
        MapFeedResponse with approximate coordinates and optional distances
    """
    # Collect all map pins
    pins = []
    
    # Parse tags if provided
    tag_names = []
    if tags:
        tag_names = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Query active offers
    offer_query = select(Offer).where(Offer.status == OfferStatus.ACTIVE)
    
    # Filter by tags if specified
    if tag_names:
        # Get tag IDs
        tag_query = select(Tag.id).where(Tag.name.in_(tag_names))
        tag_ids = list(session.exec(tag_query).all())
        
        if tag_ids:
            # Filter offers that have at least one of the specified tags
            offer_query = offer_query.where(
                Offer.id.in_(
                    select(OfferTag.offer_id).where(OfferTag.tag_id.in_(tag_ids))
                )
            )
    
    offers = session.exec(offer_query).all()
    
    # Query active needs
    need_query = select(Need).where(Need.status == NeedStatus.ACTIVE)
    
    # Filter by tags if specified
    if tag_names:
        tag_query = select(Tag.id).where(Tag.name.in_(tag_names))
        tag_ids = list(session.exec(tag_query).all())
        
        if tag_ids:
            # Filter needs that have at least one of the specified tags
            need_query = need_query.where(
                Need.id.in_(
                    select(NeedTag.need_id).where(NeedTag.tag_id.in_(tag_ids))
                )
            )
    
    needs = session.exec(need_query).all()
    
    # Process offers
    for offer in offers:
        # Get tags for this offer
        offer_tags_query = (
            select(Tag.id, Tag.name)
            .join(OfferTag, OfferTag.tag_id == Tag.id)
            .where(OfferTag.offer_id == offer.id)
        )
        offer_tags = [{"id": tag_id, "name": tag_name} for tag_id, tag_name in session.exec(offer_tags_query).all()]
        
        # Calculate distance if user location provided and offer has location
        distance = None
        if (
            user_lat is not None
            and user_lon is not None
            and offer.location_lat is not None
            and offer.location_lon is not None
            and not offer.is_remote
        ):
            distance = haversine_distance(
                user_lat, user_lon, offer.location_lat, offer.location_lon
            )
        
        # Create pin with approximate coordinates
        pin = MapPinResponse(
            id=offer.id,
            type="offer",
            title=offer.title,
            description=offer.description,
            is_remote=offer.is_remote,
            approximate_lat=(
                approximate_coordinate(offer.location_lat)
                if offer.location_lat is not None
                else None
            ),
            approximate_lon=(
                approximate_coordinate(offer.location_lon)
                if offer.location_lon is not None
                else None
            ),
            location_name=offer.location_name,
            tags=offer_tags,
            capacity=offer.capacity,
            accepted_count=offer.accepted_count,
            distance_km=round(distance, 1) if distance is not None else None,
        )
        pins.append(pin)
    
    # Process needs
    for need in needs:
        # Get tags for this need
        need_tags_query = (
            select(Tag.id, Tag.name)
            .join(NeedTag, NeedTag.tag_id == Tag.id)
            .where(NeedTag.need_id == need.id)
        )
        need_tags = [{"id": tag_id, "name": tag_name} for tag_id, tag_name in session.exec(need_tags_query).all()]
        
        # Calculate distance if user location provided and need has location
        distance = None
        if (
            user_lat is not None
            and user_lon is not None
            and need.location_lat is not None
            and need.location_lon is not None
            and not need.is_remote
        ):
            distance = haversine_distance(
                user_lat, user_lon, need.location_lat, need.location_lon
            )
        
        # Create pin with approximate coordinates
        pin = MapPinResponse(
            id=need.id,
            type="need",
            title=need.title,
            description=need.description,
            is_remote=need.is_remote,
            approximate_lat=(
                approximate_coordinate(need.location_lat)
                if need.location_lat is not None
                else None
            ),
            approximate_lon=(
                approximate_coordinate(need.location_lon)
                if need.location_lon is not None
                else None
            ),
            location_name=need.location_name,
            tags=need_tags,
            capacity=need.capacity,
            accepted_count=need.accepted_count,
            distance_km=round(distance, 1) if distance is not None else None,
        )
        pins.append(pin)
    
    # Sort by distance if user location provided
    # Remote items and items without distance go to the end
    if user_lat is not None and user_lon is not None:
        pins.sort(key=lambda p: (
            p.distance_km is None,  # None values last
            p.distance_km if p.distance_km is not None else float('inf')
        ))
    
    # Apply pagination
    total = len(pins)
    pins = pins[skip:skip + limit]
    
    return MapFeedResponse(
        items=pins,
        total=total,
        skip=skip,
        limit=limit,
        user_lat=user_lat,
        user_lon=user_lon,
    )
