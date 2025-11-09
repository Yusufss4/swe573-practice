"""
Tests for handshake mechanism endpoints.

SRS Requirements:
- FR-5.1: User can propose help with optional short message
- FR-5.2: Proposal marked as PENDING until explicitly accepted/rejected
- FR-5.3: Once accepted, exchange marked as confirmed/active
- FR-5: Handshake mechanism (pending → accepted workflow)
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
def requester_user(session: Session):
    """Create a requester user (item creator)."""
    user = User(
        email="requester@example.com",
        username="requester",
        password_hash=get_password_hash("password123"),
        full_name="Requester User",
        role=UserRole.USER,
        balance=10.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def proposer_user(session: Session):
    """Create a proposer user (helper)."""
    user = User(
        email="proposer@example.com",
        username="proposer",
        password_hash=get_password_hash("password123"),
        full_name="Proposer User",
        role=UserRole.USER,
        balance=5.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def proposer2_user(session: Session):
    """Create a second proposer user."""
    user = User(
        email="proposer2@example.com",
        username="proposer2",
        password_hash=get_password_hash("password123"),
        full_name="Proposer Two",
        role=UserRole.USER,
        balance=5.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def requester_headers(client: TestClient, requester_user: User):
    """Get authentication headers for requester user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "requester", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def proposer_headers(client: TestClient, proposer_user: User):
    """Get authentication headers for proposer user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "proposer", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def proposer2_headers(client: TestClient, proposer2_user: User):
    """Get authentication headers for proposer2 user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "proposer2", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_propose_help_for_offer(client: TestClient, requester_headers: dict, proposer_headers: dict):
    """Test proposing help for an offer (FR-5.1, FR-5.2)."""
    # Requester creates an offer
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Python Tutoring",
        "description": "Help with Python programming basics",
        "is_remote": True,
        "capacity": 2,
        "tags": ["python", "education"]
    })
    assert response.status_code == 201
    offer_id = response.json()["id"]
    
    # Proposer proposes help with optional message
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={
            "item_type": "offer",
            "item_id": offer_id,
            "message": "I'd love to help with Python tutoring!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["offer_id"] == offer_id
    assert data["status"] == "pending"  # FR-5.2: marked as PENDING (proposed)
    assert data["message"] == "I'd love to help with Python tutoring!"


def test_propose_help_for_need(client: TestClient, requester_headers: dict, proposer_headers: dict):
    """Test proposing help for a need."""
    # Requester creates a need
    response = client.post("/api/v1/needs/", headers=requester_headers, json={
        "title": "Need Python Help",
        "description": "Looking for help with Python project",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "help"]
    })
    assert response.status_code == 201
    need_id = response.json()["id"]
    
    # Proposer proposes help
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={
            "item_type": "need",
            "item_id": need_id,
            "message": "I can help with that!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["need_id"] == need_id
    assert data["status"] == "pending"


def test_propose_without_message(client: TestClient, requester_headers: dict, proposer_headers: dict):
    """Test proposing help without a message (message is optional per FR-5.1)."""
    # Create offer
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Test Offer",
        "description": "Testing proposal without message",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Propose without message
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "offer", "item_id": offer_id}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["message"] is None


def test_accept_handshake_by_requester(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict
):
    """Test accepting a handshake proposal by requester (FR-5.3)."""
    # Requester creates offer
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Test Offer",
        "description": "Testing handshake acceptance workflow",
        "is_remote": True,
        "capacity": 2,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Proposer makes a proposal
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={
            "item_type": "offer",
            "item_id": offer_id,
            "message": "I can help"
        }
    )
    handshake_id = response.json()["id"]
    
    # Requester accepts the handshake
    response = client.post(
        f"/api/v1/handshake/{handshake_id}/accept",
        headers=requester_headers,
        params={"hours": 2.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"  # FR-5.3: marked as accepted
    assert data["hours_contributed"] == 2.5
    
    # Verify offer accepted_count increased
    response = client.get(f"/api/v1/offers/{offer_id}", headers=requester_headers)
    assert response.json()["accepted_count"] == 1
    assert response.json()["status"] == "active"  # Not full yet


def test_only_requester_can_accept(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict,
    proposer2_headers: dict
):
    """Test that only the requester (item creator) can accept proposals."""
    # Requester creates offer
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Test Offer",
        "description": "Testing ownership check for acceptance",
        "is_remote": True,
        "capacity": 2,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Proposer makes a proposal
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={
            "item_type": "offer",
            "item_id": offer_id,
            "message": "I can help"
        }
    )
    handshake_id = response.json()["id"]
    
    # Proposer2 (not the requester) tries to accept
    response = client.post(
        f"/api/v1/handshake/{handshake_id}/accept",
        headers=proposer2_headers,
        params={"hours": 1.0}
    )
    assert response.status_code == 403
    assert "creator" in response.json()["detail"]


def test_cannot_accept_if_full(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict,
    proposer2_headers: dict
):
    """Test that proposals cannot be accepted if capacity is full."""
    # Create offer with capacity 1
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Limited Offer",
        "description": "Testing full capacity constraint",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Two proposers make proposals
    response1 = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "offer", "item_id": offer_id, "message": "Proposer 1"}
    )
    handshake1_id = response1.json()["id"]
    
    response2 = client.post(
        "/api/v1/handshake/propose",
        headers=proposer2_headers,
        params={"item_type": "offer", "item_id": offer_id, "message": "Proposer 2"}
    )
    handshake2_id = response2.json()["id"]
    
    # Requester accepts first proposal (fills capacity)
    response = client.post(
        f"/api/v1/handshake/{handshake1_id}/accept",
        headers=requester_headers,
        params={"hours": 1.0}
    )
    assert response.status_code == 200
    
    # Verify offer is now FULL
    response = client.get(f"/api/v1/offers/{offer_id}", headers=requester_headers)
    assert response.json()["status"] == "full"
    
    # Try to accept second proposal - should fail
    response = client.post(
        f"/api/v1/handshake/{handshake2_id}/accept",
        headers=requester_headers,
        params={"hours": 1.0}
    )
    assert response.status_code == 400
    assert "capacity already reached" in response.json()["detail"]


