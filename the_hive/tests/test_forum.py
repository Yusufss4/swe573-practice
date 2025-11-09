"""
Tests for forum system.

Covers:
- FR-15: Basic forum with moderation hooks
- FR-15.1: Create/list topics (types: discussion, event)
- FR-15.2: Search by tag/keyword
- FR-15.3: Link optional Offer/Need to events
- FR-15.4: Events ordered by recency
- FR-15.5: Links visible both ways (bidirectional)
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.core.security import create_access_token, get_password_hash
from app.models.forum import ForumComment, ForumTopic, ForumTopicTag, TopicType
from app.models.need import Need, NeedStatus
from app.models.offer import Offer, OfferStatus
from app.models.tag import Tag
from app.models.user import User, UserRole


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
    """Create a test client with the test database."""
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
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def other_user(session: Session) -> User:
    """Create another test user."""
    user = User(
        email="other@test.com",
        username="otheruser",
        password_hash=get_password_hash("password123"),
        full_name="Other User",
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(user: User) -> dict:
    """Create authentication headers for test user."""
    token = create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_user: User) -> dict:
    """Create authentication headers for other user."""
    token = create_access_token(
        data={"sub": other_user.id, "username": other_user.username, "role": other_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_offer(session: Session, user: User) -> Offer:
    """Create a sample offer."""
    offer = Offer(
        title="Python Tutoring",
        description="Learn Python programming",
        creator_id=user.id,
        capacity=1,
        accepted_count=0,
        status=OfferStatus.ACTIVE,
        is_remote=True,
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


@pytest.fixture
def sample_need(session: Session, user: User) -> Need:
    """Create a sample need."""
    need = Need(
        title="Garden Help",
        description="Need help with gardening",
        creator_id=user.id,
        capacity=1,
        accepted_count=0,
        status=NeedStatus.ACTIVE,
        is_remote=False,
        location_name="Brooklyn, NY",
    )
    session.add(need)
    session.commit()
    session.refresh(need)
    return need


# Topic Creation Tests (FR-15.1)

def test_create_discussion_topic(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test creating a discussion topic (FR-15.1)."""
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Best practices for timebanking",
            "content": "What are your experiences with timebanking?",
            "tags": ["general", "discussion"]
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["topic_type"] == "discussion"
    assert data["title"] == "Best practices for timebanking"
    assert data["creator_id"] == user.id
    assert "general" in data["tags"]
    assert "discussion" in data["tags"]
    assert data["is_visible"] == True


def test_create_event_topic(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test creating an event topic (FR-15.1)."""
    start_time = datetime.utcnow() + timedelta(days=7)
    end_time = start_time + timedelta(hours=2)
    
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Community Garden Meetup",
            "content": "Let's meet to organize the community garden!",
            "tags": ["event", "gardening"],
            "event_start_time": start_time.isoformat(),
            "event_end_time": end_time.isoformat(),
            "event_location": "Central Park"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["topic_type"] == "event"
    assert data["event_location"] == "Central Park"
    assert data["event_start_time"] is not None
    assert data["event_end_time"] is not None


def test_create_topic_invalid_type(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test creating topic with invalid type."""
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "invalid",
            "title": "Test",
            "content": "Test content"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


# Linking Tests (FR-15.3, FR-15.5)

def test_link_offer_to_event(
    client: TestClient, session: Session, user: User, auth_headers: dict, sample_offer: Offer
):
    """Test linking an offer to an event topic (FR-15.3)."""
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Python Workshop",
            "content": "Join us for a Python programming workshop!",
            "tags": ["workshop", "python"],
            "linked_offer_id": sample_offer.id
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["linked_offer_id"] == sample_offer.id
    assert data["linked_item"] is not None
    assert data["linked_item"]["type"] == "offer"
    assert data["linked_item"]["title"] == sample_offer.title


def test_link_need_to_event(
    client: TestClient, session: Session, user: User, auth_headers: dict, sample_need: Need
):
    """Test linking a need to an event topic (FR-15.3)."""
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Garden Work Day",
            "content": "Let's work on the garden together!",
            "tags": ["gardening"],
            "linked_need_id": sample_need.id
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["linked_need_id"] == sample_need.id
    assert data["linked_item"] is not None
    assert data["linked_item"]["type"] == "need"


def test_cannot_link_both_offer_and_need(
    client: TestClient, session: Session, user: User, auth_headers: dict,
    sample_offer: Offer, sample_need: Need
):
    """Test that a topic cannot link both offer and need."""
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Test Event",
            "content": "This should fail",
            "linked_offer_id": sample_offer.id,
            "linked_need_id": sample_need.id
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


def test_bidirectional_links(
    client: TestClient, session: Session, user: User, auth_headers: dict, sample_offer: Offer
):
    """Test bidirectional links - topics linking to offer are visible from offer (FR-15.5)."""
    # Create topic linking to offer
    response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Python Workshop",
            "content": "Workshop based on this offer",
            "linked_offer_id": sample_offer.id
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    topic_id = response.json()["id"]
    
    # Get topics linking to this offer (bidirectional)
    response = client.get(
        f"/api/v1/forum/topics/{sample_offer.id}/linked-from?item_type=offer"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == topic_id
    assert data["items"][0]["linked_offer_id"] == sample_offer.id


# List and Filter Tests (FR-15.2, FR-15.4)

def test_list_topics(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test listing forum topics."""
    # Create multiple topics
    for i in range(3):
        client.post(
            "/api/v1/forum/topics",
            json={
                "topic_type": "discussion",
                "title": f"Topic {i}",
                "content": f"This is content for topic {i}"
            },
            headers=auth_headers
        )
    
    # List all topics
    response = client.get("/api/v1/forum/topics")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_filter_by_topic_type(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test filtering topics by type (FR-15.2)."""
    # Create discussion
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Discussion",
            "content": "A discussion topic"
        },
        headers=auth_headers
    )
    
    # Create event
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Event",
            "content": "An event topic"
        },
        headers=auth_headers
    )
    
    # Filter for discussions only
    response = client.get("/api/v1/forum/topics?topic_type=discussion")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["topic_type"] == "discussion"
    
    # Filter for events only
    response = client.get("/api/v1/forum/topics?topic_type=event")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["topic_type"] == "event"


