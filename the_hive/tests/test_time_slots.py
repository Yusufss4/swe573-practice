"""
Tests for available time slots functionality in offers and needs.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash


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


@pytest.fixture
def test_user(session: Session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        full_name="Test User",
        role=UserRole.USER,
        balance=5.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user: User):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_offer_with_time_slots(client: TestClient, auth_headers: dict):
    """Test creating an offer with available time slots."""
    offer_data = {
        "title": "Web Development Tutoring",
        "description": "Help with HTML, CSS, JavaScript",
        "is_remote": True,
        "capacity": 3,
        "tags": ["Coding", "Education"],
        "available_slots": [
            {
                "date": "2025-12-01",
                "time_ranges": [
                    {"start_time": "14:00", "end_time": "15:00"},
                    {"start_time": "15:00", "end_time": "16:00"}
                ]
            },
            {
                "date": "2025-12-02",
                "time_ranges": [
                    {"start_time": "10:00", "end_time": "11:00"}
                ]
            }
        ]
    }
    
    response = client.post("/api/v1/offers/", json=offer_data, headers=auth_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == offer_data["title"]
    assert data["available_slots"] is not None
    assert len(data["available_slots"]) == 2
    assert data["available_slots"][0]["date"] == "2025-12-01"
    assert len(data["available_slots"][0]["time_ranges"]) == 2
    assert data["available_slots"][0]["time_ranges"][0]["start_time"] == "14:00"


def test_create_offer_without_time_slots(client: TestClient, auth_headers: dict):
    """Test creating an offer without time slots (flexible scheduling)."""
    offer_data = {
        "title": "General Programming Help",
        "description": "Available for various programming help",
        "is_remote": True,
        "capacity": 2,
        "tags": ["Programming"],
        "available_slots": None
    }
    
    response = client.post("/api/v1/offers/", json=offer_data, headers=auth_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == offer_data["title"]
    assert data["available_slots"] is None


def test_update_offer_time_slots(client: TestClient, auth_headers: dict):
    """Test updating an offer's time slots."""
    # Create offer
    offer_data = {
        "title": "Python Tutoring",
        "description": "Learn Python programming",
        "is_remote": True,
        "capacity": 2,
        "tags": ["Python"],
        "available_slots": None
    }
    
    create_response = client.post("/api/v1/offers/", json=offer_data, headers=auth_headers)
    assert create_response.status_code == 201
    offer_id = create_response.json()["id"]
    
    # Update with time slots
    update_data = {
        "available_slots": [
            {
                "date": "2025-12-10",
                "time_ranges": [
                    {"start_time": "09:00", "end_time": "10:00"}
                ]
            }
        ]
    }
    
    update_response = client.patch(
        f"/api/v1/offers/{offer_id}",
        json=update_data,
        headers=auth_headers
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["available_slots"] is not None
    assert len(data["available_slots"]) == 1
    assert data["available_slots"][0]["date"] == "2025-12-10"


def test_create_need_with_time_slots(client: TestClient, auth_headers: dict):
    """Test creating a need with available time slots."""
    need_data = {
        "title": "Need Python Help",
        "description": "Looking for help with Django project",
        "is_remote": True,
        "capacity": 1,
        "tags": ["Python", "Django"],
        "available_slots": [
            {
                "date": "2025-12-05",
                "time_ranges": [
                    {"start_time": "14:00", "end_time": "16:00"}
                ]
            }
        ]
    }
    
    response = client.post("/api/v1/needs/", json=need_data, headers=auth_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == need_data["title"]
    assert data["available_slots"] is not None
    assert len(data["available_slots"]) == 1
    assert data["available_slots"][0]["date"] == "2025-12-05"


def test_invalid_time_range(client: TestClient, auth_headers: dict):
    """Test that end_time must be after start_time."""
    offer_data = {
        "title": "Invalid Time Slots",
        "description": "This should fail",
        "is_remote": True,
        "capacity": 1,
        "tags": ["Test"],
        "available_slots": [
            {
                "date": "2025-12-01",
                "time_ranges": [
                    {"start_time": "16:00", "end_time": "14:00"}  # Invalid: end before start
                ]
            }
        ]
    }
    
    response = client.post("/api/v1/offers/", json=offer_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error


def test_invalid_time_format(client: TestClient, auth_headers: dict):
    """Test that time must be in HH:MM format."""
    offer_data = {
        "title": "Invalid Time Format",
        "description": "This should fail",
        "is_remote": True,
        "capacity": 1,
        "tags": ["Test"],
        "available_slots": [
            {
                "date": "2025-12-01",
                "time_ranges": [
                    {"start_time": "2:00 PM", "end_time": "3:00 PM"}  # Invalid format
                ]
            }
        ]
    }
    
    response = client.post("/api/v1/offers/", json=offer_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error


def test_invalid_date_format(client: TestClient, auth_headers: dict):
    """Test that date must be in YYYY-MM-DD format."""
    offer_data = {
        "title": "Invalid Date Format",
        "description": "This should fail",
        "is_remote": True,
        "capacity": 1,
        "tags": ["Test"],
        "available_slots": [
            {
                "date": "12/01/2025",  # Invalid format
                "time_ranges": [
                    {"start_time": "14:00", "end_time": "15:00"}
                ]
            }
        ]
    }
    
    response = client.post("/api/v1/offers/", json=offer_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error
