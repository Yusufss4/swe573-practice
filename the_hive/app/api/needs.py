"""
Need API endpoints.

SRS Requirements:
- FR-3: Offer and Need Management
- FR-12: Archiving and Transparency
"""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.core.offers_needs import (
    archive_expired_items,
    associate_tags_to_need,
    check_and_archive_item,
    get_need_tags,
    update_need_tags,
)
from app.models.need import Need, NeedStatus
from app.models.user import User
from app.schemas.need import (
    NeedCreate,
    NeedExtend,
    NeedListResponse,
    NeedResponse,
    NeedUpdate,
)
from app.schemas.auth import UserPublic

router = APIRouter(prefix="/needs", tags=["Needs"])


def _build_need_response(session: Session, need: Need) -> NeedResponse:
    """Build a NeedResponse with tags and creator info."""
    tags = get_need_tags(session, need.id)
    
    # Fetch creator information
    creator = session.get(User, need.creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creator user not found"
        )
    
    creator_public = UserPublic(
        id=creator.id,
        username=creator.username,
        display_name=creator.full_name,
        full_name=creator.full_name,
        profile_image=creator.profile_image,
        profile_image_type=creator.profile_image_type,
    )
    
    # Parse available slots if present
    available_slots = None
    if need.available_slots:
        import json
        try:
            available_slots = json.loads(need.available_slots)
        except:
            available_slots = None
    
    return NeedResponse(
        id=need.id,
        creator_id=need.creator_id,
        creator=creator_public,
        title=need.title,
        description=need.description,
        is_remote=need.is_remote,
        location_lat=need.location_lat,
        location_lon=need.location_lon,
        location_name=need.location_name,
        start_date=need.start_date,
        end_date=need.end_date,
        capacity=need.capacity,
        accepted_count=need.accepted_count,
        hours=need.hours,
        status=need.status.value,
        available_slots=available_slots,
        tags=tags,
        created_at=need.created_at,
        updated_at=need.updated_at,
    )


@router.post("/", response_model=NeedResponse, status_code=status.HTTP_201_CREATED)
def create_need(
    need_data: NeedCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> NeedResponse:
    """
    Create a new need.
    
    SRS FR-3.1: Users can create needs with title, description, tags, location,
    duration, remote/in-person indicator, and capacity.
    
    SRS Constraints:
    - Default 7-day duration
    - Default capacity = 1
    - Location required if not remote
    """
    # Validate location for non-remote needs
    if not need_data.is_remote:
        if not need_data.location_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location name is required for non-remote needs"
            )
    
    # Create need with 7-day default duration
    now = datetime.utcnow()
    end_date = now + timedelta(days=7)
    
    new_need = Need(
        creator_id=current_user.id,
        title=need_data.title,
        description=need_data.description,
        is_remote=need_data.is_remote,
        location_lat=need_data.location_lat,
        location_lon=need_data.location_lon,
        location_name=need_data.location_name,
        capacity=need_data.capacity,
        start_date=now,
        end_date=end_date,
        status=NeedStatus.ACTIVE,
    )
    
    # Store available slots as JSON if provided
    if need_data.available_slots:
        import json
        new_need.available_slots = json.dumps([slot.model_dump() for slot in need_data.available_slots])
    
    session.add(new_need)
    session.commit()
    session.refresh(new_need)
    
    # Associate tags
    associate_tags_to_need(session, new_need.id, need_data.tags)
    session.commit()
    
    return _build_need_response(session, new_need)