def test_search_by_keyword(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test searching topics by keyword (FR-15.2)."""
    # Create topics with different content
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Python Programming",
            "content": "Let's discuss Python"
        },
        headers=auth_headers
    )
    
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Gardening Tips",
            "content": "Share your gardening experiences"
        },
        headers=auth_headers
    )
    
    # Search for "python"
    response = client.get("/api/v1/forum/topics?keyword=python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Python" in data["items"][0]["title"]


def test_filter_by_tags(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test filtering topics by tags (FR-15.2)."""
    # Create topics with different tags
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Python Topic",
            "content": "About Python",
            "tags": ["python", "programming"]
        },
        headers=auth_headers
    )
    
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Garden Topic",
            "content": "About gardening",
            "tags": ["gardening", "nature"]
        },
        headers=auth_headers
    )
    
    # Filter by python tag
    response = client.get("/api/v1/forum/topics?tags=python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "python" in data["items"][0]["tags"]


def test_events_ordered_by_recency(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test that events are ordered by recency (FR-15.4)."""
    # Create topics with delays to ensure different timestamps
    import time
    
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "First Event",
            "content": "This is the oldest event"
        },
        headers=auth_headers
    )
    
    time.sleep(0.1)
    
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Second Event",
            "content": "This is the middle event"
        },
        headers=auth_headers
    )
    
    time.sleep(0.1)
    
    client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "event",
            "title": "Third Event",
            "content": "This is the newest event"
        },
        headers=auth_headers
    )
    
    # List events
    response = client.get("/api/v1/forum/topics?topic_type=event")
    assert response.status_code == 200
    data = response.json()
    
    # Should be ordered newest first
    assert data["items"][0]["title"] == "Third Event"
    assert data["items"][1]["title"] == "Second Event"
    assert data["items"][2]["title"] == "First Event"


# Topic CRUD Tests

def test_get_topic(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test getting a single topic."""
    # Create topic
    create_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test Topic",
            "content": "Test content"
        },
        headers=auth_headers
    )
    topic_id = create_response.json()["id"]
    
    # Get topic
    response = client.get(f"/api/v1/forum/topics/{topic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == topic_id
    assert data["title"] == "Test Topic"
    # View count should increment
    assert data["view_count"] == 1


def test_update_topic(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test updating a topic."""
    # Create topic
    create_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Original Title",
            "content": "Original content",
            "tags": ["original"]
        },
        headers=auth_headers
    )
    topic_id = create_response.json()["id"]
    
    # Update topic
    response = client.patch(
        f"/api/v1/forum/topics/{topic_id}",
        json={
            "title": "Updated Title",
            "content": "Updated content",
            "tags": ["updated", "new"]
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"
    assert "updated" in data["tags"]
    assert "new" in data["tags"]


def test_only_creator_can_update(
    client: TestClient, session: Session, user: User, other_user: User,
    auth_headers: dict, other_auth_headers: dict
):
    """Test that only creator can update a topic."""
    # User creates topic
    create_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test",
            "content": "Test content here"
        },
        headers=auth_headers
    )
    topic_id = create_response.json()["id"]
    
    # Other user tries to update
    response = client.patch(
        f"/api/v1/forum/topics/{topic_id}",
        json={"title": "Hacked"},
        headers=other_auth_headers
    )
    
    assert response.status_code == 403


def test_delete_topic(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test soft-deleting a topic."""
    # Create topic
    create_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "To be deleted",
            "content": "This will be deleted"
        },
        headers=auth_headers
    )
    topic_id = create_response.json()["id"]
    
    # Delete topic
    response = client.delete(
        f"/api/v1/forum/topics/{topic_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Topic should not appear in list
    response = client.get("/api/v1/forum/topics")
    data = response.json()
    assert all(item["id"] != topic_id for item in data["items"])


# Comment Tests

def test_create_comment(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test creating a comment on a topic."""
    # Create topic
    topic_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test Topic",
            "content": "Test content"
        },
        headers=auth_headers
    )
    topic_id = topic_response.json()["id"]
    
    # Create comment
    response = client.post(
        f"/api/v1/forum/topics/{topic_id}/comments",
        json={"content": "Great topic!"},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Great topic!"
    assert data["author_id"] == user.id
    assert data["topic_id"] == topic_id


def test_list_comments(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test listing comments for a topic."""
    # Create topic
    topic_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test",
            "content": "Test content for comments"
        },
        headers=auth_headers
    )
    topic_id = topic_response.json()["id"]
    
    # Create multiple comments
    for i in range(3):
        client.post(
            f"/api/v1/forum/topics/{topic_id}/comments",
            json={"content": f"Comment {i}"},
            headers=auth_headers
        )
    
    # List comments
    response = client.get(f"/api/v1/forum/topics/{topic_id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_update_comment(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test updating a comment."""
    # Create topic and comment
    topic_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test",
            "content": "Test content for updating comments"
        },
        headers=auth_headers
    )
    topic_id = topic_response.json()["id"]
    
    comment_response = client.post(
        f"/api/v1/forum/topics/{topic_id}/comments",
        json={"content": "Original comment"},
        headers=auth_headers
    )
    comment_id = comment_response.json()["id"]
    
    # Update comment
    response = client.patch(
        f"/api/v1/forum/comments/{comment_id}",
        json={"content": "Updated comment"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated comment"


def test_delete_comment(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test deleting a comment."""
    # Create topic and comment
    topic_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test",
            "content": "Test content for deleting comments"
        },
        headers=auth_headers
    )
    topic_id = topic_response.json()["id"]
    
    comment_response = client.post(
        f"/api/v1/forum/topics/{topic_id}/comments",
        json={"content": "To be deleted"},
        headers=auth_headers
    )
    comment_id = comment_response.json()["id"]
    
    # Delete comment
    response = client.delete(
        f"/api/v1/forum/comments/{comment_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Comment should not appear in list
    response = client.get(f"/api/v1/forum/topics/{topic_id}/comments")
    data = response.json()
    assert all(item["id"] != comment_id for item in data["items"])


def test_comment_count_increments(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test that topic comment count increments when comments are added."""
    # Create topic
    topic_response = client.post(
        "/api/v1/forum/topics",
        json={
            "topic_type": "discussion",
            "title": "Test",
            "content": "Test content for comment count"
        },
        headers=auth_headers
    )
    topic_id = topic_response.json()["id"]
    initial_count = topic_response.json()["comment_count"]
    assert initial_count == 0
    
    # Add comment
    client.post(
        f"/api/v1/forum/topics/{topic_id}/comments",
        json={"content": "First comment"},
        headers=auth_headers
    )
    
    # Check count increased
    response = client.get(f"/api/v1/forum/topics/{topic_id}")
    assert response.json()["comment_count"] == 1


def test_pagination(
    client: TestClient, session: Session, user: User, auth_headers: dict
):
    """Test pagination of topic list."""
    # Create 25 topics
    for i in range(25):
        client.post(
            "/api/v1/forum/topics",
            json={
                "topic_type": "discussion",
                "title": f"Topic {i}",
                "content": f"This is content for topic number {i}"
            },
            headers=auth_headers
        )
    
    # Get first page
    response = client.get("/api/v1/forum/topics?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25
    assert len(data["items"]) == 10
    assert data["skip"] == 0
    assert data["limit"] == 10
    
    # Get second page
    response = client.get("/api/v1/forum/topics?skip=10&limit=10")
    data = response.json()
    assert len(data["items"]) == 10
    
    # Get third page
    response = client.get("/api/v1/forum/topics?skip=20&limit=10")
    data = response.json()
    assert len(data["items"]) == 5  # Only 5 remaining
