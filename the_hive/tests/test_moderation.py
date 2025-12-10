"""
Tests for moderation system: reports and moderation actions.

SRS Requirements:
- FR-11.1: Users can report inappropriate content
- FR-11.2: Moderators review reports and take action
- FR-11.3: Moderators can remove inappropriate content
- FR-11.4: Reports and resolutions are logged
- FR-11.5: Moderators can suspend or ban users
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.models.offer import Offer, OfferStatus
from app.models.need import Need, NeedStatus
from app.models.forum import ForumComment, ForumTopic, TopicType
from app.models.report import Report, ReportStatus, ReportReason, ReportAction


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
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role=UserRole.USER,
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
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}



def test_user_can_report_user(client: TestClient, session: Session, test_user: User, auth_headers: dict):
    """Test FR-11.1: Users can report other users."""
    # Create another user to report
    reported_user = User(
        email="reported@test.com",
        username="reported",
        password_hash="hash",
        full_name="Reported User",
    )
    session.add(reported_user)
    session.commit()
    session.refresh(reported_user)
    
    # Submit report
    response = client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "reported_user_id": reported_user.id,
            "reason": "harassment",
            "description": "User sent harassing messages",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["reporter"]["username"] == test_user.username
    assert data["reported_item"]["type"] == "user"
    assert data["reported_item"]["id"] == reported_user.id
    assert data["reason"] == "harassment"
    assert data["status"] == "pending"


def test_user_can_report_offer(client: TestClient, session: Session, test_user: User, auth_headers: dict):
    """Test FR-11.1: Users can report offers."""
    # Create offer to report
    creator = User(
        email="creator@test.com",
        username="creator",
        password_hash="hash",
    )
    session.add(creator)
    session.commit()
    
    offer = Offer(
        title="Scam Offer",
        description="This is a scam",
        creator_id=creator.id,
        hours_required=5.0,
        capacity=1,
        is_remote=True,
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    # Report offer
    response = client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "reported_offer_id": offer.id,
            "reason": "scam",
            "description": "This offer is asking for money upfront",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["reported_item"]["type"] == "offer"
    assert data["reported_item"]["title"] == "Scam Offer"
    assert data["reason"] == "scam"


def test_user_can_report_need(client: TestClient, session: Session, test_user: User, auth_headers: dict):
    """Test FR-11.1: Users can report needs."""
    # Create need to report
    creator = User(
        email="creator@test.com",
        username="creator",
        password_hash="hash",
    )
    session.add(creator)
    session.commit()
    
    need = Need(
        title="Inappropriate Need",
        description="This violates policy",
        creator_id=creator.id,
        hours_offered=3.0,
        capacity=1,
        is_remote=True,
    )
    session.add(need)
    session.commit()
    session.refresh(need)
    
    # Report need
    response = client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "reported_need_id": need.id,
            "reason": "inappropriate",
            "description": "This content is not appropriate",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["reported_item"]["type"] == "need"
    assert data["reason"] == "inappropriate"


def test_user_can_report_comment(client: TestClient, session: Session, test_user: User, auth_headers: dict):
    """Test FR-11.1: Users can report forum comments."""
    # Create topic and comment
    creator = User(
        email="creator@test.com",
        username="creator",
        password_hash="hash",
    )
    session.add(creator)
    session.commit()
    
    topic = ForumTopic(
        topic_type=TopicType.DISCUSSION,
        creator_id=creator.id,
        title="Test Topic",
        content="Test content",
    )
    session.add(topic)
    session.commit()
    
    comment = ForumComment(
        topic_id=topic.id,
        author_id=creator.id,
        content="Spam comment with links",
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    # Report comment
    response = client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "reported_comment_id": comment.id,
            "reason": "spam",
            "description": "Comment contains spam links",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["reported_item"]["type"] == "comment"
    assert data["reason"] == "spam"


def test_cannot_report_without_item(client: TestClient, auth_headers: dict):
    """Test that exactly one item must be reported."""
    response = client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "reason": "spam",
            "description": "No item specified",
        },
    )
    
    assert response.status_code == 400
    assert "Exactly one reported item" in response.json()["detail"]


def test_cannot_self_report(client: TestClient, session: Session, test_user: User, auth_headers: dict):
    """Test that users cannot report themselves."""
    response = client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "reported_user_id": test_user.id,
            "reason": "other",
            "description": "Reporting myself",
        },
    )
    
    assert response.status_code == 400
    assert "cannot report yourself" in response.json()["detail"]


def test_moderator_can_list_reports(client: TestClient, session: Session, test_user: User):
    """Test FR-11.2: Moderators can list and review reports."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(test_user.id)
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create some reports
    reporter = User(
        email="reporter@test.com",
        username="reporter",
        password_hash="hash",
    )
    reported = User(
        email="reported@test.com",
        username="reported",
        password_hash="hash",
    )
    session.add_all([reporter, reported])
    session.commit()
    
    report1 = Report(
        reporter_id=reporter.id,
        reported_user_id=reported.id,
        reason=ReportReason.SPAM,
        description="Spam user",
    )
    report2 = Report(
        reporter_id=reporter.id,
        reported_user_id=reported.id,
        reason=ReportReason.HARASSMENT,
        description="Harassment",
        status=ReportStatus.UNDER_REVIEW,
    )
    session.add_all([report1, report2])
    session.commit()
    
    # List all reports
    response = client.get("/api/v1/reports/", headers=mod_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["pending_count"] == 1
    assert data["under_review_count"] == 1
    assert len(data["reports"]) == 2


def test_moderator_can_filter_reports(client: TestClient, session: Session, test_user: User):
    """Test FR-11.2: Moderators can filter reports by status and reason."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create reports with different statuses and reasons
    reporter = User(email="reporter@test.com", username="reporter", password_hash="hash")
    reported = User(email="reported@test.com", username="reported", password_hash="hash")
    session.add_all([reporter, reported])
    session.commit()
    
    reports = [
        Report(reporter_id=reporter.id, reported_user_id=reported.id, reason=ReportReason.SPAM, status=ReportStatus.PENDING),
        Report(reporter_id=reporter.id, reported_user_id=reported.id, reason=ReportReason.SPAM, status=ReportStatus.RESOLVED),
        Report(reporter_id=reporter.id, reported_user_id=reported.id, reason=ReportReason.HARASSMENT, status=ReportStatus.PENDING),
    ]
    session.add_all(reports)
    session.commit()
    
    # Filter by status
    response = client.get("/api/v1/reports/?status_filter=pending", headers=mod_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 2
    
    # Filter by reason
    response = client.get("/api/v1/reports/?reason_filter=spam", headers=mod_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 2
    
    # Filter by both
    response = client.get("/api/v1/reports/?status_filter=pending&reason_filter=spam", headers=mod_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_moderator_can_get_report_stats(client: TestClient, session: Session, test_user: User):
    """Test FR-11.2: Moderators can view report statistics."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create various reports
    reporter = User(email="reporter@test.com", username="reporter", password_hash="hash")
    reported_user = User(email="reported@test.com", username="reported", password_hash="hash")
    session.add_all([reporter, reported_user])
    session.commit()
    
    creator = User(email="creator@test.com", username="creator", password_hash="hash")
    session.add(creator)
    session.commit()
    
    offer = Offer(title="Test", description="Test", creator_id=creator.id, hours_required=1.0, capacity=1, is_remote=True)
    session.add(offer)
    session.commit()
    
    reports = [
        Report(reporter_id=reporter.id, reported_user_id=reported_user.id, reason=ReportReason.SPAM),
        Report(reporter_id=reporter.id, reported_user_id=reported_user.id, reason=ReportReason.SPAM),
        Report(reporter_id=reporter.id, reported_offer_id=offer.id, reason=ReportReason.SCAM),
    ]
    session.add_all(reports)
    session.commit()
    
    # Get stats
    response = client.get("/api/v1/reports/stats", headers=mod_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_reports"] == 3
    assert data["spam_reports"] == 2
    assert data["scam_reports"] == 1
    assert data["user_reports"] == 2
    assert data["offer_reports"] == 1


def test_moderator_can_resolve_report(client: TestClient, session: Session, test_user: User):
    """Test FR-11.2: Moderators can update and resolve reports."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(test_user.id)
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create report
    reporter = User(email="reporter@test.com", username="reporter", password_hash="hash")
    reported = User(email="reported@test.com", username="reported", password_hash="hash")
    session.add_all([reporter, reported])
    session.commit()
    
    report = Report(
        reporter_id=reporter.id,
        reported_user_id=reported.id,
        reason=ReportReason.SPAM,
        description="Spam behavior",
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    
    # Resolve report
    response = client.put(
        f"/api/v1/reports/{report.id}",
        headers=mod_headers,
        json={
            "status": "resolved",
            "moderator_action": "user_suspended",
            "moderator_notes": "User suspended for 7 days",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["moderator_action"] == "user_suspended"
    assert data["moderator"]["id"] == test_user.id
    assert data["resolved_at"] is not None


def test_moderator_can_remove_offer(client: TestClient, session: Session, test_user: User):
    """Test FR-11.3: Moderators can remove inappropriate offers."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create offer
    creator = User(email="creator@test.com", username="creator", password_hash="hash")
    session.add(creator)
    session.commit()
    
    offer = Offer(
        title="Inappropriate Offer",
        description="Violates policy",
        creator_id=creator.id,
        hours_required=5.0,
        capacity=1,
        is_remote=True,
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    
    # Remove offer
    response = client.delete(
        f"/api/v1/moderation/offers/{offer.id}",
        headers=mod_headers,
    )
    
    assert response.status_code == 204
    
    # Verify offer is archived
    session.refresh(offer)
    assert offer.status == OfferStatus.CANCELLED
    assert offer.archived_at is not None


def test_moderator_can_remove_need(client: TestClient, session: Session, test_user: User):
    """Test FR-11.3: Moderators can remove inappropriate needs."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create need
    creator = User(email="creator@test.com", username="creator", password_hash="hash")
    session.add(creator)
    session.commit()
    
    need = Need(
        title="Inappropriate Need",
        description="Violates policy",
        creator_id=creator.id,
        hours_offered=3.0,
        capacity=1,
        is_remote=True,
    )
    session.add(need)
    session.commit()
    session.refresh(need)
    
    # Remove need
    response = client.delete(
        f"/api/v1/moderation/needs/{need.id}",
        headers=mod_headers,
    )
    
    assert response.status_code == 204
    
    # Verify need is archived
    session.refresh(need)
    assert need.status == NeedStatus.CANCELLED
    assert need.archived_at is not None


def test_moderator_can_remove_comment(client: TestClient, session: Session, test_user: User):
    """Test FR-11.3: Moderators can remove inappropriate comments."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create comment
    creator = User(email="creator@test.com", username="creator", password_hash="hash")
    session.add(creator)
    session.commit()
    
    topic = ForumTopic(
        topic_type=TopicType.DISCUSSION,
        creator_id=creator.id,
        title="Test",
        content="Test",
    )
    session.add(topic)
    session.commit()
    
    comment = ForumComment(
        topic_id=topic.id,
        author_id=creator.id,
        content="Inappropriate comment",
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    # Remove comment
    response = client.delete(
        f"/api/v1/moderation/comments/{comment.id}",
        headers=mod_headers,
    )
    
    assert response.status_code == 204
    
    # Verify comment is soft-deleted
    session.refresh(comment)
    assert comment.is_deleted is True
    assert comment.deleted_at is not None


def test_moderator_can_suspend_user(client: TestClient, session: Session, test_user: User):
    """Test FR-11.5: Moderators can suspend users temporarily."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create user to suspend
    target_user = User(
        email="target@test.com",
        username="target",
        password_hash="hash",
    )
    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    
    # Suspend user
    response = client.put(
        f"/api/v1/moderation/users/{target_user.id}/suspend",
        headers=mod_headers,
        json={
            "reason": "Repeated policy violations",
            "duration_days": 7,
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_suspended"] is True
    
    # Verify in database
    session.refresh(target_user)
    assert target_user.is_suspended is True
    assert target_user.suspended_at is not None
    assert target_user.suspended_until is not None
    assert target_user.suspension_reason == "Repeated policy violations"


def test_moderator_can_ban_user(client: TestClient, session: Session, test_user: User):
    """Test FR-11.5: Moderators can permanently ban users."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create user to ban
    target_user = User(
        email="target@test.com",
        username="target",
        password_hash="hash",
    )
    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    
    # Ban user
    response = client.put(
        f"/api/v1/moderation/users/{target_user.id}/ban",
        headers=mod_headers,
        json={"reason": "Severe violations"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_banned"] is True
    
    # Verify in database
    session.refresh(target_user)
    assert target_user.is_banned is True
    assert target_user.banned_at is not None
    assert target_user.ban_reason == "Severe violations"


def test_cannot_suspend_moderator(client: TestClient, session: Session, test_user: User):
    """Test that moderators cannot suspend other moderators."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create another moderator
    other_mod = User(
        email="mod@test.com",
        username="othermod",
        password_hash="hash",
        role=UserRole.MODERATOR,
    )
    session.add(other_mod)
    session.commit()
    
    # Try to suspend
    response = client.put(
        f"/api/v1/moderation/users/{other_mod.id}/suspend",
        headers=mod_headers,
        json={"reason": "Test", "duration_days": 7},
    )
    
    assert response.status_code == 403
    assert "Cannot suspend moderators" in response.json()["detail"]


def test_cannot_self_suspend(client: TestClient, session: Session, test_user: User):
    """Test that moderators cannot suspend themselves."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Try to self-suspend
    response = client.put(
        f"/api/v1/moderation/users/{test_user.id}/suspend",
        headers=mod_headers,
        json={"reason": "Test", "duration_days": 7},
    )
    
    assert response.status_code == 403
    # Since test_user is a moderator, it hits the "Cannot suspend moderators" check first
    assert "Cannot suspend moderators" in response.json()["detail"]


def test_moderator_can_unsuspend_user(client: TestClient, session: Session, test_user: User):
    """Test FR-11.5: Moderators can lift suspensions."""
    # Make test_user a moderator
    test_user.role = UserRole.MODERATOR
    session.add(test_user)
    session.commit()
    
    mod_token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username, "role": test_user.role.value}
    )
    mod_headers = {"Authorization": f"Bearer {mod_token}"}
    
    # Create suspended user
    target_user = User(
        email="target@test.com",
        username="target",
        password_hash="hash",
        is_suspended=True,
        suspended_at=datetime.utcnow(),
        suspended_until=datetime.utcnow() + timedelta(days=7),
        suspension_reason="Test",
    )
    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    
    # Unsuspend
    response = client.put(
        f"/api/v1/moderation/users/{target_user.id}/unsuspend",
        headers=mod_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_suspended"] is False
    
    # Verify in database
    session.refresh(target_user)
    assert target_user.is_suspended is False
    assert target_user.suspended_at is None


def test_regular_user_cannot_access_moderation(client: TestClient, auth_headers: dict):
    """Test that regular users cannot access moderation endpoints."""
    # Try to list reports
    response = client.get("/api/v1/reports/", headers=auth_headers)
    assert response.status_code == 403
    
    # Try to remove content
    response = client.delete("/api/v1/moderation/offers/1", headers=auth_headers)
    assert response.status_code == 403
    
    # Try to suspend user
    response = client.put("/api/v1/moderation/users/1/suspend", headers=auth_headers, json={"reason": "Test", "duration_days": 7})
    assert response.status_code == 403
