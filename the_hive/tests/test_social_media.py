"""
Tests for social media links functionality.

SRS FR-2: Profile Management - Social Media Links
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole


@pytest.fixture(name="engine")
def engine_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with overridden session."""
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
        password_hash=get_password_hash("TestPassword123!"),
        full_name="Test User",
        description="A test user",
        role=UserRole.USER,
        balance=5.0,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="user_with_social")
def user_with_social_fixture(session: Session):
    """Create a test user with social media links."""
    user = User(
        email="social@example.com",
        username="socialuser",
        password_hash=get_password_hash("TestPassword123!"),
        full_name="Social User",
        description="A user with social media",
        role=UserRole.USER,
        balance=5.0,
        social_blog="https://myblog.com",
        social_instagram="myinstagram",
        social_facebook="myfacebook",
        social_twitter="mytwitter",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Generate authentication headers for test user."""
    token = create_access_token(
        data={"sub": test_user.id, "username": test_user.username, "role": test_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="social_auth_headers")
def social_auth_headers_fixture(user_with_social: User):
    """Generate authentication headers for user with social media."""
    token = create_access_token(
        data={"sub": user_with_social.id, "username": user_with_social.username, "role": user_with_social.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


class TestSocialMediaUpdate:
    """Tests for updating social media links."""

    def test_update_social_media_all_fields(
        self, client: TestClient, auth_headers: dict, session: Session, test_user: User
    ):
        """Test updating all social media fields."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "social_blog": "https://example.com/blog",
                "social_instagram": "testuser_insta",
                "social_facebook": "testuser_fb",
                "social_twitter": "testuser_twitter",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] == "https://example.com/blog"
        assert data["social_instagram"] == "testuser_insta"
        assert data["social_facebook"] == "testuser_fb"
        assert data["social_twitter"] == "testuser_twitter"
        
        # Verify in database
        session.refresh(test_user)
        assert test_user.social_blog == "https://example.com/blog"
        assert test_user.social_instagram == "testuser_insta"
        assert test_user.social_facebook == "testuser_fb"
        assert test_user.social_twitter == "testuser_twitter"

    def test_update_social_media_partial(
        self, client: TestClient, auth_headers: dict, session: Session, test_user: User
    ):
        """Test updating only some social media fields."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "social_instagram": "only_insta",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_instagram"] == "only_insta"
        # Other fields should be None
        assert data["social_blog"] is None
        assert data["social_facebook"] is None
        assert data["social_twitter"] is None

    def test_update_social_media_clear_existing(
        self, client: TestClient, social_auth_headers: dict, session: Session, user_with_social: User
    ):
        """Test clearing existing social media links by setting to empty string."""
        # First verify user has social media
        assert user_with_social.social_blog == "https://myblog.com"
        
        # Clear by setting to empty string (treated as null)
        response = client.put(
            "/api/v1/users/me",
            headers=social_auth_headers,
            json={
                "social_blog": "",
                "social_instagram": "",
                "social_facebook": "",
                "social_twitter": "",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        # Empty strings should be stored (frontend sends empty string when cleared)
        assert data["social_blog"] == ""
        assert data["social_instagram"] == ""

    def test_update_social_media_with_other_fields(
        self, client: TestClient, auth_headers: dict, session: Session, test_user: User
    ):
        """Test updating social media along with other profile fields."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "full_name": "Updated Name",
                "description": "Updated description",
                "social_twitter": "new_twitter",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["social_twitter"] == "new_twitter"


class TestSocialMediaGet:
    """Tests for retrieving social media links."""

    def test_get_own_profile_with_social_media(
        self, client: TestClient, social_auth_headers: dict, user_with_social: User
    ):
        """Test getting own profile includes social media fields."""
        response = client.get("/api/v1/users/me", headers=social_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] == "https://myblog.com"
        assert data["social_instagram"] == "myinstagram"
        assert data["social_facebook"] == "myfacebook"
        assert data["social_twitter"] == "mytwitter"

    def test_get_own_profile_without_social_media(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test getting own profile without social media shows null values."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] is None
        assert data["social_instagram"] is None
        assert data["social_facebook"] is None
        assert data["social_twitter"] is None

    def test_get_other_user_profile_with_social_media(
        self, client: TestClient, auth_headers: dict, user_with_social: User
    ):
        """Test getting another user's profile includes their social media."""
        response = client.get(
            f"/api/v1/users/username/{user_with_social.username}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] == "https://myblog.com"
        assert data["social_instagram"] == "myinstagram"
        assert data["social_facebook"] == "myfacebook"
        assert data["social_twitter"] == "mytwitter"

    def test_get_other_user_profile_without_social_media(
        self, client: TestClient, social_auth_headers: dict, test_user: User
    ):
        """Test getting another user's profile without social media shows null values."""
        response = client.get(
            f"/api/v1/users/username/{test_user.username}",
            headers=social_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] is None
        assert data["social_instagram"] is None
        assert data["social_facebook"] is None
        assert data["social_twitter"] is None

    def test_get_profile_public_no_auth(
        self, client: TestClient, user_with_social: User
    ):
        """Test that user profiles with social media are accessible without auth."""
        response = client.get(f"/api/v1/users/username/{user_with_social.username}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] == "https://myblog.com"
        assert data["social_instagram"] == "myinstagram"


class TestSocialMediaValidation:
    """Tests for social media field validation."""

    def test_social_blog_accepts_url(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that blog field accepts full URLs."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "social_blog": "https://example.com/my-blog",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_blog"] == "https://example.com/my-blog"

    def test_social_username_accepts_simple_string(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that social usernames accept simple strings without URLs."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "social_instagram": "my_username123",
                "social_twitter": "twitterhandle",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["social_instagram"] == "my_username123"
        assert data["social_twitter"] == "twitterhandle"
