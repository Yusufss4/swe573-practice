"""
API endpoints for user profiles.

SRS Requirements:
- FR-2: Profile Management
- FR-2.4: Profile includes description, skills, location
- FR-10.3: Ratings visible on profiles
"""
from typing import Annotated, Optional
from datetime import datetime
import base64
import re

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlmodel import Session, select, func, or_

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.user import User, UserTag, PRESET_AVATARS
from app.models.ledger import LedgerEntry
from app.models.rating import Rating
from app.schemas.auth import UserPublic, UserProfileUpdate
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

# Maximum image size: 2MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]


class UserStats(BaseModel):
    """User statistics for profile display."""
    balance: float
    hours_given: float
    hours_received: float
    completed_exchanges: int
    ratings_received: int


class UserProfileResponse(BaseModel):
    """Complete user profile with stats."""
    id: int
    username: str
    display_name: Optional[str]
    description: Optional[str]
    profile_image: Optional[str]
    profile_image_type: str
    location_name: Optional[str]
    balance: float
    social_blog: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    stats: UserStats
    tags: list[str]
    created_at: str
    
    model_config = {"from_attributes": True}


class PresetAvatarsResponse(BaseModel):
    """List of available preset avatars."""
    avatars: list[str]


@router.get("/avatars/presets", response_model=PresetAvatarsResponse)
def get_preset_avatars() -> PresetAvatarsResponse:
    """
    Get list of available preset avatar options.
    
    Returns:
        List of preset avatar names
    """
    return PresetAvatarsResponse(avatars=PRESET_AVATARS)


def _get_user_tags(session: Session, user_id: int) -> list[str]:
    """Get tag names for a user."""
    statement = select(UserTag).where(UserTag.user_id == user_id)
    user_tags = session.exec(statement).all()
    return [ut.tag_name for ut in user_tags]


