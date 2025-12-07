"""
Tests for role-based access control.

Tests the require_role dependency and authorization.
"""
import pytest
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.auth import AdminUser, CurrentUser, ModeratorUser, require_role
from app.core.db import get_session
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User

# Create a test router for role testing
test_router = APIRouter(prefix="/test", tags=["Test"])


@test_router.get("/user-only")
def user_endpoint(current_user: CurrentUser):
    """Endpoint accessible by any authenticated user."""
    return {"message": f"Hello {current_user.username}", "role": current_user.role}


@test_router.get("/moderator-only")
def moderator_endpoint(current_user: ModeratorUser):
    """Endpoint accessible only by moderators and admins."""
    return {"message": f"Moderator access for {current_user.username}"}


@test_router.get("/admin-only")
def admin_endpoint(current_user: AdminUser):
    """Endpoint accessible only by admins."""
    return {"message": f"Admin access for {current_user.username}"}


@test_router.get("/custom-role", dependencies=[Depends(require_role("admin", "moderator"))])
def custom_role_endpoint():
    """Test custom role dependency."""
    return {"message": "Custom role access granted"}


# Add test router to app
app.include_router(test_router, prefix="/api/v1")


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh in-memory database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="regular_user_token")
def regular_user_token_fixture(session: Session):
    """Create a regular user and return their token."""
    user = User(
        id=1,
        email="user@example.com",
        username="regularuser",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0,
        is_active=True
    )
    session.add(user)
    session.commit()
    
    token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role})
    return token


@pytest.fixture(name="moderator_token")
def moderator_token_fixture(session: Session):
    """Create a moderator user and return their token."""
    user = User(
        id=2,
        email="mod@example.com",
        username="moderator",
        password_hash=get_password_hash("password123"),
        role="moderator",
        balance=5.0,
        is_active=True
    )
    session.add(user)
    session.commit()
    
    token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role})
    return token


@pytest.fixture(name="admin_token")
def admin_token_fixture(session: Session):
    """Create an admin user and return their token."""
    user = User(
        id=3,
        email="admin@example.com",
        username="admin",
        password_hash=get_password_hash("password123"),
        role="admin",
        balance=5.0,
        is_active=True
    )
    session.add(user)
    session.commit()
    
    token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role})
    return token


def test_regular_user_access(client: TestClient, regular_user_token: str):
    """Test that regular users can access user-only endpoints."""
    response = client.get(
        "/api/v1/test/user-only",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "user"


def test_regular_user_forbidden_moderator(client: TestClient, regular_user_token: str):
    """Test that regular users cannot access moderator endpoints (SRS requirement)."""
    response = client.get(
        "/api/v1/test/moderator-only",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_regular_user_forbidden_admin(client: TestClient, regular_user_token: str):
    """Test that regular users cannot access admin endpoints (SRS requirement)."""
    response = client.get(
        "/api/v1/test/admin-only",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_moderator_access_user_endpoint(client: TestClient, moderator_token: str):
    """Test that moderators can access user endpoints."""
    response = client.get(
        "/api/v1/test/user-only",
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    
    assert response.status_code == 200


def test_moderator_access_moderator_endpoint(client: TestClient, moderator_token: str):
    """Test that moderators can access moderator endpoints."""
    response = client.get(
        "/api/v1/test/moderator-only",
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    
    assert response.status_code == 200


def test_moderator_forbidden_admin(client: TestClient, moderator_token: str):
    """Test that moderators cannot access admin-only endpoints."""
    response = client.get(
        "/api/v1/test/admin-only",
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    
    assert response.status_code == 403


def test_admin_access_all_endpoints(client: TestClient, admin_token: str):
    """Test that admins can access all endpoints."""
    # User endpoint
    response = client.get(
        "/api/v1/test/user-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Moderator endpoint
    response = client.get(
        "/api/v1/test/moderator-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Admin endpoint
    response = client.get(
        "/api/v1/test/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_custom_role_dependency(client: TestClient, regular_user_token: str, moderator_token: str, admin_token: str):
    """Test custom role dependency with multiple allowed roles."""
    # Regular user should be denied
    response = client.get(
        "/api/v1/test/custom-role",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == 403
    
    # Moderator should be allowed
    response = client.get(
        "/api/v1/test/custom-role",
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    assert response.status_code == 200
    
    # Admin should be allowed
    response = client.get(
        "/api/v1/test/custom-role",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_no_token_returns_401(client: TestClient):
    """Test that endpoints without token return 403."""
    response = client.get("/api/v1/test/user-only")
    assert response.status_code == 403


def test_invalid_token_returns_401(client: TestClient):
    """Test that invalid token returns 401."""
    response = client.get(
        "/api/v1/test/user-only",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_inactive_user_denied(client: TestClient, session: Session):
    """Test that inactive users cannot access endpoints."""
    # Create inactive user
    user = User(
        id=99,
        email="inactive@example.com",
        username="inactive",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0,
        is_active=False  # Inactive
    )
    session.add(user)
    session.commit()
    
    # Create token for inactive user
    token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role})
    
    # Try to access endpoint
    response = client.get(
        "/api/v1/test/user-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "Inactive user" in response.json()["detail"]
