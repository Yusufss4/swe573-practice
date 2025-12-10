"""
Tests for the rating system.
# SRS FR-9: User Rating System
# SRS FR-9.1: Users can rate each other after completing an exchange
# SRS FR-9.2: Ratings include three required categories (reliability, kindness, helpfulness)
#            General rating is calculated from these three
# SRS FR-9.3: Blind ratings - visible only after both users submit or deadline passes
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.db import get_session
from app.core.security import create_access_token
from app.main import app
from app.models.need import Need
from app.models.offer import Offer
from app.models.participant import Participant, ParticipantRole, ParticipantStatus
from app.models.rating import Rating, RatingVisibility
from app.models.user import User


# --- Fixtures ---
@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
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


@pytest.fixture(name="provider_user")
def provider_user_fixture(session: Session) -> User:
    """Create a provider user for testing."""
    user = User(
        email="provider@example.com",
        username="provider",
        password_hash="hashed",
        full_name="Provider User",
        is_active=True,
        balance=5.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="requester_user")
def requester_user_fixture(session: Session) -> User:
    """Create a requester user for testing."""
    user = User(
        email="requester@example.com",
        username="requester",
        password_hash="hashed",
        full_name="Requester User",
        is_active=True,
        balance=5.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="completed_offer_participant")
def completed_offer_participant_fixture(
    session: Session, provider_user: User, requester_user: User
) -> tuple[Offer, Participant]:
    """Create a completed offer with participant for rating tests."""
    offer = Offer(
        title="Test Service Offer",
        description="A test service",
        creator_id=provider_user.id,
        hours=2.0,
        status="ACTIVE",
        is_remote=True,
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)

    participant = Participant(
        offer_id=offer.id,
        user_id=requester_user.id,
        role=ParticipantRole.REQUESTER,
        status=ParticipantStatus.COMPLETED,
        provider_confirmed=True,
        requester_confirmed=True,
    )
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return offer, participant


@pytest.fixture(name="provider_headers")
def provider_headers_fixture(provider_user: User) -> dict:
    """Create auth headers for provider user."""
    token = create_access_token(
        data={"sub": str(provider_user.id), "username": provider_user.username, "role": provider_user.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="requester_headers")
def requester_headers_fixture(requester_user: User) -> dict:
    """Create auth headers for requester user."""
    token = create_access_token(
        data={"sub": str(requester_user.id), "username": requester_user.username, "role": requester_user.role}
    )
    return {"Authorization": f"Bearer {token}"}


# --- Rating Creation Tests ---
class TestCreateRating:
    """Tests for rating creation endpoint."""

    def test_create_rating_with_all_categories(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test creating a rating with all three required category ratings."""
        # SRS FR-9.2: All three category ratings are required
        # General rating is calculated as the average
        _, participant = completed_offer_participant

        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 4,
                "helpfulness_rating": 5,
            },
        )

        assert response.status_code == 201
        data = response.json()
        # General rating should be calculated as round((5+4+5)/3) = round(4.67) = 5
        assert data["general_rating"] == 5
        assert data["reliability_rating"] == 5
        assert data["kindness_rating"] == 4
        assert data["helpfulness_rating"] == 5

    def test_create_rating_with_all_categories_and_comment(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test creating a rating with all category ratings and public comment."""
        _, participant = completed_offer_participant

        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 4,
                "kindness_rating": 4,
                "helpfulness_rating": 4,
                "public_comment": "Great experience working together!",
            },
        )

        assert response.status_code == 201
        data = response.json()
        # General rating should be calculated as round((4+4+4)/3) = 4
        assert data["general_rating"] == 4
        assert data["reliability_rating"] == 4
        assert data["kindness_rating"] == 4
        assert data["helpfulness_rating"] == 4
        # Note: public_comment visibility depends on blind rating rules

    def test_create_rating_missing_required_category(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that missing required category ratings fails validation."""
        _, participant = completed_offer_participant

        # Missing kindness_rating
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "helpfulness_rating": 5,
            },
        )

        assert response.status_code == 422  # Validation error

    def test_create_rating_invalid_category_rating(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that category ratings must be 1-5."""
        _, participant = completed_offer_participant

        # Rating too low
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 0,
                "kindness_rating": 3,
                "helpfulness_rating": 3,
            },
        )
        assert response.status_code == 422

        # Rating too high
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 6,
                "kindness_rating": 3,
                "helpfulness_rating": 3,
            },
        )
        assert response.status_code == 422

    def test_cannot_rate_invalid_recipient(
        self,
        client: TestClient,
        provider_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that users can only rate the other party in the exchange."""
        _, participant = completed_offer_participant

        # Provider trying to rate themselves
        response = client.post(
            "/api/v1/ratings/",
            headers=provider_headers,
            json={
                "recipient_id": provider_user.id,  # Trying to rate self
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )

        assert response.status_code == 400
        assert "invalid recipient" in response.json()["detail"].lower()

    def test_cannot_rate_incomplete_exchange(
        self,
        client: TestClient,
        session: Session,
        requester_headers: dict,
        provider_user: User,
        requester_user: User,
    ):
        """Test that ratings cannot be submitted for incomplete exchanges."""
        # Create an offer with ACCEPTED (not COMPLETED) participant
        offer = Offer(
            title="Incomplete Offer",
            description="Not yet completed",
            creator_id=provider_user.id,
            hours=1.0,
            status="ACTIVE",
            is_remote=True,
        )
        session.add(offer)
        session.commit()
        session.refresh(offer)

        participant = Participant(
            offer_id=offer.id,
            user_id=requester_user.id,
            role=ParticipantRole.REQUESTER,
            status=ParticipantStatus.ACCEPTED,  # Not completed
        )
        session.add(participant)
        session.commit()
        session.refresh(participant)

        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )

        assert response.status_code == 400
        # User must confirm completion before rating
        assert "confirm" in response.json()["detail"].lower()

    def test_cannot_rate_twice(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that users cannot submit multiple ratings for the same exchange."""
        _, participant = completed_offer_participant

        # First rating succeeds
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )
        assert response.status_code == 201

        # Second rating fails
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 4,
                "kindness_rating": 4,
                "helpfulness_rating": 4,
            },
        )
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()


# --- Blind Rating Tests ---
class TestBlindRatings:
    """Tests for blind rating visibility system."""

    def test_rating_status_before_submission(
        self,
        client: TestClient,
        requester_headers: dict,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test getting rating status before any ratings submitted."""
        # SRS FR-9.3: Blind ratings status check
        _, participant = completed_offer_participant

        response = client.get(
            f"/api/v1/ratings/status/{participant.id}",
            headers=requester_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["can_submit_rating"] is True
        assert data["has_submitted_rating"] is False
        assert data["other_party_has_rated"] is False
        assert data["is_visible"] is False

    def test_rating_status_after_one_submission(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test rating status after one party submits."""
        _, participant = completed_offer_participant

        # Requester submits rating
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )
        assert response.status_code == 201

        # Check status - should show submitted but not visible
        response = client.get(
            f"/api/v1/ratings/status/{participant.id}",
            headers=requester_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["has_submitted_rating"] is True
        assert data["other_party_has_rated"] is False
        assert data["is_visible"] is False  # Hidden until both rate

    def test_rating_visible_after_both_submit(
        self,
        client: TestClient,
        requester_headers: dict,
        provider_headers: dict,
        provider_user: User,
        requester_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that ratings become visible after both parties submit."""
        # SRS FR-9.3: Blind ratings - visible only after both submit
        _, participant = completed_offer_participant

        # Requester submits rating
        response = client.post(
            "/api/v1/ratings/",
            headers=requester_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )
        assert response.status_code == 201

        # Provider submits rating
        response = client.post(
            "/api/v1/ratings/",
            headers=provider_headers,
            json={
                "recipient_id": requester_user.id,
                "participant_id": participant.id,
                "reliability_rating": 4,
                "kindness_rating": 4,
                "helpfulness_rating": 4,
            },
        )
        assert response.status_code == 201

        # Check status - should now be visible
        response = client.get(
            f"/api/v1/ratings/status/{participant.id}",
            headers=requester_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["both_have_rated"] is True
        assert data["is_visible"] is True


# --- Rating Retrieval Tests ---
class TestGetRatings:
    """Tests for rating retrieval endpoints."""

    def test_get_user_ratings_visible_only(
        self,
        client: TestClient,
        session: Session,
        provider_headers: dict,
        provider_user: User,
        requester_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that only visible ratings are returned in user ratings."""
        _, participant = completed_offer_participant

        # Create a visible rating with all three required categories
        rating = Rating(
            from_user_id=requester_user.id,
            to_user_id=provider_user.id,
            participant_id=participant.id,
            general_rating=5,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=4,
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating)
        session.commit()

        response = client.get(
            f"/api/v1/ratings/user/{provider_user.id}",
            headers=provider_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["general_rating"] == 5

    def test_get_exchange_ratings(
        self,
        client: TestClient,
        session: Session,
        provider_headers: dict,
        provider_user: User,
        requester_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test getting ratings for a specific exchange."""
        _, participant = completed_offer_participant

        # Both users submit ratings (making them visible)
        rating1 = Rating(
            from_user_id=requester_user.id,
            to_user_id=provider_user.id,
            participant_id=participant.id,
            general_rating=5,
            reliability_rating=5,
            kindness_rating=5,
            helpfulness_rating=5,
            visibility=RatingVisibility.VISIBLE,
        )
        rating2 = Rating(
            from_user_id=provider_user.id,
            to_user_id=requester_user.id,
            participant_id=participant.id,
            general_rating=4,
            reliability_rating=4,
            kindness_rating=4,
            helpfulness_rating=4,
            visibility=RatingVisibility.VISIBLE,
        )
        session.add(rating1)
        session.add(rating2)
        session.commit()

        response = client.get(
            f"/api/v1/ratings/exchange/{participant.id}",
            headers=provider_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_hidden_ratings_not_returned(
        self,
        client: TestClient,
        session: Session,
        provider_headers: dict,
        provider_user: User,
        requester_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that hidden ratings are not returned in user ratings."""
        _, participant = completed_offer_participant

        # Create a hidden rating with all three required categories
        rating = Rating(
            from_user_id=requester_user.id,
            to_user_id=provider_user.id,
            participant_id=participant.id,
            general_rating=1,  # Low rating
            reliability_rating=1,
            kindness_rating=1,
            helpfulness_rating=1,
            visibility=RatingVisibility.HIDDEN,  # Hidden
        )
        session.add(rating)
        session.commit()

        response = client.get(
            f"/api/v1/ratings/user/{provider_user.id}",
            headers=provider_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Hidden rating should not be returned
        assert data["total"] == 0


# --- Rating Labels Tests ---
class TestRatingLabels:
    """Tests for rating label endpoint."""

    def test_get_rating_labels(self, client: TestClient):
        """Test getting rating labels and category info."""
        response = client.get("/api/v1/ratings/labels")

        assert response.status_code == 200
        data = response.json()
        assert "rating_labels" in data
        assert "categories" in data
        assert data["rating_labels"]["5"] == "Exceptional"
        # general is no longer a separate category, all three are required
        assert "reliability" in data["categories"]
        assert "kindness" in data["categories"]
        assert "helpfulness" in data["categories"]


# --- Authorization Tests ---
class TestRatingAuthorization:
    """Tests for rating authorization."""

    def test_unauthenticated_cannot_create_rating(
        self,
        client: TestClient,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that unauthenticated users cannot create ratings."""
        _, participant = completed_offer_participant

        response = client.post(
            "/api/v1/ratings/",
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )

        assert response.status_code == 401

    def test_non_participant_cannot_rate(
        self,
        client: TestClient,
        session: Session,
        provider_user: User,
        completed_offer_participant: tuple[Offer, Participant],
    ):
        """Test that only exchange participants can submit ratings."""
        _, participant = completed_offer_participant

        # Create a third user who wasn't part of the exchange
        outsider = User(
            email="outsider@example.com",
            username="outsider",
            password_hash="hashed",
            full_name="Outsider",
            is_active=True,
        )
        session.add(outsider)
        session.commit()
        session.refresh(outsider)

        outsider_token = create_access_token(
            data={"sub": str(outsider.id), "username": outsider.username, "role": outsider.role}
        )
        outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

        response = client.post(
            "/api/v1/ratings/",
            headers=outsider_headers,
            json={
                "recipient_id": provider_user.id,
                "participant_id": participant.id,
                "reliability_rating": 5,
                "kindness_rating": 5,
                "helpfulness_rating": 5,
            },
        )

        assert response.status_code == 403
        # User not involved in exchange
        assert "participated" in response.json()["detail"].lower()