@router.get("/", response_model=NeedListResponse)
def list_needs(
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str = Query("active", description="Filter by status: active, all"),
) -> NeedListResponse:
    """
    List all needs (excluding expired by default).
    
    SRS FR-12.2: Expired items shall be hidden by default.
    Simple 'archive expired on read' - archives expired items before returning list.
    """
    # Archive expired items (simple hook before listing)
    archive_expired_items(session)
    
    # Build query
    statement = select(Need).order_by(Need.created_at.desc())
    
    # Filter by status
    if status_filter == "active":
        statement = statement.where(Need.status == NeedStatus.ACTIVE)
    
    # Get total count
    total_statement = select(Need)
    if status_filter == "active":
        total_statement = total_statement.where(Need.status == NeedStatus.ACTIVE)
    total = len(session.exec(total_statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    needs = session.exec(statement).all()
    
    # Build responses with tags
    items = [_build_need_response(session, need) for need in needs]
    
    return NeedListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/my", response_model=NeedListResponse)
def list_my_needs(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_expired: bool = Query(False, description="Include expired needs"),
) -> NeedListResponse:
    """
    List current user's needs.
    
    Owners can view their own expired items.
    """
    statement = select(Need).where(
        Need.creator_id == current_user.id
    ).order_by(Need.created_at.desc())
    
    # Optionally filter out expired
    if not include_expired:
        statement = statement.where(Need.status != NeedStatus.EXPIRED)
    
    # Get total
    total_statement = select(Need).where(Need.creator_id == current_user.id)
    if not include_expired:
        total_statement = total_statement.where(Need.status != NeedStatus.EXPIRED)
    total = len(session.exec(total_statement).all())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    needs = session.exec(statement).all()
    
    items = [_build_need_response(session, need) for need in needs]
    
    return NeedListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{need_id}", response_model=NeedResponse)
def get_need(
    need_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> NeedResponse:
    """
    Get a specific need by ID.
    
    Checks and archives if expired (on-read hook).
    """
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Archive if expired (on-read hook)
    check_and_archive_item(session, need)
    session.refresh(need)
    
    return _build_need_response(session, need)


@router.patch("/{need_id}", response_model=NeedResponse)
def update_need(
    need_id: int,
    need_data: NeedUpdate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> NeedResponse:
    """
    Update a need.
    
    Only the creator can update their need.
    Cannot update expired or completed needs.
    """
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Check ownership
    if need.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own needs"
        )
    
    # Check status
    if need.status in [NeedStatus.EXPIRED, NeedStatus.COMPLETED, NeedStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update {need.status.value} need"
        )
    
    # Update fields
    update_data = need_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "tags":
            update_need_tags(session, need_id, value)
        elif key == "available_slots" and value is not None:
            import json
            # value is already a list of dicts from model_dump()
            if value and isinstance(value[0], dict):
                need.available_slots = json.dumps(value)
            else:
                # If it's AvailableTimeSlot objects, convert them
                need.available_slots = json.dumps([slot.model_dump() for slot in value])
        elif key == "capacity":
            # SRS FR-3.7: Cannot decrease capacity below accepted count
            if value < need.accepted_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot decrease capacity below accepted count ({need.accepted_count})"
                )
            setattr(need, key, value)
        else:
            setattr(need, key, value)
    
    need.updated_at = datetime.utcnow()
    
    session.add(need)
    session.commit()
    session.refresh(need)
    
    return _build_need_response(session, need)


@router.post("/{need_id}/extend", response_model=NeedResponse)
def extend_need(
    need_id: int,
    extend_data: NeedExtend,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> NeedResponse:
    """
    Extend a need's end date.
    
    SRS FR-3.2: Users can renew or extend needs but not shorten expiration date.
    """
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Check ownership
    if need.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only extend your own needs"
        )
    
    # Extend end date (can extend even if expired to "renew")
    new_end_date = need.end_date + timedelta(days=extend_data.days)
    need.end_date = new_end_date
    
    # If expired, reactivate
    if need.status == NeedStatus.EXPIRED:
        need.status = NeedStatus.ACTIVE
    
    need.updated_at = datetime.utcnow()
    
    session.add(need)
    session.commit()
    session.refresh(need)
    
    return _build_need_response(session, need)


@router.delete("/{need_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_need(
    need_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Delete (cancel) a need.
    
    Only the creator can delete their need.
    Sets status to CANCELLED rather than hard delete.
    """
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Need not found"
        )
    
    # Check ownership
    if need.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own needs"
        )
    
    # Soft delete by setting status to cancelled
    need.status = NeedStatus.CANCELLED
    need.updated_at = datetime.utcnow()
    
    session.add(need)
    session.commit()
    
    return None
