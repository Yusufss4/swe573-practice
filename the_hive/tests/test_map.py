"""Tests for Map Feed API.

SRS Requirements:
- FR-9: Map view for discovering offers/needs
- FR-9.1: Display with approximate locations
- FR-9.2: Filter by tags
- FR-9.3: Sort by distance
- NFR-7: Privacy - approximate coordinates only
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.tag import Tag
from app.models.associations import OfferTag, NeedTag
from app.api.map import haversine_distance, approximate_coordinate


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
def user(session: Session) -> User:
    """Create a test user."""
    user = User(
        email="user@test.com",
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
def tags(session: Session) -> dict[str, Tag]:
    """Create test tags."""
    python_tag = Tag(name="python")
    cooking_tag = Tag(name="cooking")
    gardening_tag = Tag(name="gardening")
    
    session.add_all([python_tag, cooking_tag, gardening_tag])
    session.commit()
    session.refresh(python_tag)
    session.refresh(cooking_tag)
    session.refresh(gardening_tag)
    
    return {
        "python": python_tag,
        "cooking": cooking_tag,
        "gardening": gardening_tag,
    }


# ============================================================================
# Privacy Tests (SRS NFR-7)
# ============================================================================

def test_approximate_coordinate_rounds_to_two_decimals():
    """Test that coordinates are rounded to 2 decimal places (~1km precision)."""
    exact_lat = 40.123456
    approx_lat = approximate_coordinate(exact_lat)
    
    assert approx_lat == 40.12
    assert approx_lat != exact_lat


def test_map_feed_returns_approximate_coords_not_exact(
    client: TestClient, session: Session, user: User
):
    """Test that map feed never returns exact coordinates (FR-9, NFR-7)."""
    # Create offer with exact coordinates
    exact_lat = 40.7589123
    exact_lon = -73.9851456
    
    offer = Offer(
        title="Test Offer",
        description="Test",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=exact_lat,
        location_lon=exact_lon,
        location_name="Brooklyn, NY",
    )
    session.add(offer)
    session.commit()
    
    # Get map feed
    response = client.get("/api/v1/map/feed")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    
    pin = data["items"][0]
    assert pin["approximate_lat"] == 40.76  # Rounded
    assert pin["approximate_lon"] == -73.99  # Rounded
    assert pin["approximate_lat"] != exact_lat
    assert pin["approximate_lon"] != exact_lon


def test_map_feed_never_exposes_exact_location(
    client: TestClient, session: Session, user: User
):
    """Test privacy protection - exact locations never in response."""
    offer = Offer(
        title="Secret Location",
        description="Test",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.758896,
        location_lon=-73.985130,
        location_name="Near Empire State Building",
    )
    session.add(offer)
    session.commit()
    
    response = client.get("/api/v1/map/feed")
    
    assert response.status_code == 200
    data = response.json()
    pin = data["items"][0]
    
    # Check that only approximate coords and name are returned
    assert "approximate_lat" in pin
    assert "approximate_lon" in pin
    assert "location_name" in pin
    # Ensure no exact coords in response
    response_str = response.text
    assert "40.758896" not in response_str
    assert "-73.985130" not in response_str


# ============================================================================
# Distance Calculation Tests (FR-9.3)
# ============================================================================

def test_haversine_distance_calculation():
    """Test Haversine formula for distance calculation."""
    # New York to Los Angeles (approximate)
    ny_lat, ny_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437
    
    distance = haversine_distance(ny_lat, ny_lon, la_lat, la_lon)
    
    # Should be approximately 3944 km
    assert 3900 < distance < 4000


def test_map_feed_calculates_distance_when_user_location_provided(
    client: TestClient, session: Session, user: User
):
    """Test distance calculation from user location (FR-9.3)."""
    # User in Manhattan
    user_lat, user_lon = 40.7589, -73.9851
    
    # Offer in Brooklyn (about 8km away)
    offer = Offer(
        title="Brooklyn Offer",
        description="Test",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.6782,
        location_lon=-73.9442,
        location_name="Brooklyn, NY",
    )
    session.add(offer)
    session.commit()
    
    # Get map feed with user location
    response = client.get(
        f"/api/v1/map/feed?user_lat={user_lat}&user_lon={user_lon}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    
    pin = data["items"][0]
    assert pin["distance_km"] is not None
    # Distance should be around 9-10 km
    assert 9 < pin["distance_km"] < 11


def test_map_feed_sorts_by_distance(
    client: TestClient, session: Session, user: User
):
    """Test that results are sorted by distance when user location provided."""
    user_lat, user_lon = 40.7589, -73.9851  # Manhattan
    
    # Create offers at different distances
    near_offer = Offer(
        title="Near Offer",
        description="Close by",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.7600,  # Very close
        location_lon=-73.9860,
    )
    
    far_offer = Offer(
        title="Far Offer",
        description="Far away",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.6782,  # Brooklyn - farther
        location_lon=-73.9442,
    )
    
    session.add_all([far_offer, near_offer])  # Add in reverse order
    session.commit()
    
    # Get map feed with user location
    response = client.get(
        f"/api/v1/map/feed?user_lat={user_lat}&user_lon={user_lon}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    
    # Check sorting - nearest first
    assert data["items"][0]["title"] == "Near Offer"
    assert data["items"][1]["title"] == "Far Offer"
    assert data["items"][0]["distance_km"] < data["items"][1]["distance_km"]


def test_map_feed_remote_items_have_no_distance(
    client: TestClient, session: Session, user: User
):
    """Test that remote items don't have distance calculated."""
    user_lat, user_lon = 40.7589, -73.9851
    
    remote_offer = Offer(
        title="Remote Offer",
        description="Work from anywhere",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        is_remote=True,
        location_lat=None,
        location_lon=None,
    )
    session.add(remote_offer)
    session.commit()
    
    response = client.get(
        f"/api/v1/map/feed?user_lat={user_lat}&user_lon={user_lon}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    
    pin = data["items"][0]
    assert pin["is_remote"] is True
    assert pin["distance_km"] is None
    assert pin["approximate_lat"] is None
    assert pin["approximate_lon"] is None


def test_map_feed_remote_items_sorted_last(
    client: TestClient, session: Session, user: User
):
    """Test that remote items appear after local items in sorted results."""
    user_lat, user_lon = 40.7589, -73.9851
    
    local_offer = Offer(
        title="Local Offer",
        description="In person",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.7600,
        location_lon=-73.9860,
    )
    
    remote_offer = Offer(
        title="Remote Offer",
        description="Online",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        is_remote=True,
    )
    
    session.add_all([remote_offer, local_offer])
    session.commit()
    
    response = client.get(
        f"/api/v1/map/feed?user_lat={user_lat}&user_lon={user_lon}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    
    # Local items first, remote last
    assert data["items"][0]["title"] == "Local Offer"
    assert data["items"][1]["title"] == "Remote Offer"


# ============================================================================
# Filtering Tests (FR-9.2)
# ============================================================================

def test_map_feed_returns_only_active_items(
    client: TestClient, session: Session, user: User
):
    """Test that only ACTIVE offers/needs are returned."""
    active_offer = Offer(
        title="Active Offer",
        description="Active",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    
    expired_offer = Offer(
        title="Expired Offer",
        description="Expired",
        creator_id=user.id,
        status=OfferStatus.EXPIRED,
        capacity=1,
        accepted_count=0,
    )
    
    completed_offer = Offer(
        title="Completed Offer",
        description="Completed",
        creator_id=user.id,
        status=OfferStatus.COMPLETED,
        capacity=1,
        accepted_count=1,
    )
    
    session.add_all([active_offer, expired_offer, completed_offer])
    session.commit()
    
    response = client.get("/api/v1/map/feed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Active Offer"


def test_map_feed_filters_by_tags(
    client: TestClient, session: Session, user: User, tags: dict
):
    """Test filtering by tags (FR-9.2)."""
    # Create offers with different tags
    python_offer = Offer(
        title="Python Tutoring",
        description="Learn Python",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    session.add(python_offer)
    session.commit()
    
    python_tag_assoc = OfferTag(offer_id=python_offer.id, tag_id=tags["python"].id)
    session.add(python_tag_assoc)
    
    cooking_offer = Offer(
        title="Cooking Class",
        description="Learn to cook",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    session.add(cooking_offer)
    session.commit()
    
    cooking_tag_assoc = OfferTag(offer_id=cooking_offer.id, tag_id=tags["cooking"].id)
    session.add(cooking_tag_assoc)
    session.commit()
    
    # Filter by python tag
    response = client.get("/api/v1/map/feed?tags=python")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Tutoring"
    assert "python" in data["items"][0]["tags"]


def test_map_feed_filters_by_multiple_tags(
    client: TestClient, session: Session, user: User, tags: dict
):
    """Test filtering by multiple tags (OR logic)."""
    # Python offer
    python_offer = Offer(
        title="Python",
        description="Python",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    session.add(python_offer)
    session.commit()
    session.add(OfferTag(offer_id=python_offer.id, tag_id=tags["python"].id))
    
    # Cooking offer
    cooking_offer = Offer(
        title="Cooking",
        description="Cooking",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    session.add(cooking_offer)
    session.commit()
    session.add(OfferTag(offer_id=cooking_offer.id, tag_id=tags["cooking"].id))
    
    # Gardening offer
    gardening_offer = Offer(
        title="Gardening",
        description="Gardening",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    session.add(gardening_offer)
    session.commit()
    session.add(OfferTag(offer_id=gardening_offer.id, tag_id=tags["gardening"].id))
    session.commit()
    
    # Filter by python and cooking
    response = client.get("/api/v1/map/feed?tags=python,cooking")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    titles = {item["title"] for item in data["items"]}
    assert "Python" in titles
    assert "Cooking" in titles
    assert "Gardening" not in titles


# ============================================================================
# Integration Tests
# ============================================================================

def test_map_feed_includes_both_offers_and_needs(
    client: TestClient, session: Session, user: User
):
    """Test that map feed includes both offers and needs."""
    offer = Offer(
        title="Test Offer",
        description="Offer",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.7589,
        location_lon=-73.9851,
    )
    
    need = Need(
        title="Test Need",
        description="Need",
        creator_id=user.id,
        status=NeedStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.7600,
        location_lon=-73.9860,
    )
    
    session.add_all([offer, need])
    session.commit()
    
    response = client.get("/api/v1/map/feed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    
    types = {item["type"] for item in data["items"]}
    assert "offer" in types
    assert "need" in types


def test_map_feed_pagination(
    client: TestClient, session: Session, user: User
):
    """Test pagination of map feed results."""
    # Create 10 offers
    for i in range(10):
        offer = Offer(
            title=f"Offer {i}",
            description="Test",
            creator_id=user.id,
            status=OfferStatus.ACTIVE,
            capacity=1,
            accepted_count=0,
        )
        session.add(offer)
    session.commit()
    
    # Get first page
    response = client.get("/api/v1/map/feed?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 5
    assert data["skip"] == 0
    assert data["limit"] == 5
    
    # Get second page
    response = client.get("/api/v1/map/feed?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 5
    assert data["skip"] == 5


def test_map_feed_response_includes_user_location(
    client: TestClient, session: Session, user: User
):
    """Test that response includes user location used for sorting."""
    user_lat, user_lon = 40.7589, -73.9851
    
    offer = Offer(
        title="Test",
        description="Test",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
    )
    session.add(offer)
    session.commit()
    
    response = client.get(
        f"/api/v1/map/feed?user_lat={user_lat}&user_lon={user_lon}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_lat"] == user_lat
    assert data["user_lon"] == user_lon


def test_map_feed_works_without_user_location(
    client: TestClient, session: Session, user: User
):
    """Test that map feed works without user location (no distance sorting)."""
    offer = Offer(
        title="Test Offer",
        description="Test",
        creator_id=user.id,
        status=OfferStatus.ACTIVE,
        capacity=1,
        accepted_count=0,
        location_lat=40.7589,
        location_lon=-73.9851,
    )
    session.add(offer)
    session.commit()
    
    response = client.get("/api/v1/map/feed")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["user_lat"] is None
    assert data["user_lon"] is None
    assert data["items"][0]["distance_km"] is None
