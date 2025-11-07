"""
Tests for Offers API endpoints.

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
from app.models.offer import Offer, OfferStatus
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


def test_create_offer_remote(client: TestClient, auth_headers: dict):
    """Test creating a remote offer (SRS FR-3.1)."""
    response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Python Tutoring",
            "description": "I can help you learn Python programming basics",
            "is_remote": True,
            "capacity": 3,
            "tags": ["tutoring", "python", "programming"]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == "Python Tutoring"
    assert data["is_remote"] is True
    assert data["capacity"] == 3
    assert data["accepted_count"] == 0
    assert data["status"] == "active"
    assert "python" in data["tags"]
    assert "tutoring" in data["tags"]
    
    # Check 7-day default (SRS constraint)
    start = datetime.fromisoformat(data["start_date"].replace('Z', '+00:00'))
    end = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
    diff = (end - start).days
    assert diff == 7


def test_create_offer_with_location(client: TestClient, auth_headers: dict):
    """Test creating an offer with location."""
    response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Guitar Lessons",
            "description": "Beginner guitar lessons in person",
            "is_remote": False,
            "location_name": "Brooklyn, NY",
            "location_lat": 40.6782,
            "location_lon": -73.9442,
            "tags": ["music", "guitar", "lessons"]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["is_remote"] is False
    assert data["location_name"] == "Brooklyn, NY"
    assert data["location_lat"] == 40.6782
    assert data["location_lon"] == -73.9442


def test_create_offer_missing_location(client: TestClient, auth_headers: dict):
    """Test that non-remote offers require location."""
    response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Guitar Lessons",
            "description": "Beginner guitar lessons in person",
            "is_remote": False,
            "tags": ["music"]
        }
    )
    
    assert response.status_code == 400
    assert "location" in response.json()["detail"].lower()


def test_list_offers(client: TestClient, session: Session, auth_headers: dict):
    """Test listing offers (SRS FR-12.2: expired hidden by default)."""
    user_id = 1
    
    # Create active offer
    active_offer = Offer(
        creator_id=user_id,
        title="Active Offer",
        description="This is active",
        is_remote=True,
        status=OfferStatus.ACTIVE,
        end_date=datetime.utcnow() + timedelta(days=5)
    )
    session.add(active_offer)
    
    # Create expired offer
    expired_offer = Offer(
        creator_id=user_id,
        title="Expired Offer",
        description="This is expired",
        is_remote=True,
        status=OfferStatus.ACTIVE,  # Will be auto-archived
        end_date=datetime.utcnow() - timedelta(days=1)
    )
    session.add(expired_offer)
    session.commit()
    
    # List offers
    response = client.get("/api/v1/offers/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only show active (expired gets archived on read)
    titles = [item["title"] for item in data["items"]]
    assert "Active Offer" in titles
    assert "Expired Offer" not in titles


def test_list_my_offers(client: TestClient, auth_headers: dict):
    """Test listing user's own offers."""
    # Create offer
    client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "My Offer",
            "description": "This is my offer",
            "is_remote": True,
            "tags": ["test"]
        }
    )
    
    # List my offers
    response = client.get("/api/v1/offers/my", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] >= 1
    assert any(item["title"] == "My Offer" for item in data["items"])


