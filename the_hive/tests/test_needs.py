"""
Tests for Needs API endpoints.

Validates SRS FR-3: Offer and Need Management
"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.db import get_session
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.need import Need, NeedStatus
from app.models.user import User


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


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Create authorization headers with JWT token."""
    token = create_access_token(
        data={"sub": test_user.id, "username": test_user.username, "role": test_user.role}
    )
    return {"Authorization": f"Bearer {token}"}


def test_create_need_remote(client: TestClient, auth_headers: dict):
    """Test creating a remote need (SRS FR-3.1)."""
    response = client.post(
        "/api/v1/needs/",
        headers=auth_headers,
        json={
            "title": "Need Python Help",
            "description": "I need help with Python programming basics",
            "is_remote": True,
            "capacity": 2,
            "tags": ["tutoring", "python", "help"]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == "Need Python Help"
    assert data["is_remote"] is True
    assert data["capacity"] == 2
    assert data["accepted_count"] == 0
    assert data["status"] == "active"
    assert "python" in data["tags"]
    
    # Check 7-day default (SRS constraint)
    start = datetime.fromisoformat(data["start_date"].replace('Z', '+00:00'))
    end = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
    diff = (end - start).days
    assert diff == 7


def test_create_need_with_location(client: TestClient, auth_headers: dict):
    """Test creating a need with location."""
    response = client.post(
        "/api/v1/needs/",
        headers=auth_headers,
        json={
            "title": "Need Moving Help",
            "description": "Need help moving furniture",
            "is_remote": False,
            "location_name": "Manhattan, NY",
            "location_lat": 40.7589,
            "location_lon": -73.9851,
            "tags": ["moving", "help"]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["is_remote"] is False
    assert data["location_name"] == "Manhattan, NY"


def test_list_needs(client: TestClient, session: Session, auth_headers: dict):
    """Test listing needs (SRS FR-12.2: expired hidden by default)."""
    user_id = 1
    
    # Create active need
    active_need = Need(
        creator_id=user_id,
        title="Active Need",
        description="This is active",
        is_remote=True,
        status=NeedStatus.ACTIVE,
        end_date=datetime.utcnow() + timedelta(days=5)
    )
    session.add(active_need)
    
    # Create expired need
    expired_need = Need(
        creator_id=user_id,
        title="Expired Need",
        description="This is expired",
        is_remote=True,
        status=NeedStatus.ACTIVE,
        end_date=datetime.utcnow() - timedelta(days=1)
    )
    session.add(expired_need)
    session.commit()
    
    # List needs
    response = client.get("/api/v1/needs/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only show active (expired gets archived on read)
    titles = [item["title"] for item in data["items"]]
    assert "Active Need" in titles
    assert "Expired Need" not in titles


def test_extend_need(client: TestClient, auth_headers: dict):
    """Test extending a need (SRS FR-3.2: can extend, not shorten)."""
    # Create need
    create_response = client.post(
        "/api/v1/needs/",
        headers=auth_headers,
        json={
            "title": "Test Need",
            "description": "Test description that is long enough",
            "is_remote": True,
            "tags": ["test"]
        }
    )
    need_id = create_response.json()["id"]
    original_end = datetime.fromisoformat(
        create_response.json()["end_date"].replace('Z', '+00:00')
    )
    
    # Extend by 10 days
    response = client.post(
        f"/api/v1/needs/{need_id}/extend",
        headers=auth_headers,
        json={"days": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    new_end = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
    diff = (new_end - original_end).days
    assert diff == 10


def test_update_need(client: TestClient, auth_headers: dict):
    """Test updating a need."""
    # Create need
    create_response = client.post(
        "/api/v1/needs/",
        headers=auth_headers,
        json={
            "title": "Original Need",
            "description": "Original description here",
            "is_remote": True,
            "tags": ["original"]
        }
    )
    need_id = create_response.json()["id"]
    
    # Update need
    response = client.patch(
        f"/api/v1/needs/{need_id}",
        headers=auth_headers,
        json={
            "title": "Updated Need",
            "tags": ["updated"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Need"
    assert "updated" in data["tags"]


def test_delete_need(client: TestClient, auth_headers: dict):
    """Test deleting (cancelling) a need."""
    # Create need
    create_response = client.post(
        "/api/v1/needs/",
        headers=auth_headers,
        json={
            "title": "Test Need",
            "description": "Test description that is long enough",
            "is_remote": True,
            "tags": ["test"]
        }
    )
    need_id = create_response.json()["id"]
    
    # Delete need
    response = client.delete(
        f"/api/v1/needs/{need_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
