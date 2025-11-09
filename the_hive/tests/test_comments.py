"""
Tests for comment system.

Covers:
- FR-10.1: Comments only after completed exchange
- FR-10.2: Basic content moderation
- FR-10.3: Comments visible on profiles
"""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.core.moderation import check_profanity, check_spam_patterns, moderate_content, sanitize_content
from app.main import app
from app.core.db import get_session
from app.models.comment import Comment
from app.models.need import Need, NeedStatus
from app.models.offer import Offer, OfferStatus
from app.models.participant import Participant, ParticipantRole, ParticipantStatus
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
    """Create a test client with the test database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def provider(session: Session) -> User:
    """Create a provider user."""
    user = User(
        email="provider@test.com",
        username="provider",
        password_hash="hashed",
        full_name="Provider User",
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def requester(session: Session) -> User:
    """Create a requester user."""
    user = User(
        email="requester@test.com",
        username="requester",
        password_hash="hashed",
        full_name="Requester User",
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def third_party(session: Session) -> User:
    """Create a third party user not involved in the exchange."""
    user = User(
        email="third@test.com",
        username="thirdparty",
        password_hash="hashed",
        full_name="Third Party",
        balance=5.0,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def completed_exchange(
    session: Session, provider: User, requester: User
) -> Participant:
    """Create a completed exchange between provider and requester."""
    # Requester creates an offer (wants service)
    offer = Offer(
        title="Test Service",
        description="Test service description",
        creator_id=requester.id,
        capacity=1,
        accepted_count=1,
        status=OfferStatus.ACTIVE,
    )
    session.add(offer)
    session.commit()
    
    # Provider accepts and completes
    participant = Participant(
        user_id=provider.id,
        offer_id=offer.id,
        role=ParticipantRole.PROVIDER,
        hours_contributed=3.0,
        status=ParticipantStatus.COMPLETED,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


@pytest.fixture
def pending_exchange(
    session: Session, provider: User, requester: User
) -> Participant:
    """Create a pending (not completed) exchange."""
    offer = Offer(
        title="Pending Service",
        description="Not yet completed",
        creator_id=requester.id,
        capacity=1,
        accepted_count=1,
        status=OfferStatus.ACTIVE,
    )
    session.add(offer)
    session.commit()
    
    participant = Participant(
        user_id=provider.id,
        offer_id=offer.id,
        role=ParticipantRole.PROVIDER,
        hours_contributed=2.0,
        status=ParticipantStatus.ACCEPTED,  # Not COMPLETED
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


# ===== Content Moderation Tests =====

def test_check_profanity_clean_text():
    """Test profanity check with clean text."""
    has_profanity, words = check_profanity("This is a great service!")
    assert has_profanity is False
    assert len(words) == 0


def test_check_profanity_contains_profanity():
    """Test profanity check with inappropriate content."""
    has_profanity, words = check_profanity("This is spam and fake")
    assert has_profanity is True
    assert "spam" in words
    assert "fake" in words


def test_check_spam_patterns_clean():
    """Test spam pattern check with clean text."""
    has_spam, patterns = check_spam_patterns("Great work, very professional")
    assert has_spam is False


def test_check_spam_patterns_contains_url():
    """Test spam pattern detection for URLs."""
    has_spam, patterns = check_spam_patterns("Visit http://example.com for more")
    assert has_spam is True


def test_check_spam_patterns_contains_phone():
    """Test spam pattern detection for phone numbers."""
    has_spam, patterns = check_spam_patterns("Call 555-1234 now")
    assert has_spam is True


def test_moderate_content_valid():
    """Test content moderation with valid content."""
    is_approved, reason = moderate_content("Excellent service, very professional and helpful!")
    assert is_approved is True
    assert reason == ""


def test_moderate_content_too_short():
    """Test content moderation rejects too short content."""
    is_approved, reason = moderate_content("Good")
    assert is_approved is False
    assert "too short" in reason.lower()


def test_moderate_content_profanity():
    """Test content moderation rejects profanity."""
    is_approved, reason = moderate_content("This is spam and fake content")
    assert is_approved is False
    assert "inappropriate language" in reason.lower()


def test_moderate_content_excessive_caps():
    """Test content moderation rejects excessive capitalization."""
    is_approved, reason = moderate_content("THIS IS ALL CAPS AND VERY ANNOYING!!!")
    assert is_approved is False
    assert "capital letters" in reason.lower()


def test_moderate_content_excessive_repetition():
    """Test content moderation rejects excessive character repetition."""
    is_approved, reason = moderate_content("Greeeeeeat service!!!!!!!")
    assert is_approved is False
    assert "repetition" in reason.lower()


def test_sanitize_content():
    """Test content sanitization."""
    text = "  Multiple   spaces   and\n\n\n\nmultiple newlines  "
    sanitized = sanitize_content(text)
    assert sanitized == "Multiple spaces and\n\nmultiple newlines"


# ===== Comment API Tests =====

def test_create_comment_on_completed_exchange(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """
    Test FR-10.1: Can create comment after completed exchange.
    """
    # Provider comments on requester's profile
    # Login as provider
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    response = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "Great experience! Very professional and punctual.",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["from_user_id"] == provider.id
    assert data["to_user_id"] == requester.id
    assert "Great experience" in data["content"]
    
    # Verify comment in database
    comment = session.get(Comment, data["id"])
    assert comment is not None
    assert comment.from_user_id == provider.id
    assert comment.to_user_id == requester.id


def test_cannot_comment_on_pending_exchange(
    client: TestClient,
    provider: User,
    requester: User,
    pending_exchange: Participant
):
    """
    Test FR-10.1: Cannot comment on exchanges that are not completed.
    """
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    response = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": pending_exchange.id,
            "content": "Trying to comment before completion",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "completed" in response.json()["detail"].lower()


def test_cannot_comment_as_non_participant(
    client: TestClient,
    requester: User,
    third_party: User,
    completed_exchange: Participant
):
    """
    Test FR-10.1: Non-participants cannot comment.
    """
    from app.core.security import create_access_token
    token = create_access_token({"sub": third_party.id, "username": third_party.username, "role": "user"})
    
    response = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "Trying to comment as non-participant",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "participated" in response.json()["detail"].lower()


def test_cannot_comment_on_self(
    client: TestClient,
    provider: User,
    completed_exchange: Participant
):
    """Test that users cannot comment on their own profile."""
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    response = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": provider.id,  # Same as commenter
            "participant_id": completed_exchange.id,
            "content": "Trying to comment on myself",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Returns 403 because exchange verification fails first
    assert response.status_code == 403
    assert "participated" in response.json()["detail"].lower() or "own profile" in response.json()["detail"].lower()


def test_cannot_duplicate_comment(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """Test that users cannot comment twice on the same exchange."""
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    # First comment succeeds
    response1 = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "First comment on this exchange",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 201
    
    # Second comment fails
    response2 = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "Trying to comment again",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 400
    assert "already commented" in response2.json()["detail"].lower()


def test_content_moderation_rejects_profanity(
    client: TestClient,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """
    Test FR-10.2: Content moderation rejects inappropriate content.
    """
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    response = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "This was spam and fake service",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "rejected" in response.json()["detail"].lower()


def test_content_moderation_rejects_too_short(
    client: TestClient,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """
    Test FR-10.2: Content moderation rejects too short comments.
    """
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    response = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "Good",  # Too short
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Pydantic validator catches this before the endpoint, returns 422
    assert response.status_code == 422
    assert "detail" in response.json()


def test_get_user_comments_public_visibility(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """
    Test FR-10.3: Comments are publicly visible on user profiles.
    """
    # Create a comment
    comment = Comment(
        from_user_id=provider.id,
        to_user_id=requester.id,
        participant_id=completed_exchange.id,
        content="Excellent service, highly recommend!",
        is_moderated=True,
        is_approved=True,
        is_visible=True,
    )
    session.add(comment)
    session.commit()
    
    # Anyone can view (no authentication required)
    response = client.get(f"/api/v1/comments/user/{requester.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["to_user_id"] == requester.id
    assert "Excellent service" in data["items"][0]["content"]


def test_get_user_comments_excludes_flagged(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """Test that flagged comments are excluded by default."""
    # Create approved comment
    approved = Comment(
        from_user_id=provider.id,
        to_user_id=requester.id,
        participant_id=completed_exchange.id,
        content="Great service!",
        is_moderated=True,
        is_approved=True,
        is_visible=True,
    )
    session.add(approved)
    
    # Create flagged comment
    flagged = Comment(
        from_user_id=provider.id,
        to_user_id=requester.id,
        participant_id=completed_exchange.id,
        content="This is spam content",
        is_moderated=True,
        is_approved=False,
        is_visible=True,
    )
    session.add(flagged)
    session.commit()
    
    # Get comments (should exclude flagged)
    response = client.get(f"/api/v1/comments/user/{requester.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Great service" in data["items"][0]["content"]


def test_get_user_comments_pagination(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """Test comment pagination."""
    # Create multiple comments
    for i in range(5):
        comment = Comment(
            from_user_id=provider.id,
            to_user_id=requester.id,
            participant_id=completed_exchange.id,
            content=f"Comment {i} about the service",
            is_moderated=True,
            is_approved=True,
            is_visible=True,
        )
        session.add(comment)
    session.commit()
    
    # Get first page
    response1 = client.get(f"/api/v1/comments/user/{requester.id}?skip=0&limit=3")
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["items"]) == 3
    assert data1["total"] == 5
    
    # Get second page
    response2 = client.get(f"/api/v1/comments/user/{requester.id}?skip=3&limit=3")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 2


def test_get_my_comments(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """Test getting comments written by current user."""
    # Create a comment
    comment = Comment(
        from_user_id=provider.id,
        to_user_id=requester.id,
        participant_id=completed_exchange.id,
        content="My comment on the exchange",
        is_moderated=True,
        is_approved=True,
        is_visible=True,
    )
    session.add(comment)
    session.commit()
    
    # Get as provider
    from app.core.security import create_access_token
    token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    
    response = client.get(
        "/api/v1/comments/my-comments",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["from_user_id"] == provider.id
    assert "My comment" in data["items"][0]["content"]


def test_bidirectional_comments(
    client: TestClient,
    session: Session,
    provider: User,
    requester: User,
    completed_exchange: Participant
):
    """Test that both parties can comment on each other."""
    from app.core.security import create_access_token
    
    # Provider comments on requester
    provider_token = create_access_token({"sub": provider.id, "username": provider.username, "role": "user"})
    response1 = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": requester.id,
            "participant_id": completed_exchange.id,
            "content": "Requester was very clear about expectations",
        },
        headers={"Authorization": f"Bearer {provider_token}"}
    )
    assert response1.status_code == 201
    
    # Requester comments on provider
    requester_token = create_access_token({"sub": requester.id, "username": requester.username, "role": "user"})
    response2 = client.post(
        "/api/v1/comments",
        json={
            "recipient_id": provider.id,
            "participant_id": completed_exchange.id,
            "content": "Provider delivered excellent service",
        },
        headers={"Authorization": f"Bearer {requester_token}"}
    )
    assert response2.status_code == 201
    
    # Verify both comments exist
    requester_comments = client.get(f"/api/v1/comments/user/{requester.id}")
    provider_comments = client.get(f"/api/v1/comments/user/{provider.id}")
    
    assert requester_comments.json()["total"] == 1
    assert provider_comments.json()["total"] == 1
