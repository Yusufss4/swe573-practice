"""
Authentication API endpoints.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.auth import CurrentUser, get_current_user
from app.core.db import get_session
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    session: Annotated[Session, Depends(get_session)]
) -> User:
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **username**: Username between 3-50 characters (unique)
    - **password**: Password with minimum 8 characters
    - **full_name**: Optional full name
    
    Returns the created user with default role='user' and balance=5.0
    """
    # Check if username already exists
    statement = select(User).where(User.username == user_data.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_email = session.exec(statement).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user with default values from SRS
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role="user",  # Default role
        balance=5.0,  # Starting balance from SRS
        is_active=True
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    session: Annotated[Session, Depends(get_session)]
) -> dict[str, str]:
    """
    Login with username and password.
    
    - **username**: Registered username
    - **password**: User password
    
    Returns a JWT access token valid for 7 days.
    """
    # Find user by username
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "username": user.username,
            "role": user.role
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: CurrentUser) -> User:
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header:
    `Authorization: Bearer <token>`
    
    Returns the current user's profile information.
    """
    return current_user


@router.post("/logout")
def logout() -> dict[str, str]:
    """
    Logout endpoint (stateless JWT).
    
    Since JWT tokens are stateless, logout is handled client-side
    by removing the token. This endpoint exists for API completeness.
    
    Clients should delete the stored token upon calling this endpoint.
    """
    return {"message": "Successfully logged out. Please delete your token."}