def test_get_offer(client: TestClient, auth_headers: dict):
    """Test getting a specific offer."""
    # Create offer
    create_response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Test Offer",
            "description": "Test description",
            "is_remote": True,
            "tags": ["test"]
        }
    )
    offer_id = create_response.json()["id"]
    
    # Get offer
    response = client.get(f"/api/v1/offers/{offer_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == offer_id
    assert data["title"] == "Test Offer"


def test_update_offer(client: TestClient, auth_headers: dict):
    """Test updating an offer."""
    # Create offer
    create_response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Original Title",
            "description": "Original description",
            "is_remote": True,
            "capacity": 1,
            "tags": ["original"]
        }
    )
    offer_id = create_response.json()["id"]
    
    # Update offer
    response = client.patch(
        f"/api/v1/offers/{offer_id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "capacity": 5,
            "tags": ["updated", "new"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["capacity"] == 5
    assert "updated" in data["tags"]


def test_cannot_decrease_capacity_below_accepted(client: TestClient, session: Session, auth_headers: dict):
    """Test SRS FR-3.7: Cannot decrease capacity below accepted count."""
    user_id = 1
    
    # Create offer with accepted participants
    offer = Offer(
        creator_id=user_id,
        title="Test Offer",
        description="Test",
        is_remote=True,
        capacity=5,
        accepted_count=3,  # 3 people accepted
        status=OfferStatus.ACTIVE
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    # Try to decrease capacity to 2 (below accepted count of 3)
    response = client.patch(
        f"/api/v1/offers/{offer.id}",
        headers=auth_headers,
        json={"capacity": 2}
    )
    
    assert response.status_code == 400
    assert "accepted count" in response.json()["detail"].lower()


def test_extend_offer(client: TestClient, auth_headers: dict):
    """Test extending an offer (SRS FR-3.2: can extend, not shorten)."""
    # Create offer
    create_response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Test Offer",
            "description": "Test description",
            "is_remote": True,
            "tags": ["test"]
        }
    )
    offer_id = create_response.json()["id"]
    original_end = datetime.fromisoformat(
        create_response.json()["end_date"].replace('Z', '+00:00')
    )
    
    # Extend by 5 days
    response = client.post(
        f"/api/v1/offers/{offer_id}/extend",
        headers=auth_headers,
        json={"days": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    new_end = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
    diff = (new_end - original_end).days
    assert diff == 5


def test_renew_expired_offer(client: TestClient, session: Session, auth_headers: dict):
    """Test renewing an expired offer (SRS FR-3.2)."""
    user_id = 1
    
    # Create expired offer
    offer = Offer(
        creator_id=user_id,
        title="Expired Offer",
        description="Test",
        is_remote=True,
        status=OfferStatus.EXPIRED,
        end_date=datetime.utcnow() - timedelta(days=2)
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    # Renew by extending
    response = client.post(
        f"/api/v1/offers/{offer.id}/extend",
        headers=auth_headers,
        json={"days": 7}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should be active again
    assert data["status"] == "active"
    
    # End date should be in future
    new_end = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
    assert new_end > datetime.utcnow()


def test_delete_offer(client: TestClient, auth_headers: dict):
    """Test deleting (cancelling) an offer."""
    # Create offer
    create_response = client.post(
        "/api/v1/offers/",
        headers=auth_headers,
        json={
            "title": "Test Offer",
            "description": "Test description",
            "is_remote": True,
            "tags": ["test"]
        }
    )
    offer_id = create_response.json()["id"]
    
    # Delete offer
    response = client.delete(
        f"/api/v1/offers/{offer_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's cancelled (soft delete)
    get_response = client.get(f"/api/v1/offers/{offer_id}")
    assert get_response.json()["status"] == "cancelled"


def test_cannot_update_others_offer(client: TestClient, session: Session, auth_headers: dict):
    """Test that users cannot update offers they don't own."""
    # Create another user's offer
    other_user = User(
        id=2,
        email="other@example.com",
        username="otheruser",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0
    )
    session.add(other_user)
    
    offer = Offer(
        creator_id=2,  # Different user
        title="Other's Offer",
        description="Test",
        is_remote=True,
        status=OfferStatus.ACTIVE
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    # Try to update
    response = client.patch(
        f"/api/v1/offers/{offer.id}",
        headers=auth_headers,
        json={"title": "Hacked Title"}
    )
    
    assert response.status_code == 403


def test_pagination(client: TestClient, session: Session):
    """Test pagination of offer list."""
    user_id = 1
    
    # Create multiple offers
    for i in range(15):
        offer = Offer(
            creator_id=user_id,
            title=f"Offer {i}",
            description="Test",
            is_remote=True,
            status=OfferStatus.ACTIVE
        )
        session.add(offer)
    session.commit()
    
    # Test pagination
    response = client.get("/api/v1/offers/?skip=0&limit=10")
    data = response.json()
    
    assert len(data["items"]) == 10
    assert data["total"] >= 15
    assert data["skip"] == 0
    assert data["limit"] == 10
    
    # Test second page
    response = client.get("/api/v1/offers/?skip=10&limit=10")
    data = response.json()
    
    assert len(data["items"]) >= 5
