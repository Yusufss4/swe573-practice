"""
Offer API endpoints.

SRS Requirements:
- FR-3: Offer and Need Management
- FR-12: Archiving and Transparency
"""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.core.offers_needs import (
    archive_expired_items,
    associate_tags_to_offer,
    check_and_archive_item,
    get_offer_tags,
    update_offer_tags,
)
from app.models.offer import Offer, OfferStatus
from app.models.user import User
from app.models.participant import Participant, ParticipantStatus
from app.models.need import Need
from app.models.rating import Rating
from app.schemas.offer import (
    OfferCreate,
    OfferExtend,
    OfferListResponse,
    OfferResponse,
    OfferUpdate,
)
from app.schemas.auth import UserPublic

router = APIRouter(prefix="/offers", tags=["Offers"])


def _get_creator_stats(session: Session, user_id: int) -> tuple[int, float | None]:
    """Get creator's completed exchanges and average rating."""
    # Completed exchanges
    completed_as_participant = session.exec(
        select(func.count(Participant.id)).where(
            Participant.user_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    completed_on_offers = session.exec(
        select(func.count(Participant.id))
        .select_from(Participant)
        .join(Offer, Participant.offer_id == Offer.id)
        .where(
            Offer.creator_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    completed_on_needs = session.exec(
        select(func.count(Participant.id))
        .select_from(Participant)
        .join(Need, Participant.need_id == Need.id)
        .where(
            Need.creator_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    total_completed = completed_as_participant + completed_on_offers + completed_on_needs
    
    # Average rating
    avg_rating = session.exec(
        select(func.avg(Rating.general_rating)).where(Rating.to_user_id == user_id)
    ).one()
    
    return total_completed, avg_rating


def _build_offer_response(session: Session, offer: Offer) -> OfferResponse:
    """Build an OfferResponse with tags and creator info."""
    tags = get_offer_tags(session, offer.id)
    
    # Fetch creator information
    creator = session.get(User, offer.creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creator user not found"
        )
    
    # Get creator stats
    completed_exchanges, average_rating = _get_creator_stats(session, creator.id)
    
    creator_public = UserPublic(
        id=creator.id,
        username=creator.username,
        display_name=creator.full_name,
        full_name=creator.full_name,
        profile_image=creator.profile_image,
        profile_image_type=creator.profile_image_type,
        completed_exchanges=completed_exchanges,
        average_rating=round(average_rating, 1) if average_rating else None,
    )
    
    # Parse available slots if present
    available_slots = None
    if offer.available_slots:
        import json
        try:
            available_slots = json.loads(offer.available_slots)
        except:
            available_slots = None
    
    return OfferResponse(
        id=offer.id,
        creator_id=offer.creator_id,
        creator=creator_public,
        title=offer.title,
        description=offer.description,
        is_remote=offer.is_remote,
        location_lat=offer.location_lat,
        location_lon=offer.location_lon,
        location_name=offer.location_name,
        start_date=offer.start_date,
        end_date=offer.end_date,
        capacity=offer.capacity,
        accepted_count=offer.accepted_count,
        hours=offer.hours,
        status=offer.status.value,
        available_slots=available_slots,
        tags=tags,
        created_at=offer.created_at,
        updated_at=offer.updated_at,
    )


@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer_data: OfferCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> OfferResponse:
    """
    Create a new offer.
    
    SRS FR-3.1: Users can create offers with title, description, tags, location,
    duration, remote/in-person indicator, and capacity.
    
    SRS Constraints:
    - Default 7-day duration
    - Default capacity = 1
    - Location required if not remote
    """
    # Validate location for non-remote offers
    if not offer_data.is_remote:
        if not offer_data.location_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location name is required for non-remote offers"
            )
    
    # Create offer with 7-day default duration
    now = datetime.utcnow()
    end_date = now + timedelta(days=7)
    
    new_offer = Offer(
        creator_id=current_user.id,
        title=offer_data.title,
        description=offer_data.description,
        is_remote=offer_data.is_remote,
        location_lat=offer_data.location_lat,
        location_lon=offer_data.location_lon,
        location_name=offer_data.location_name,
        capacity=offer_data.capacity,
        hours=offer_data.hours,
        start_date=now,
        end_date=end_date,
        status=OfferStatus.ACTIVE,
    )
    
    # Store available slots as JSON if provided
    if offer_data.available_slots:
        import json
        new_offer.available_slots = json.dumps([slot.model_dump() for slot in offer_data.available_slots])
    
    session.add(new_offer)
    session.commit()
    session.refresh(new_offer)
    
    # Associate tags
    associate_tags_to_offer(session, new_offer.id, offer_data.tags)
    session.commit()
    
    return _build_offer_response(session, new_offer)


@router.get("/", response_model=OfferListResponse)
def list_offers(
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str = Query("active", description="Filter by status: active, all"),
) -> OfferListResponse:
    """
    List all offers (excluding expired by default).
    
    SRS FR-12.2: Expired items shall be hidden by default.
    Simple 'archive expired on read' - archives expired items before returning list.
    """
    # Archive expired items (simple hook before listing)
    archive_expired_items(session)
    
    # Build query
    statement = select(Offer).order_by(Offer.created_at.desc())
    
    # Filter by status
    if status_filter == "active":
        statement = statement.where(Offer.status == OfferStatus.ACTIVE)
    
    # Get total count
    total_statement = select(Offer)
    if status_filter == "active":
        total_statement = total_statement.where(Offer.status == OfferStatus.ACTIVE)
    total = len(session.exec(total_statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    offers = session.exec(statement).all()
    
    # Build responses with tags
    items = [_build_offer_response(session, offer) for offer in offers]
    
    return OfferListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/my", response_model=OfferListResponse)
def list_my_offers(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_expired: bool = Query(False, description="Include expired offers"),
) -> OfferListResponse:
    """
    List current user's offers.
    
    Owners can view their own expired items.
    """
    statement = select(Offer).where(
        Offer.creator_id == current_user.id
    ).order_by(Offer.created_at.desc())
    
    # Optionally filter out expired
    if not include_expired:
        statement = statement.where(Offer.status != OfferStatus.EXPIRED)
    
    # Get total
    total_statement = select(Offer).where(Offer.creator_id == current_user.id)
    if not include_expired:
        total_statement = total_statement.where(Offer.status != OfferStatus.EXPIRED)
    total = len(session.exec(total_statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    offers = session.exec(statement).all()
    
    items = [_build_offer_response(session, offer) for offer in offers]
    
    return OfferListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(
    offer_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> OfferResponse:
    """
    Get a specific offer by ID.
    
    Checks and archives if expired (on-read hook).
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Archive if expired (on-read hook)
    check_and_archive_item(session, offer)
    session.refresh(offer)
    
    return _build_offer_response(session, offer)


@router.patch("/{offer_id}", response_model=OfferResponse)
def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> OfferResponse:
    """
    Update an offer.
    
    Only the creator can update their offer.
    Cannot update expired or completed offers.
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Check ownership
    if offer.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own offers"
        )
    
    # Check status
    if offer.status in [OfferStatus.EXPIRED, OfferStatus.COMPLETED, OfferStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update {offer.status.value} offer"
        )
    
    # Update fields
    update_data = offer_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "tags":
            update_offer_tags(session, offer_id, value)
        elif key == "available_slots" and value is not None:
            import json
            # value is already a list of dicts from model_dump()
            if value and isinstance(value[0], dict):
                offer.available_slots = json.dumps(value)
            else:
                # If it's AvailableTimeSlot objects, convert them
                offer.available_slots = json.dumps([slot.model_dump() for slot in value])
        elif key == "capacity":
            # SRS FR-3.7: Cannot decrease capacity below accepted count
            if value < offer.accepted_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot decrease capacity below accepted count ({offer.accepted_count})"
                )
            setattr(offer, key, value)
        else:
            setattr(offer, key, value)
    
    offer.updated_at = datetime.utcnow()
    
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    return _build_offer_response(session, offer)


@router.post("/{offer_id}/extend", response_model=OfferResponse)
def extend_offer(
    offer_id: int,
    extend_data: OfferExtend,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> OfferResponse:
    """
    Extend an offer's end date.
    
    SRS FR-3.2: Users can renew or extend offers but not shorten expiration date.
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Check ownership
    if offer.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only extend your own offers"
        )
    
    # Extend end date (can extend even if expired to "renew")
    new_end_date = offer.end_date + timedelta(days=extend_data.days)
    offer.end_date = new_end_date
    
    # If expired, reactivate
    if offer.status == OfferStatus.EXPIRED:
        offer.status = OfferStatus.ACTIVE
    
    offer.updated_at = datetime.utcnow()
    
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    return _build_offer_response(session, offer)


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(
    offer_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Delete (cancel) an offer.
    
    Only the creator can delete their offer.
    Sets status to CANCELLED rather than hard delete.
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Check ownership
    if offer.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own offers"
        )
    
    # Soft delete by setting status to cancelled
    offer.status = OfferStatus.CANCELLED
    offer.updated_at = datetime.utcnow()
    
    session.add(offer)
    session.commit()
    
    return None
