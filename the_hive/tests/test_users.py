"""
Tests for user API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.models.user import User


# Create in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
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


def test_create_user(client: TestClient):
    """Test creating a new user."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_email(client: TestClient):
    """Test creating a user with duplicate email fails."""
    # Create first user
    client.post(
        "/api/v1/users/",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
        },
    )
    
    # Try to create second user with same email
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_create_user_duplicate_username(client: TestClient):
    """Test creating a user with duplicate username fails."""
    # Create first user
    client.post(
        "/api/v1/users/",
        json={
            "email": "user1@example.com",
            "username": "duplicateuser",
        },
    )
    
    # Try to create second user with same username
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "user2@example.com",
            "username": "duplicateuser",
        },
    )
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"].lower()


def test_list_users(client: TestClient):
    """Test listing all users."""
    # Create test users
    for i in range(3):
        client.post(
            "/api/v1/users/",
            json={
                "email": f"user{i}@example.com",
                "username": f"user{i}",
            },
        )
    
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_users_with_pagination(client: TestClient):
    """Test listing users with pagination."""
    # Create 5 test users
    for i in range(5):
        client.post(
            "/api/v1/users/",
            json={
                "email": f"user{i}@example.com",
                "username": f"user{i}",
            },
        )
    
    # Get first 2 users
    response = client.get("/api/v1/users/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Get next 2 users
    response = client.get("/api/v1/users/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_user(client: TestClient):
    """Test getting a specific user."""
    # Create a user
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "getuser@example.com",
            "username": "getuser",
        },
    )
    user_id = create_response.json()["id"]
    
    # Get the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "getuser@example.com"


def test_get_user_not_found(client: TestClient):
    """Test getting a non-existent user."""
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404


def test_update_user(client: TestClient):
    """Test updating a user."""
    # Create a user
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "original@example.com",
            "username": "original",
        },
    )
    user_id = create_response.json()["id"]
    
    # Update the user
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "full_name": "Updated Name",
            "is_active": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["is_active"] is False
    assert data["email"] == "original@example.com"  # Unchanged


def test_delete_user(client: TestClient):
    """Test deleting a user."""
    # Create a user
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "delete@example.com",
            "username": "deleteuser",
        },
    )
    user_id = create_response.json()["id"]
    
    # Delete the user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user is deleted
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 404


def test_delete_user_not_found(client: TestClient):
    """Test deleting a non-existent user."""
    response = client.delete("/api/v1/users/999")
    assert response.status_code == 404
