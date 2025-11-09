"""
Tests for search and tag filtering functionality.

SRS Requirements:
- FR-8: Search and discovery with semantic tags
- FR-8.2: Search by tags, type, location
- FR-8.3: Users can create new tags freely
- FR-8.5: Order by distance (placeholder), recency
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


def test_search_empty_database(client: TestClient):
    """Test search with no items."""
    response = client.get("/api/v1/search/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_search_text_query(client: TestClient, auth_headers: dict):
    """Test text search in title and description."""
    # Create offers with different titles
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Python Programming Help",
        "description": "Learn Python basics",
        "is_remote": True,
        "capacity": 1,
        "tags": ["programming"]
    })
    
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "JavaScript Tutoring",
        "description": "Frontend development with React",
        "is_remote": True,
        "capacity": 1,
        "tags": ["programming"]
    })
    
    # Search for "python"
    response = client.get("/api/v1/search/?query=python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Python" in data["items"][0]["title"]


def test_search_by_type_offer(client: TestClient, auth_headers: dict):
    """Test filtering by type: offers only."""
    # Create offer
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Offer Item",
        "description": "This is an offer",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    
    # Create need
    client.post("/api/v1/needs/", headers=auth_headers, json={
        "title": "Need Item",
        "description": "This is a need",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    
    # Search for offers only
    response = client.get("/api/v1/search/?type=offer")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == "offer"
    assert data["items"][0]["title"] == "Offer Item"


def test_search_by_type_need(client: TestClient, auth_headers: dict):
    """Test filtering by type: needs only."""
    # Create offer and need
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Offer Item",
        "description": "This is an offer",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    
    client.post("/api/v1/needs/", headers=auth_headers, json={
        "title": "Need Item",
        "description": "This is a need",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    
    # Search for needs only
    response = client.get("/api/v1/search/?type=need")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == "need"


def test_search_by_tags_any(client: TestClient, auth_headers: dict):
    """Test tag filtering with ANY match mode."""
    # Create items with different tags
    response = client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Python Help",
        "description": "Programming course for beginners",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "programming"]
    })
    assert response.status_code == 201, f"Failed to create offer: {response.json()}"
    
    response2 = client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "JavaScript Help",
        "description": "Web dev tutorials and support",
        "is_remote": True,
        "capacity": 1,
        "tags": ["javascript", "programming"]
    })
    assert response2.status_code == 201, f"Failed to create offer 2: {response2.json()}"
    
    response3 = client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Math Tutoring",
        "description": "Algebra and geometry lessons",
        "is_remote": True,
        "capacity": 1,
        "tags": ["math", "education"]
    })
    assert response3.status_code == 201, f"Failed to create offer 3: {response3.json()}"
    
    # Search for items with "python" OR "javascript" tags
    response = client.get("/api/v1/search/?tags=python&tags=javascript&tag_match=any")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # Both Python and JavaScript items


def test_search_by_tags_all(client: TestClient, auth_headers: dict):
    """Test tag filtering with ALL match mode."""
    # Create items with different tag combinations
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Python Web Dev",
        "description": "Full stack",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "programming", "web"]
    })
    
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Python Basics",
        "description": "Intro course",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "programming"]  # Missing "web"
    })
    
    # Search for items with ALL: python AND programming AND web
    response = client.get("/api/v1/search/?tags=python&tags=programming&tags=web&tag_match=all")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Web Dev" in data["items"][0]["title"]


def test_search_by_remote_flag(client: TestClient, auth_headers: dict):
    """Test filtering by remote flag."""
    # Create remote offer
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Remote Service",
        "description": "Online only",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    
    # Create in-person offer
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "In-Person Service",
        "description": "Face to face",
        "is_remote": False,
        "location_name": "New York",
        "capacity": 1,
        "tags": ["test"]
    })
    
    # Search for remote only
    response = client.get("/api/v1/search/?is_remote=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["is_remote"] is True
    
    # Search for in-person only
    response = client.get("/api/v1/search/?is_remote=false")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["is_remote"] is False


def test_search_sort_by_recency(client: TestClient, auth_headers: dict):
    """Test sorting by recency (most recent first)."""
    import time
    
    # Create items in sequence
    response1 = client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "First Offer",
        "description": "Created first",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    offer1_id = response1.json()["id"]
    
    # Small delay to ensure different timestamps
    time.sleep(0.1)
    
    response2 = client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Second Offer",
        "description": "Created second",
        "is_remote": True,
        "capacity": 1,
        "tags": ["test"]
    })
    offer2_id = response2.json()["id"]
    
    # Search with recency sort (default)
    response = client.get("/api/v1/search/?sort_by=recency")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    # Most recent (second) should be first
    assert data["items"][0]["id"] == offer2_id
    assert data["items"][1]["id"] == offer1_id


def test_search_pagination(client: TestClient, auth_headers: dict):
    """Test pagination in search results."""
    # Create multiple offers
    for i in range(5):
        client.post("/api/v1/offers/", headers=auth_headers, json={
            "title": f"Offer {i}",
            "description": f"Description {i}",
            "is_remote": True,
            "capacity": 1,
            "tags": ["test"]
        })
    
    # Get first page (2 items)
    response = client.get("/api/v1/search/?limit=2&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 2
    
    # Get second page
    response = client.get("/api/v1/search/?limit=2&skip=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["skip"] == 2


def test_search_combined_filters(client: TestClient, auth_headers: dict):
    """Test multiple filters combined."""
    # Create various items
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Remote Python Tutoring",
        "description": "Online Python lessons",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "education"]
    })
    
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "In-Person Python Class",
        "description": "Local Python class",
        "is_remote": False,
        "location_name": "NYC",
        "capacity": 1,
        "tags": ["python", "education"]
    })
    
    client.post("/api/v1/needs/", headers=auth_headers, json={
        "title": "Need Python Help",
        "description": "Remote help needed",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "education"]
    })
    
    # Search: remote + python tag + offer type
    response = client.get("/api/v1/search/?type=offer&tags=python&is_remote=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Remote Python Tutoring"


def test_list_tags(client: TestClient, auth_headers: dict):
    """Test listing available tags."""
    # Create items with tags
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Offer 1",
        "description": "Test offer for listing tags",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "programming"]
    })
    
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Offer 2",
        "description": "Another test offer for tags",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "education"]  # python used twice
    })
    
    # List all tags
    response = client.get("/api/v1/search/tags")
    assert response.status_code == 200
    tags = response.json()
    
    # Should have 3 unique tags
    assert len(tags) == 3
    
    # Python should have highest usage count (2)
    tag_names = [t["name"] for t in tags]
    assert "python" in tag_names
    assert "programming" in tag_names
    assert "education" in tag_names
    
    python_tag = next(t for t in tags if t["name"] == "python")
    assert python_tag["usage_count"] == 2


def test_tag_autocomplete(client: TestClient, auth_headers: dict):
    """Test tag search for autocomplete."""
    # Create tags
    client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Test",
        "description": "Test offer for autocomplete tags",
        "is_remote": True,
        "capacity": 1,
        "tags": ["python", "programming", "javascript"]
    })
    
    # Search tags starting with "py"
    response = client.get("/api/v1/search/tags?query=py")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) == 1
    assert tags[0]["name"] == "python"


def test_tags_created_on_demand(client: TestClient, auth_headers: dict):
    """Test that new tags are created automatically (FR-8.3)."""
    # Create offer with new tag
    response = client.post("/api/v1/offers/", headers=auth_headers, json={
        "title": "Test Offer",
        "description": "Testing tag creation",
        "is_remote": True,
        "capacity": 1,
        "tags": ["brand_new_tag", "another_new_tag"]
    })
    
    assert response.status_code == 201
    
    # Verify tags were created
    tags_response = client.get("/api/v1/search/tags")
    tags = tags_response.json()
    tag_names = [t["name"] for t in tags]
    
    assert "brand_new_tag" in tag_names
    assert "another_new_tag" in tag_names
