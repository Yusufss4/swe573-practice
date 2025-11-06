"""
User API endpoints.

Provides CRUD operations for users.
"""
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.core.db import SessionDep
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: SessionDep) -> User:
    """
    Create a new user.
    
    Args:
        user: User data
        session: Database session
    
    Returns:
        Created user
    
    Raises:
        HTTPException: If user with email or username already exists
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[User]:
    """
    List all users with pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Filter only active users
    
    Returns:
        List of users
    """
    statement = select(User)
    
    if active_only:
        statement = statement.where(User.is_active == True)
    
    statement = statement.offset(skip).limit(limit)
    users = session.exec(statement).all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: SessionDep) -> User:
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID
        session: Database session
    
    Returns:
        User details
    
    Raises:
        HTTPException: If user not found
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: SessionDep
) -> User:
    """
    Update a user.
    
    Args:
        user_id: User ID
        user_update: Updated user data
        session: Database session
    
    Returns:
        Updated user
    
    Raises:
        HTTPException: If user not found
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    # Update timestamp
    from datetime import datetime
    db_user.updated_at = datetime.utcnow()
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: SessionDep) -> None:
    """
    Delete a user.
    
    Args:
        user_id: User ID
        session: Database session
    
    Raises:
        HTTPException: If user not found
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    session.delete(user)
    session.commit()