def test_cannot_propose_if_already_full(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict,
    proposer2_headers: dict
):
    """Test that proposals cannot be made to items that are already full."""
    # Create offer with capacity 1
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Limited Offer",
        "description": "Testing proposal to full item",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Proposer makes proposal
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "offer", "item_id": offer_id}
    )
    handshake_id = response.json()["id"]
    
    # Requester accepts (fills capacity)
    client.post(
        f"/api/v1/handshake/{handshake_id}/accept",
        headers=requester_headers,
        params={"hours": 1.0}
    )
    
    # Proposer2 tries to make a new proposal to the now-full offer
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer2_headers,
        params={"item_type": "offer", "item_id": offer_id}
    )
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_proposer_sees_pending_until_accepted(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict
):
    """Test that proposer can see their pending proposals until accepted."""
    # Create offer
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Test Offer",
        "description": "Testing proposal visibility",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Proposer makes a proposal
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "offer", "item_id": offer_id, "message": "My proposal"}
    )
    handshake_id = response.json()["id"]
    
    # Proposer lists their proposals - should see pending
    response = client.get(
        "/api/v1/handshake/my-proposals",
        headers=proposer_headers,
        params={"status_filter": "pending"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == handshake_id
    assert data["items"][0]["status"] == "pending"
    
    # Requester accepts the proposal
    client.post(
        f"/api/v1/handshake/{handshake_id}/accept",
        headers=requester_headers,
        params={"hours": 1.0}
    )
    
    # Proposer lists pending proposals - should now be empty
    response = client.get(
        "/api/v1/handshake/my-proposals",
        headers=proposer_headers,
        params={"status_filter": "pending"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0
    
    # Proposer lists accepted proposals - should see the accepted one
    response = client.get(
        "/api/v1/handshake/my-proposals",
        headers=proposer_headers,
        params={"status_filter": "accepted"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "accepted"


def test_requester_sees_pending_proposals(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict,
    proposer2_headers: dict
):
    """Test that requester can see pending proposals for their items."""
    # Requester creates offer
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Test Offer",
        "description": "Testing requester's pending view",
        "is_remote": True,
        "capacity": 3,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Two proposers make proposals
    client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "offer", "item_id": offer_id, "message": "Proposer 1"}
    )
    client.post(
        "/api/v1/handshake/propose",
        headers=proposer2_headers,
        params={"item_type": "offer", "item_id": offer_id, "message": "Proposer 2"}
    )
    
    # Requester lists pending proposals for their items
    response = client.get(
        "/api/v1/handshake/pending-for-me",
        headers=requester_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["status"] == "pending" for item in data["items"])


def test_handshake_increments_accepted_count(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict,
    proposer2_headers: dict
):
    """Test that accepting handshakes correctly increments accepted_count."""
    # Create offer with capacity 2
    response = client.post("/api/v1/offers/", headers=requester_headers, json={
        "title": "Test Offer",
        "description": "Testing accepted count increment",
        "is_remote": True,
        "capacity": 2,
        "tags": ["test"]
    })
    offer_id = response.json()["id"]
    
    # Two proposers make proposals
    response1 = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "offer", "item_id": offer_id}
    )
    handshake1_id = response1.json()["id"]
    
    response2 = client.post(
        "/api/v1/handshake/propose",
        headers=proposer2_headers,
        params={"item_type": "offer", "item_id": offer_id}
    )
    handshake2_id = response2.json()["id"]
    
    # Check initial state
    response = client.get(f"/api/v1/offers/{offer_id}", headers=requester_headers)
    assert response.json()["accepted_count"] == 0
    
    # Accept first proposal
    client.post(
        f"/api/v1/handshake/{handshake1_id}/accept",
        headers=requester_headers,
        params={"hours": 1.0}
    )
    
    response = client.get(f"/api/v1/offers/{offer_id}", headers=requester_headers)
    assert response.json()["accepted_count"] == 1
    assert response.json()["status"] == "active"
    
    # Accept second proposal (fills capacity)
    client.post(
        f"/api/v1/handshake/{handshake2_id}/accept",
        headers=requester_headers,
        params={"hours": 1.0}
    )
    
    response = client.get(f"/api/v1/offers/{offer_id}", headers=requester_headers)
    assert response.json()["accepted_count"] == 2
    assert response.json()["status"] == "full"


def test_need_handshake_workflow(
    client: TestClient,
    requester_headers: dict,
    proposer_headers: dict
):
    """Test complete handshake workflow for needs."""
    # Create need
    response = client.post("/api/v1/needs/", headers=requester_headers, json={
        "title": "Need Help",
        "description": "Testing need handshake workflow",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    need_id = response.json()["id"]
    
    # Proposer proposes help
    response = client.post(
        "/api/v1/handshake/propose",
        headers=proposer_headers,
        params={"item_type": "need", "item_id": need_id, "message": "I can help"}
    )
    handshake_id = response.json()["id"]
    assert response.json()["status"] == "pending"
    
    # Requester accepts
    response = client.post(
        f"/api/v1/handshake/{handshake_id}/accept",
        headers=requester_headers,
        params={"hours": 3.0}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    
    # Verify need is marked FULL
    response = client.get(f"/api/v1/needs/{need_id}", headers=requester_headers)
    assert response.json()["status"] == "full"
    assert response.json()["accepted_count"] == 1
