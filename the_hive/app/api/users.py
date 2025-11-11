"""
API endpoints for user profiles.

SRS Requirements:
- FR-2: Profile Management
- FR-2.4: Profile includes description, skills, location
- FR-10.3: Comments visible on profiles
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.core.auth import CurrentUser
from app.core.db import get_session
from app.models.user import User
from app.models.ledger import LedgerEntry
from app.models.comment import Comment
from app.schemas.auth import UserPublic
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserStats(BaseModel):
    """User statistics for profile display."""
    balance: float
    hours_given: float
    hours_received: float
    completed_exchanges: int
    comments_received: int


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
    
    # Comments received count
    comments_count = session.exec(
        select(func.count(Comment.id)).where(
            Comment.to_user_id == user_id,
            Comment.is_visible == True,
            Comment.is_approved == True
        )
    ).one() or 0
    
    stats = UserStats(
        balance=user.balance,
        hours_given=debit_sum,
        hours_received=credit_sum,
        completed_exchanges=completed_count,
        comments_received=comments_count
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