def _get_user_stats(session: Session, user_id: int, balance: float) -> UserStats:
    """Calculate user stats from database."""
    from app.models.participant import Participant, ParticipantStatus
    from app.models.offer import Offer
    from app.models.need import Need
    
    # Hours given (debit entries)
    debit_sum = session.exec(
        select(func.sum(LedgerEntry.debit)).where(LedgerEntry.user_id == user_id)
    ).one() or 0.0
    
    # Hours received (credit entries)
    credit_sum = session.exec(
        select(func.sum(LedgerEntry.credit)).where(LedgerEntry.user_id == user_id)
    ).one() or 0.0
    
    # Completed exchanges - count both as participant and as creator
    # 1. Count where user is a participant
    completed_as_participant = session.exec(
        select(func.count(Participant.id)).where(
            Participant.user_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    # 2. Count completed participants on user's offers
    completed_on_offers = session.exec(
        select(func.count(Participant.id))
        .select_from(Participant)
        .join(Offer, Participant.offer_id == Offer.id)
        .where(
            Offer.creator_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    # 3. Count completed participants on user's needs
    completed_on_needs = session.exec(
        select(func.count(Participant.id))
        .select_from(Participant)
        .join(Need, Participant.need_id == Need.id)
        .where(
            Need.creator_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    completed_count = completed_as_participant + completed_on_offers + completed_on_needs
    
    # Ratings received count
    ratings_count = session.exec(
        select(func.count(Rating.id)).where(
            Rating.to_user_id == user_id
        )
    ).one() or 0
    
    return UserStats(
        balance=balance,
        hours_given=debit_sum,
        hours_received=credit_sum,
        completed_exchanges=completed_count,
        ratings_received=ratings_count
    )


def _build_profile_response(session: Session, user: User) -> UserProfileResponse:
    """Build a complete user profile response."""
    stats = _get_user_stats(session, user.id, user.balance)
    tags = _get_user_tags(session, user.id)
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.full_name,
        description=user.description,
        profile_image=user.profile_image,
        profile_image_type=user.profile_image_type or "preset",
        location_name=user.location_name,
        balance=user.balance,
        social_blog=user.social_blog,
        social_instagram=user.social_instagram,
        social_facebook=user.social_facebook,
        social_twitter=user.social_twitter,
        stats=stats,
        tags=tags,
        created_at=user.created_at.isoformat()
    )


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> UserProfileResponse:
    """
    Get current user's profile.
    
    SRS FR-2: Profile Management
    
    Returns:
        Current user's profile with stats
    """
    return _build_profile_response(session, current_user)


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> UserProfileResponse:
    """
    Update current user's profile.
    
    SRS FR-2.4: Profile includes description, skills, location
    
    Allows updating:
    - full_name
    - description (About section)
    - profile_image and profile_image_type
    - location fields
    - tags
    
    Returns:
        Updated user profile
    """
    # Update basic fields if provided
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    
    if profile_update.description is not None:
        current_user.description = profile_update.description
    
    if profile_update.profile_image is not None:
        current_user.profile_image = profile_update.profile_image
    
    if profile_update.profile_image_type is not None:
        # Validate preset avatar name if type is preset
        if profile_update.profile_image_type == "preset" and profile_update.profile_image:
            if profile_update.profile_image not in PRESET_AVATARS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid preset avatar. Must be one of: {', '.join(PRESET_AVATARS)}"
                )
        current_user.profile_image_type = profile_update.profile_image_type
    
    if profile_update.location_lat is not None:
        current_user.location_lat = profile_update.location_lat
    
    if profile_update.location_lon is not None:
        current_user.location_lon = profile_update.location_lon
    
    if profile_update.location_name is not None:
        current_user.location_name = profile_update.location_name
    
    # Update social media fields if provided
    if profile_update.social_blog is not None:
        current_user.social_blog = profile_update.social_blog
    
    if profile_update.social_instagram is not None:
        current_user.social_instagram = profile_update.social_instagram
    
    if profile_update.social_facebook is not None:
        current_user.social_facebook = profile_update.social_facebook
    
    if profile_update.social_twitter is not None:
        current_user.social_twitter = profile_update.social_twitter
    
    # Update tags if provided
    if profile_update.tags is not None:
        # Delete existing tags
        existing_tags = session.exec(
            select(UserTag).where(UserTag.user_id == current_user.id)
        ).all()
        for tag in existing_tags:
            session.delete(tag)
        
        # Add new tags (limit to 10 tags)
        unique_tags = list(set(tag.strip().lower() for tag in profile_update.tags if tag.strip()))[:10]
        for tag_name in unique_tags:
            user_tag = UserTag(user_id=current_user.id, tag_name=tag_name)
            session.add(user_tag)
    
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return _build_profile_response(session, current_user)


class ImageUploadResponse(BaseModel):
    """Response for image upload."""
    profile_image: str
    profile_image_type: str
    message: str


@router.post("/me/avatar", response_model=ImageUploadResponse)
async def upload_profile_image(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    file: UploadFile = File(...),
) -> ImageUploadResponse:
    """
    Upload a custom profile image.
    
    Accepts JPEG, PNG, GIF, or WebP images up to 500KB.
    The image is stored as a base64 data URL.
    
    Returns:
        Updated profile image info
    """
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large. Maximum size is {MAX_IMAGE_SIZE // 1024}KB"
        )
    
    # Convert to base64 data URL
    base64_content = base64.b64encode(content).decode('utf-8')
    data_url = f"data:{file.content_type};base64,{base64_content}"
    
    # Update user profile
    current_user.profile_image = data_url
    current_user.profile_image_type = "custom"
    current_user.updated_at = datetime.utcnow()
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return ImageUploadResponse(
        profile_image=data_url,
        profile_image_type="custom",
        message="Profile image uploaded successfully"
    )


@router.delete("/me/avatar")
def remove_profile_image(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> dict:
    """
    Remove custom profile image and reset to default.
    
    Returns:
        Success message
    """
    current_user.profile_image = None
    current_user.profile_image_type = "preset"
    current_user.updated_at = datetime.utcnow()
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Profile image removed successfully"}


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> UserProfileResponse:
    """
    Get public user profile with stats.
    
    SRS FR-2: Profile Management
    SRS FR-10.3: Profile displays user info and badges
    
    Returns:
        User profile with TimeBank stats and badges
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return _build_profile_response(session, user)


@router.get("/username/{username}", response_model=UserProfileResponse)
def get_user_profile_by_username(
    username: str,
    session: Annotated[Session, Depends(get_session)],
) -> UserProfileResponse:
    """
    Get public user profile by username with stats.
    
    SRS FR-2: Profile Management
    
    Returns:
        User profile with TimeBank stats and badges
    """
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return _build_profile_response(session, user)


class CompletedExchangeResponse(BaseModel):
    """Schema for a completed exchange."""
    id: int  # Participant ID (0 if no participants yet)
    offer_id: Optional[int]
    need_id: Optional[int]
    item_title: str
    item_description: str
    item_type: str  # "offer" or "need"
    other_user_id: Optional[int]  # The other party in the exchange (None if no participants yet)
    other_username: str
    role: str  # provider or requester or creator
    hours: float
    completed_at: str
    is_remote: bool
    location_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CompletedExchangesListResponse(BaseModel):
    """Schema for paginated completed exchanges list."""
    items: list[CompletedExchangeResponse]
    total: int
    skip: int
    limit: int


@router.get("/username/{username}/completed-exchanges", response_model=CompletedExchangesListResponse)
def get_user_completed_exchanges(
    username: str,
    session: Annotated[Session, Depends(get_session)],
    status_filter: str = Query("completed", description="Filter by status: accepted, completed, all"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> CompletedExchangesListResponse:
    """
    Get exchanges for a user by username.
    
    SRS FR-10: View exchanges on profile
    
    Returns exchanges where user was either:
    1. A participant (applied to someone's offer/need)
    2. The creator of an offer/need that was accepted/completed
    
    Args:
        status_filter: Filter by participant status (accepted=active, completed, all)
    
    Returns:
        List of exchanges with details
    """
    from app.models.participant import Participant, ParticipantStatus
    from app.models.offer import Offer
    from app.models.need import Need
    
    # Get user by username
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build query based on status filter
    if status_filter == "accepted":
        status_condition = Participant.status == ParticipantStatus.ACCEPTED
    elif status_filter == "completed":
        status_condition = Participant.status == ParticipantStatus.COMPLETED
    else:  # all
        status_condition = (Participant.status == ParticipantStatus.ACCEPTED) | (Participant.status == ParticipantStatus.COMPLETED)
    
    # Get filtered participants
    all_participants = session.exec(
        select(Participant).where(status_condition)
    ).all()
    
    # Build response with enriched details
    exchanges = []
    seen_participant_ids = set()  # Avoid duplicates
    seen_item_ids = set()  # Track items already added (to avoid duplicates from own active items)
    
    for participant in all_participants:
        if participant.offer_id:
            offer = session.get(Offer, participant.offer_id)
            if offer:
                # Check if user is either the participant or the offer creator
                is_participant = participant.user_id == user.id
                is_creator = offer.creator_id == user.id
                
                if is_participant or is_creator:
                    if participant.id in seen_participant_ids:
                        continue
                    seen_participant_ids.add(participant.id)
                    
                    # For accepted status (active exchanges), if user is creator, only add once per item
                    item_key = ("offer", participant.offer_id)
                    if status_filter == "accepted" and is_creator:
                        if item_key in seen_item_ids:
                            continue  # Skip duplicate - already added this offer
                        seen_item_ids.add(item_key)
                        # For creator with active exchanges, show "Waiting for participants"
                        exchanges.append(CompletedExchangeResponse(
                            id=0,  # Not tied to specific participant
                            offer_id=participant.offer_id,
                            need_id=None,
                            item_title=offer.title,
                            item_description=offer.description,
                            item_type="offer",
                            other_user_id=None,
                            other_username="Waiting for participants",
                            role="creator",
                            hours=offer.hours,
                            completed_at=offer.created_at.isoformat(),
                            is_remote=offer.is_remote,
                            location_name=offer.location_name,
                        ))
                        continue
                    
                    # For completed or if user is participant, show normally
                    # Determine the "other party" from user's perspective
                    if is_participant:
                        other_user = session.get(User, offer.creator_id)
                        other_user_id = offer.creator_id
                        role = participant.role.value
                    else:  # is_creator
                        other_user = session.get(User, participant.user_id)
                        other_user_id = participant.user_id
                        # If participant was provider, creator was requester and vice versa
                        role = "requester" if participant.role.value == "provider" else "provider"
                    
                    exchanges.append(CompletedExchangeResponse(
                        id=participant.id,
                        offer_id=participant.offer_id,
                        need_id=None,
                        item_title=offer.title,
                        item_description=offer.description,
                        item_type="offer",
                        other_user_id=other_user_id,
                        other_username=other_user.username if other_user else "Unknown",
                        role=role,
                        hours=participant.hours_contributed,
                        completed_at=participant.updated_at.isoformat(),
                        is_remote=offer.is_remote,
                        location_name=offer.location_name,
                    ))
                    
                    # Track this item to avoid duplicates when adding own active items
                    if item_key not in seen_item_ids:
                        seen_item_ids.add(item_key)
                    
        elif participant.need_id:
            need = session.get(Need, participant.need_id)
            if need:
                # Check if user is either the participant or the need creator
                is_participant = participant.user_id == user.id
                is_creator = need.creator_id == user.id
                
                if is_participant or is_creator:
                    if participant.id in seen_participant_ids:
                        continue
                    seen_participant_ids.add(participant.id)
                    
                    # For accepted status (active exchanges), if user is creator, only add once per item
                    item_key = ("need", participant.need_id)
                    if status_filter == "accepted" and is_creator:
                        if item_key in seen_item_ids:
                            continue  # Skip duplicate - already added this need
                        seen_item_ids.add(item_key)
                        # For creator with active exchanges, show "Waiting for participants"
                        exchanges.append(CompletedExchangeResponse(
                            id=0,  # Not tied to specific participant
                            offer_id=None,
                            need_id=participant.need_id,
                            item_title=need.title,
                            item_description=need.description,
                            item_type="need",
                            other_user_id=None,
                            other_username="Waiting for participants",
                            role="creator",
                            hours=need.hours,
                            completed_at=need.created_at.isoformat(),
                            is_remote=need.is_remote,
                            location_name=need.location_name,
                        ))
                        continue
                    
                    # For completed or if user is participant, show normally
                    # Determine the "other party" from user's perspective
                    if is_participant:
                        other_user = session.get(User, need.creator_id)
                        other_user_id = need.creator_id
                        role = participant.role.value
                    else:  # is_creator
                        other_user = session.get(User, participant.user_id)
                        other_user_id = participant.user_id
                        # If participant was provider, creator was requester and vice versa
                        role = "requester" if participant.role.value == "provider" else "provider"
                    
                    exchanges.append(CompletedExchangeResponse(
                        id=participant.id,
                        offer_id=None,
                        need_id=participant.need_id,
                        item_title=need.title,
                        item_description=need.description,
                        item_type="need",
                        other_user_id=other_user_id,
                        other_username=other_user.username if other_user else "Unknown",
                        role=role,
                        hours=participant.hours_contributed,
                        completed_at=participant.updated_at.isoformat(),
                        is_remote=need.is_remote,
                        location_name=need.location_name,
                    ))
                    
                    # Track this item to avoid duplicates when adding own active items
                    if item_key not in seen_item_ids:
                        seen_item_ids.add(item_key)
    
    # If status_filter is "accepted" or "all", also include user's own ACTIVE offers/needs
    # even if they have no accepted participants yet
    if status_filter in ["accepted", "all"]:
        from app.models.offer import OfferStatus
        from app.models.need import NeedStatus
        
        # Get user's own ACTIVE offers
        user_offers = session.exec(
            select(Offer).where(
                Offer.creator_id == user.id,
                Offer.status == OfferStatus.ACTIVE
            )
        ).all()
        
        for offer in user_offers:
            item_key = ("offer", offer.id)
            if item_key not in seen_item_ids:
                exchanges.append(CompletedExchangeResponse(
                    id=0,  # No participant ID for items without accepted participants
                    offer_id=offer.id,
                    need_id=None,
                    item_title=offer.title,
                    item_description=offer.description,
                    item_type="offer",
                    other_user_id=None,  # No other party yet
                    other_username="Waiting for participants",
                    role="creator",
                    hours=offer.hours,
                    completed_at=offer.created_at.isoformat(),
                    is_remote=offer.is_remote,
                    location_name=offer.location_name,
                ))
        
        # Get user's own ACTIVE needs
        user_needs = session.exec(
            select(Need).where(
                Need.creator_id == user.id,
                Need.status == NeedStatus.ACTIVE
            )
        ).all()
        
        for need in user_needs:
            item_key = ("need", need.id)
            if item_key not in seen_item_ids:
                exchanges.append(CompletedExchangeResponse(
                    id=0,  # No participant ID for items without accepted participants
                    offer_id=None,
                    need_id=need.id,
                    item_title=need.title,
                    item_description=need.description,
                    item_type="need",
                    other_user_id=None,  # No other party yet
                    other_username="Waiting for participants",
                    role="creator",
                    hours=need.hours,
                    completed_at=need.created_at.isoformat(),
                    is_remote=need.is_remote,
                    location_name=need.location_name,
                ))
    
    # Sort by completed_at descending
    exchanges.sort(key=lambda x: x.completed_at, reverse=True)
    
    # Apply pagination
    total = len(exchanges)
    paginated_exchanges = exchanges[skip:skip + limit]
    
    return CompletedExchangesListResponse(
        items=paginated_exchanges,
        total=total,
        skip=skip,
        limit=limit,
    )
