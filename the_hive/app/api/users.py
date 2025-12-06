"""
API endpoints for user profiles.

SRS Requirements:
- FR-2: Profile Management
- FR-2.4: Profile includes description, skills, location
- FR-10.3: Ratings visible on profiles
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.user import User
from app.models.ledger import LedgerEntry
from app.models.rating import Rating
from app.schemas.auth import UserPublic
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


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
    location_name: Optional[str]
    balance: float
    stats: UserStats
    created_at: str
    
    model_config = {"from_attributes": True}


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
    # Get user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate stats from ledger
    # Hours given (debit entries)
    debit_sum = session.exec(
        select(func.sum(LedgerEntry.debit)).where(LedgerEntry.user_id == user_id)
    ).one() or 0.0
    
    # Hours received (credit entries)
    credit_sum = session.exec(
        select(func.sum(LedgerEntry.credit)).where(LedgerEntry.user_id == user_id)
    ).one() or 0.0
    
    # Completed exchanges (count of COMPLETED participants)
    from app.models.participant import Participant, ParticipantStatus
    completed_count = session.exec(
        select(func.count(Participant.id)).where(
            Participant.user_id == user_id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    # Ratings received count
    ratings_count = session.exec(
        select(func.count(Rating.id)).where(
            Rating.to_user_id == user_id
        )
    ).one() or 0
    
    stats = UserStats(
        balance=user.balance,
        hours_given=debit_sum,
        hours_received=credit_sum,
        completed_exchanges=completed_count,
        ratings_received=ratings_count
    )
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.full_name,
        description=user.description,
        location_name=user.location_name,
        balance=user.balance,
        stats=stats,
        created_at=user.created_at.isoformat()
    )


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
    # Get user by username
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate stats from ledger
    # Hours given (debit entries)
    debit_sum = session.exec(
        select(func.sum(LedgerEntry.debit)).where(LedgerEntry.user_id == user.id)
    ).one() or 0.0
    
    # Hours received (credit entries)
    credit_sum = session.exec(
        select(func.sum(LedgerEntry.credit)).where(LedgerEntry.user_id == user.id)
    ).one() or 0.0
    
    # Completed exchanges (count of COMPLETED participants)
    from app.models.participant import Participant, ParticipantStatus
    completed_count = session.exec(
        select(func.count(Participant.id)).where(
            Participant.user_id == user.id,
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).one() or 0
    
    # Ratings received count
    ratings_count = session.exec(
        select(func.count(Rating.id)).where(
            Rating.to_user_id == user.id
        )
    ).one() or 0
    
    stats = UserStats(
        balance=user.balance,
        hours_given=debit_sum,
        hours_received=credit_sum,
        completed_exchanges=completed_count,
        ratings_received=ratings_count
    )
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.full_name,
        description=user.description,
        location_name=user.location_name,
        balance=user.balance,
        stats=stats,
        created_at=user.created_at.isoformat()
    )


class CompletedExchangeResponse(BaseModel):
    """Schema for a completed exchange."""
    id: int  # Participant ID
    offer_id: Optional[int]
    need_id: Optional[int]
    item_title: str
    item_description: str
    item_type: str  # "offer" or "need"
    other_user_id: int  # The other party in the exchange
    other_username: str
    role: str  # provider or requester
    hours: float
    completed_at: str
    
    model_config = {"from_attributes": True}


class CompletedExchangesListResponse(BaseModel):
    """Schema for paginated completed exchanges list."""
    items: list[CompletedExchangeResponse]
    total: int
    skip: int
    limit: int


from datetime import datetime
from fastapi import Query
from sqlmodel import or_


@router.get("/username/{username}/completed-exchanges", response_model=CompletedExchangesListResponse)
def get_user_completed_exchanges(
    username: str,
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> CompletedExchangesListResponse:
    """
    Get completed exchanges for a user by username.
    
    SRS FR-10: View completed exchanges on profile
    
    Returns completed exchanges where user was either:
    1. A participant (applied to someone's offer/need)
    2. The creator of an offer/need that was completed
    
    Returns:
        List of completed exchanges with details
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
    
    # Get all completed participants
    # We need to find exchanges where either:
    # 1. User is the participant (user_id == user.id)
    # 2. User is the creator of the offer/need
    
    # First, get all completed participants
    all_completed = session.exec(
        select(Participant).where(
            Participant.status == ParticipantStatus.COMPLETED
        )
    ).all()
    
    # Build response with enriched details
    exchanges = []
    seen_participant_ids = set()  # Avoid duplicates
    
    for participant in all_completed:
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
                    ))
                    
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
