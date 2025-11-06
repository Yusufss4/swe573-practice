"""
Example API endpoint showing database usage.

This demonstrates how to use SQLModel sessions with FastAPI.
"""
from fastapi import APIRouter

from app.core.db import SessionDep
# from app.models.base import User  # Uncomment when you have models
# from sqlmodel import select

router = APIRouter(prefix="/examples", tags=["Examples"])


@router.get("/db-test")
async def test_database_connection(session: SessionDep) -> dict:
    """
    Test database connection using dependency injection.
    
    Args:
        session: Database session (injected by FastAPI)
    
    Returns:
        dict: Connection status
    """
    try:
        # Example: Query database
        # users = session.exec(select(User)).all()
        # return {"status": "connected", "user_count": len(users)}
        
        return {
            "status": "connected",
            "message": "Database session available",
            "note": "Add models to run actual queries"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Example: Creating a record
# @router.post("/users")
# async def create_user(user: UserCreate, session: SessionDep) -> User:
#     """Create a new user."""
#     db_user = User.from_orm(user)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user


# Example: Reading records
# @router.get("/users")
# async def list_users(session: SessionDep, skip: int = 0, limit: int = 100) -> list[User]:
#     """List all users with pagination."""
#     statement = select(User).offset(skip).limit(limit)
#     users = session.exec(statement).all()
#     return users


# Example: Updating a record
# @router.patch("/users/{user_id}")
# async def update_user(user_id: int, user: UserUpdate, session: SessionDep) -> User:
#     """Update a user."""
#     db_user = session.get(User, user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     
#     user_data = user.dict(exclude_unset=True)
#     for key, value in user_data.items():
#         setattr(db_user, key, value)
#     
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user


# Example: Deleting a record
# @router.delete("/users/{user_id}")
# async def delete_user(user_id: int, session: SessionDep) -> dict:
#     """Delete a user."""
#     db_user = session.get(User, user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     
#     session.delete(db_user)
#     session.commit()
#     return {"ok": True}
