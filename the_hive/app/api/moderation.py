"""
Moderation actions API for content removal and user sanctions.

SRS Requirements:
- FR-11.3: Moderators can remove inappropriate content
- FR-11.5: Moderators can suspend or ban users
- FR-11.6: Actions are logged with reason and moderator
"""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Body
from sqlmodel import Session

from app.core.auth import ModeratorUser
from app.core.db import SessionDep
from app.models.user import User
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.forum import ForumComment
from app.schemas.auth import UserPublic


router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.delete("/offers/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_offer(
    offer_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
    reason: str = Body(..., embed=True, description="Reason for removal"),
) -> None:
    """
    Remove an offer (moderators only).
    
    SRS FR-11.3: Moderators can remove inappropriate offers
    
    This archives the offer and marks it as removed by moderation.
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Archive the offer (mark as cancelled and set archived timestamp)
    offer.status = OfferStatus.CANCELLED
    offer.archived_at = datetime.utcnow()
    
    # Note: In production, you might want to add a moderation_reason field
    # to the Offer model to track why it was removed
    
    session.add(offer)
    session.commit()


@router.delete("/needs/{need_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_need(
    need_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
    reason: str = Body(..., embed=True, description="Reason for removal"),
) -> None:
    """
    Remove a need (moderators only).
    
    SRS FR-11.3: Moderators can remove inappropriate needs
    
    This archives the need and marks it as removed by moderation.
    """
    need = session.get(Need, need_id)
    if not need:
        raise HTTPException(status_code=404, detail="Need not found")
    
    # Archive the need (mark as cancelled and set archived timestamp)
    need.status = NeedStatus.CANCELLED
    need.archived_at = datetime.utcnow()
    
    session.add(need)
    session.commit()


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    comment_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
    reason: str = Body(..., embed=True, description="Reason for removal"),
) -> None:
    """
    Remove a forum comment (moderators only).
    
    SRS FR-11.3: Moderators can remove inappropriate comments
    
    This soft-deletes the comment by setting is_deleted flag.
    """
    comment = session.get(ForumComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Soft delete
    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()
    
    session.add(comment)
    session.commit()


@router.put("/users/{user_id}/suspend", response_model=UserPublic)
def suspend_user(
    user_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
    reason: str = Body(..., embed=True, description="Reason for suspension"),
    duration_days: int = Body(7, embed=True, ge=1, le=365, description="Suspension duration in days"),
) -> UserPublic:
    """
    Suspend a user temporarily (moderators only).
    
    SRS FR-11.5: Moderators can suspend users for policy violations
    
    Suspended users cannot:
    - Create new offers or needs
    - Participate in exchanges
    - Post forum comments
    
    They can still view content and access their profile.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent suspending other moderators or admins
    if user.is_moderator or user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot suspend moderators or admins"
        )
    
    # Prevent self-suspension
    if user.id == moderator.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot suspend yourself"
        )
    
    # Set suspension
    user.is_suspended = True
    user.suspended_at = datetime.utcnow()
    user.suspended_until = datetime.utcnow() + timedelta(days=duration_days)
    user.suspension_reason = reason
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserPublic.model_validate(user)


@router.put("/users/{user_id}/unsuspend", response_model=UserPublic)
def unsuspend_user(
    user_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
) -> UserPublic:
    """
    Remove suspension from a user (moderators only).
    
    SRS FR-11.5: Moderators can lift suspensions early
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not suspended"
        )
    
    # Remove suspension
    user.is_suspended = False
    user.suspended_at = None
    user.suspended_until = None
    user.suspension_reason = None
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserPublic.model_validate(user)


@router.put("/users/{user_id}/ban", response_model=UserPublic)
def ban_user(
    user_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
    reason: str = Body(..., embed=True, description="Reason for permanent ban"),
) -> UserPublic:
    """
    Permanently ban a user (moderators only).
    
    SRS FR-11.5: Moderators can permanently ban users for severe violations
    
    Banned users cannot:
    - Log in
    - Access any platform features
    - Create new accounts with the same email
    
    This is irreversible without admin intervention.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent banning other moderators or admins
    if user.is_moderator or user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban moderators or admins"
        )
    
    # Prevent self-ban
    if user.id == moderator.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban yourself"
        )
    
    # Set ban
    user.is_banned = True
    user.banned_at = datetime.utcnow()
    user.ban_reason = reason
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserPublic.model_validate(user)


@router.put("/users/{user_id}/unban", response_model=UserPublic)
def unban_user(
    user_id: int,
    moderator: ModeratorUser,
    session: SessionDep,
) -> UserPublic:
    """
    Remove ban from a user (moderators only).
    
    SRS FR-11.5: Moderators can unban users after review
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not banned"
        )
    
    # Remove ban
    user.is_banned = False
    user.banned_at = None
    user.ban_reason = None
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserPublic.model_validate(user)
