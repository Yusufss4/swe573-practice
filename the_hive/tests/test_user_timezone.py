"""
Test timezone functionality in user registration and time slots.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session


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


def test_register_user_with_timezone(client: TestClient):
    """Test user registration with timezone."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "istanbul@example.com",
            "username": "istanbuluser",
            "password": "SecurePass123!",
            "full_name": "Istanbul User",
            "timezone": "Europe/Istanbul"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "istanbuluser"
    assert data["timezone"] == "Europe/Istanbul"
    assert data["balance"] == 5.0


def test_register_user_without_timezone_defaults_to_utc(client: TestClient):
    """Test user registration without timezone defaults to UTC."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "notz@example.com",
            "username": "notzuser",
            "password": "SecurePass123!",
            "full_name": "No TZ User"
            # No timezone provided
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "notzuser"
    assert data["timezone"] == "UTC"  # Should default to UTC


def test_user_timezone_in_me_endpoint(client: TestClient):
    """Test that timezone is returned in /me endpoint."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "tokyo@example.com",
            "username": "tokyouser",
            "password": "SecurePass123!",
            "full_name": "Tokyo User",
            "timezone": "Asia/Tokyo"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "tokyouser", "password": "SecurePass123!"}
    )
    token = login_response.json()["access_token"]
    
    # Get user info
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert me_response.status_code == 200
    data = me_response.json()
    assert data["username"] == "tokyouser"
    assert data["timezone"] == "Asia/Tokyo"


def test_create_offer_with_user_timezone_context(client: TestClient):
    """Test creating offer - timezone context is now available from user."""
    # Register user with timezone
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "ny@example.com",
            "username": "nyuser",
            "password": "SecurePass123!",
            "timezone": "America/New_York"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "nyuser", "password": "SecurePass123!"}
    )
    token = login_response.json()["access_token"]
    
    # Create offer with time slots (timezone can be inferred from user or explicitly set)
    offer_response = client.post(
        "/api/v1/offers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "NYC Tutoring",
            "description": "Tutoring in New York",
            "is_remote": False,
            "location_name": "New York, NY",
            "capacity": 2,
            "tags": ["Education"],
            "available_slots": [
                {
                    "date": "2025-12-01",
                    "time_ranges": [
                        {"start_time": "10:00", "end_time": "11:00"}
                    ],
                    "timezone": "America/New_York"  # Can explicitly set or use user's timezone
                }
            ]
        }
    )
    
    assert offer_response.status_code == 201
    offer_data = offer_response.json()
    assert offer_data["title"] == "NYC Tutoring"
    assert offer_data["available_slots"] is not None
    assert offer_data["available_slots"][0]["timezone"] == "America/New_York"


def test_multiple_users_different_timezones(client: TestClient):
    """Test that multiple users can have different timezones."""
    # Register users in different timezones
    users = [
        {"username": "user_utc", "email": "utc@example.com", "timezone": "UTC"},
        {"username": "user_istanbul", "email": "ist@example.com", "timezone": "Europe/Istanbul"},
        {"username": "user_tokyo", "email": "tky@example.com", "timezone": "Asia/Tokyo"},
        {"username": "user_la", "email": "la@example.com", "timezone": "America/Los_Angeles"},
    ]
    
    for user in users:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": user["email"],
                "username": user["username"],
                "password": "SecurePass123!",
                "full_name": f"{user['username']} Full Name",
                "timezone": user["timezone"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["timezone"] == user["timezone"]
