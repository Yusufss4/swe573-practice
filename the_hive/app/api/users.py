# SRS FR-8: User profile endpoints
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    session: Annotated[Session, Depends(get_session)]
) -> User:
    """
    SRS FR-8.1: Get public user profile by ID
    Returns user details including balance, location (if shared), and basic info.
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
