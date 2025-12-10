"""
Tests for notification system.
# SRS FR-N: Notification system tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime

from app.main import app
from app.core.db import get_session
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.participant import Participant, ParticipantStatus, ParticipantRole
from app.models.notification import Notification, NotificationType
from app.core.notifications import (
    notify_application_received,
    notify_application_accepted,
    notify_exchange_completed,
    notify_rating_received,
)


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory database for testing."""
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
    """Create test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_users")
def test_users_fixture(session: Session):
    """Create test users."""
    users = []
    for i, username in enumerate(["alice", "bob", "carol"], start=1):
        user = User(
            email=f"{username}@example.com",
            username=username,
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oDWKZVzZVJ0G",
            full_name=f"Test {username.title()}",
            role=UserRole.USER,
            balance=5.0,
        )
        session.add(user)
        users.append(user)
    
    session.commit()
    for user in users:
        session.refresh(user)
    
    return users


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_users):
    """Create auth headers for first test user (alice)."""
    token = create_access_token({"sub": str(test_users[0].id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="test_offer")
def test_offer_fixture(session: Session, test_users):
    """Create test offer."""
    offer = Offer(
        title="Test Offer",
        description="Test description",
        duration_hours=2.0,
        creator_id=test_users[0].id,  # alice
        capacity=3,
        accepted_count=0,
        status=OfferStatus.ACTIVE,
        is_remote=True,
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


@pytest.fixture(name="test_need")
def test_need_fixture(session: Session, test_users):
    """Create test need."""
    need = Need(
        title="Test Need",
        description="Test description",
        duration_hours=2.0,
        creator_id=test_users[0].id,  # alice
        capacity=2,
        accepted_count=0,
        status=NeedStatus.ACTIVE,
        is_remote=True,
    )
    session.add(need)
    session.commit()
    session.refresh(need)
    return need


def test_list_notifications_empty(client: TestClient, auth_headers):
    """Test listing notifications when none exist."""
    response = client.get("/api/v1/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert data["notifications"] == []


def test_create_notification_helper(session: Session, test_users):
    """Test notification creation helper function."""
    alice = test_users[0]
    
    notification = Notification(
        user_id=alice.id,
        type=NotificationType.APPLICATION_RECEIVED,
        title="Test Notification",
        message="Test message",
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    assert notification.id is not None
    assert notification.user_id == alice.id
    assert notification.type == NotificationType.APPLICATION_RECEIVED
    assert notification.is_read is False
    assert notification.read_at is None


def test_list_notifications_with_data(client: TestClient, session: Session, test_users, auth_headers):
    """Test listing notifications with data."""
    alice = test_users[0]
    
    # Create multiple notifications
    for i in range(3):
        notification = Notification(
            user_id=alice.id,
            type=NotificationType.APPLICATION_RECEIVED,
            title=f"Notification {i}",
            message=f"Message {i}",
        )
        session.add(notification)
    
    session.commit()
    
    response = client.get("/api/v1/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["unread_count"] == 3
    assert len(data["notifications"]) == 3


def test_mark_notification_as_read(client: TestClient, session: Session, test_users, auth_headers):
    """Test marking a notification as read."""
    alice = test_users[0]
    
    notification = Notification(
        user_id=alice.id,
        type=NotificationType.APPLICATION_RECEIVED,
        title="Test",
        message="Test message",
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    # Mark as read
    response = client.post(
        f"/api/v1/notifications/{notification.id}/read",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["read_at"] is not None


def test_mark_notification_as_read_already_read(client: TestClient, session: Session, test_users, auth_headers):
    """Test marking an already read notification."""
    alice = test_users[0]
    
    notification = Notification(
        user_id=alice.id,
        type=NotificationType.APPLICATION_RECEIVED,
        title="Test",
        message="Test message",
        is_read=True,
        read_at=datetime.utcnow(),
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    # Mark as read again (should be idempotent)
    response = client.post(
        f"/api/v1/notifications/{notification.id}/read",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True


def test_mark_notification_as_read_not_found(client: TestClient, auth_headers):
    """Test marking a non-existent notification."""
    response = client.post(
        "/api/v1/notifications/99999/read",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_mark_notification_as_read_wrong_user(client: TestClient, session: Session, test_users):
    """Test marking another user's notification."""
    alice = test_users[0]
    bob = test_users[1]
    
    notification = Notification(
        user_id=alice.id,
        type=NotificationType.APPLICATION_RECEIVED,
        title="Test",
        message="Test message",
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    # Try to mark as read with bob's token
    bob_token = create_access_token({"sub": str(bob.id)})
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    
    response = client.post(
        f"/api/v1/notifications/{notification.id}/read",
        headers=bob_headers
    )
    assert response.status_code == 403


def test_mark_all_as_read(client: TestClient, session: Session, test_users, auth_headers):
    """Test marking all notifications as read."""
    alice = test_users[0]
    
    # Create multiple unread notifications
    for i in range(5):
        notification = Notification(
            user_id=alice.id,
            type=NotificationType.APPLICATION_RECEIVED,
            title=f"Notification {i}",
            message=f"Message {i}",
        )
        session.add(notification)
    
    session.commit()
    
    # Mark all as read
    response = client.post("/api/v1/notifications/read-all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["marked_read"] == 5
    
    # Verify all are read
    response = client.get("/api/v1/notifications", headers=auth_headers)
    data = response.json()
    assert data["unread_count"] == 0
    for notif in data["notifications"]:
        assert notif["is_read"] is True


def test_notification_pagination(client: TestClient, session: Session, test_users, auth_headers):
    """Test notification pagination."""
    alice = test_users[0]
    
    # Create 10 notifications
    for i in range(10):
        notification = Notification(
            user_id=alice.id,
            type=NotificationType.APPLICATION_RECEIVED,
            title=f"Notification {i}",
            message=f"Message {i}",
        )
        session.add(notification)
    
    session.commit()
    
    # Get first page
    response = client.get("/api/v1/notifications?skip=0&limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["notifications"]) == 5
    
    # Get second page
    response = client.get("/api/v1/notifications?skip=5&limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["notifications"]) == 5


def test_notification_filter_unread_only(client: TestClient, session: Session, test_users, auth_headers):
    """Test filtering for unread notifications only."""
    alice = test_users[0]
    
    # Create mix of read and unread
    for i in range(3):
        notification = Notification(
            user_id=alice.id,
            type=NotificationType.APPLICATION_RECEIVED,
            title=f"Unread {i}",
            message=f"Message {i}",
            is_read=False,
        )
        session.add(notification)
    
    for i in range(2):
        notification = Notification(
            user_id=alice.id,
            type=NotificationType.APPLICATION_RECEIVED,
            title=f"Read {i}",
            message=f"Message {i}",
            is_read=True,
            read_at=datetime.utcnow(),
        )
        session.add(notification)
    
    session.commit()
    
    # Filter unread only
    response = client.get("/api/v1/notifications?unread_only=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["unread_count"] == 3
    assert len(data["notifications"]) == 3


def test_notify_application_received(session: Session, test_users, test_offer):
    """Test application received notification."""
    alice = test_users[0]  # offer creator
    bob = test_users[1]    # applicant
    
    # Create participant (application)
    participant = Participant(
        offer_id=test_offer.id,
        user_id=bob.id,
        role=ParticipantRole.PROVIDER,
        status=ParticipantStatus.PENDING,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    # Notify offer creator
    notify_application_received(
        session=session,
        offer_creator_id=alice.id,
        applicant_username=bob.username,
        offer_title=test_offer.title,
        offer_id=test_offer.id,
        participant_id=participant.id,
    )
    
    # Check notification was created
    notifications = session.query(Notification).filter(
        Notification.user_id == alice.id
    ).all()
    assert len(notifications) == 1
    assert notifications[0].type == NotificationType.APPLICATION_RECEIVED
    assert bob.username in notifications[0].message
    assert test_offer.title in notifications[0].message


def test_notify_application_accepted(session: Session, test_users, test_offer):
    """Test application accepted notification."""
    alice = test_users[0]  # offer creator
    bob = test_users[1]    # applicant
    
    # Create accepted participant
    participant = Participant(
        offer_id=test_offer.id,
        user_id=bob.id,
        role=ParticipantRole.PROVIDER,
        status=ParticipantStatus.ACCEPTED,
        hours_contributed=2.0,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    # Notify applicant
    notify_application_accepted(
        session=session,
        applicant_id=bob.id,
        offer_title=test_offer.title,
        offer_id=test_offer.id,
        participant_id=participant.id,
    )
    
    # Check notification was created
    notifications = session.query(Notification).filter(
        Notification.user_id == bob.id
    ).all()
    assert len(notifications) == 1
    assert notifications[0].type == NotificationType.APPLICATION_ACCEPTED
    assert test_offer.title in notifications[0].message


def test_notify_exchange_completed(session: Session, test_users, test_offer):
    """Test exchange completed notification."""
    alice = test_users[0]  # offer creator
    bob = test_users[1]    # provider
    
    # Create completed participant
    participant = Participant(
        offer_id=test_offer.id,
        user_id=bob.id,
        role=ParticipantRole.PROVIDER,
        status=ParticipantStatus.COMPLETED,
        hours_contributed=2.0,
        provider_confirmed=True,
        requester_confirmed=True,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    # Notify both parties
    notify_exchange_completed(
        session=session,
        user_id=alice.id,
        other_party_username=bob.username,
        offer_title=test_offer.title,
        offer_id=test_offer.id,
        participant_id=participant.id,
    )
    
    notify_exchange_completed(
        session=session,
        user_id=bob.id,
        other_party_username=alice.username,
        offer_title=test_offer.title,
        offer_id=test_offer.id,
        participant_id=participant.id,
    )
    
    # Check notifications were created
    alice_notifications = session.query(Notification).filter(
        Notification.user_id == alice.id
    ).all()
    assert len(alice_notifications) == 1
    assert alice_notifications[0].type == NotificationType.EXCHANGE_COMPLETED
    
    bob_notifications = session.query(Notification).filter(
        Notification.user_id == bob.id
    ).all()
    assert len(bob_notifications) == 1
    assert bob_notifications[0].type == NotificationType.EXCHANGE_COMPLETED


def test_notify_exchange_awaiting_confirmation(session: Session, test_users, test_offer):
    """Test exchange awaiting confirmation notification."""
    alice = test_users[0]  # offer creator/requester
    bob = test_users[1]    # provider
    
    # Create participant with provider confirmed, requester not confirmed
    participant = Participant(
        offer_id=test_offer.id,
        user_id=bob.id,
        role=ParticipantRole.PROVIDER,
        status=ParticipantStatus.ACCEPTED,
        hours_contributed=2.0,
        provider_confirmed=True,
        requester_confirmed=False,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    
    # Notify requester (alice) that provider (bob) confirmed
    from app.core.notifications import notify_exchange_awaiting_confirmation
    notify_exchange_awaiting_confirmation(
        session=session,
        user_id=alice.id,
        other_party_username=bob.username,
        offer_title=test_offer.title,
        offer_id=test_offer.id,
        participant_id=participant.id,
    )
    
    # Check notification was created
    notifications = session.query(Notification).filter(
        Notification.user_id == alice.id
    ).all()
    assert len(notifications) == 1
    assert notifications[0].type == NotificationType.EXCHANGE_AWAITING_CONFIRMATION
    assert bob.username in notifications[0].message
    assert "confirm" in notifications[0].message.lower()


def test_notify_rating_received(session: Session, test_users):
    """Test rating received notification."""
    alice = test_users[0]
    bob = test_users[1]
    
    # Notify that bob rated alice
    notify_rating_received(
        session=session,
        rated_user_id=alice.id,
        rater_username=bob.username,
        rating_value=4.5,
        rating_id=1,
    )
    
    # Check notification was created
    notifications = session.query(Notification).filter(
        Notification.user_id == alice.id
    ).all()
    assert len(notifications) == 1
    assert notifications[0].type == NotificationType.RATING_RECEIVED
    assert bob.username in notifications[0].message
    assert "4.5" in notifications[0].message


def test_notification_related_entities(session: Session, test_users, test_offer):
    """Test notification with related entities."""
    alice = test_users[0]
    bob = test_users[1]
    
    notification = Notification(
        user_id=alice.id,
        type=NotificationType.APPLICATION_RECEIVED,
        title="Application",
        message="Bob applied",
        related_offer_id=test_offer.id,
        related_user_id=bob.id,
        related_participant_id=1,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    
    assert notification.related_offer_id == test_offer.id
    assert notification.related_user_id == bob.id
    assert notification.related_participant_id == 1


def test_notification_types(session: Session, test_users):
    """Test all notification types can be created."""
    alice = test_users[0]
    
    types = [
        NotificationType.APPLICATION_RECEIVED,
        NotificationType.APPLICATION_ACCEPTED,
        NotificationType.APPLICATION_DECLINED,
        NotificationType.PARTICIPANT_CANCELLED,
        NotificationType.EXCHANGE_AWAITING_CONFIRMATION,
        NotificationType.EXCHANGE_COMPLETED,
        NotificationType.RATING_RECEIVED,
    ]
    
    for notification_type in types:
        notification = Notification(
            user_id=alice.id,
            type=notification_type,
            title=f"Test {notification_type}",
            message=f"Test message for {notification_type}",
        )
        session.add(notification)
    
    session.commit()
    
    notifications = session.query(Notification).filter(
        Notification.user_id == alice.id
    ).all()
    assert len(notifications) == len(types)


def test_notification_unauthorized(client: TestClient):
    """Test accessing notifications without authentication."""
    response = client.get("/api/v1/notifications")
    assert response.status_code == 401


def test_notification_ordering(client: TestClient, session: Session, test_users, auth_headers):
    """Test notifications are ordered by creation time (newest first)."""
    alice = test_users[0]
    
    # Create notifications with slight delays
    import time
    for i in range(3):
        notification = Notification(
            user_id=alice.id,
            type=NotificationType.APPLICATION_RECEIVED,
            title=f"Notification {i}",
            message=f"Message {i}",
        )
        session.add(notification)
        session.commit()
        if i < 2:
            time.sleep(0.01)  # Small delay to ensure different timestamps
    
    response = client.get("/api/v1/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Verify ordering (newest first)
    notifications = data["notifications"]
    assert notifications[0]["title"] == "Notification 2"
    assert notifications[1]["title"] == "Notification 1"
    assert notifications[2]["title"] == "Notification 0"
