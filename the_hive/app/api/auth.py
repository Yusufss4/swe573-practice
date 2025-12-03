from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.auth import CurrentUser, get_current_user
from app.core.db import get_session
from app.core.ledger import get_user_ledger
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.schemas.ledger import LedgerHistoryResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    session: Annotated[Session, Depends(get_session)]
) -> User:
    statement = select(User).where(User.username == user_data.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    statement = select(User).where(User.email == user_data.email)
    existing_email = session.exec(statement).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role="user",
        balance=5.0,
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
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
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
    return current_user


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Successfully logged out. Please delete your token."}


@router.get("/me/ledger", response_model=LedgerHistoryResponse)
def get_my_ledger_history(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 20
) -> dict:
    """Get current user's transaction history from the TimeBank ledger"""
    if not current_user.id:
        raise HTTPException(status_code=400, detail="User ID not found")
    
    entries, total = get_user_ledger(session, current_user.id, skip, limit)
    
    return {
        "items": entries,
        "total": total,
        "skip": skip,
        "limit": limit,
        "current_balance": current_user.balance or 0.0
    }
