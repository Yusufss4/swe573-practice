"""
Tests for authentication endpoints.

Validates SRS FR-1: User Registration and Authentication
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.security import get_password_hash, verify_password
from app.main import app
from app.core.db import get_session
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


def test_register_user(client: TestClient):
    """Test user registration (SRS FR-1.1, FR-1.2)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"  # Default role
    assert data["balance"] == 5.0  # SRS FR-7.1: Starting balance
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data  # Password should never be returned


def test_register_duplicate_username(client: TestClient, session: Session):
    """Test registration with duplicate username fails."""
    # Create first user
    user = User(
        email="first@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0
    )
    session.add(user)
    session.commit()
    
    # Try to register with same username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "second@example.com",
            "username": "testuser",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_register_duplicate_email(client: TestClient, session: Session):
    """Test registration with duplicate email fails."""
    # Create first user
    user = User(
        email="test@example.com",
        username="firstuser",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0
    )
    session.add(user)
    session.commit()
    
    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "seconduser",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_invalid_email(client: TestClient):
    """Test registration with invalid email format (SRS FR-1.2)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "username": "testuser",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_register_short_username(client: TestClient):
    """Test registration with username too short."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "ab",  # Less than 3 characters
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 422


def test_register_short_password(client: TestClient):
    """Test registration with password too short (SRS FR-1.2)."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "short"  # Less than 8 characters
        }
    )
    
    assert response.status_code == 422


def test_login_success(client: TestClient, session: Session):
    """Test successful login (SRS FR-1.3, FR-1.4)."""
    # Create a user
    password = "SecurePass123!"
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash(password),
        role="user",
        balance=5.0,
        is_active=True
    )
    session.add(user)
    session.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": password
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_password(client: TestClient, session: Session):
    """Test login with incorrect password fails."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("correctpassword"),
        role="user",
        balance=5.0
    )
    session.add(user)
    session.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent username fails."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "anypassword"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_inactive_user(client: TestClient, session: Session):
    """Test login with inactive user fails."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="user",
        balance=5.0,
        is_active=False  # Inactive user
    )
    session.add(user)
    session.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    
    assert response.status_code == 400
    assert "Inactive user" in response.json()["detail"]


def test_get_current_user_with_token(client: TestClient, session: Session):
    """Test /auth/me endpoint with valid token (SRS FR-1.5)."""
    # Create and login user
    password = "SecurePass123!"
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash(password),
        full_name="Test User",
        role="user",
        balance=5.0,
        is_active=True
    )
    session.add(user)
    session.commit()
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": password}
    )
    token = login_response.json()["access_token"]
    
    # Call /auth/me with token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"
    assert data["balance"] == 5.0
    assert "password" not in data


def test_get_current_user_without_token(client: TestClient):
    """Test /auth/me without token fails."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401  # Unauthorized without credentials


def test_get_current_user_invalid_token(client: TestClient):
    """Test /auth/me with invalid token fails."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401


def test_logout(client: TestClient):
    """Test logout endpoint."""
    response = client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200
    assert "logged out" in response.json()["message"].lower()


def test_password_hashing():
    """Test password hashing is secure (SRS NFR-5)."""
    password = "MySecurePassword123!"
    hashed = get_password_hash(password)
    
    # Hash should be different from plain password
    assert hashed != password
    
    # Hash should be bcrypt format (starts with $2b$)
    assert hashed.startswith("$2b$")
    
    # Verify works correctly
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_user_roles(client: TestClient, session: Session):
    """Test different user roles are created correctly."""
    # Register regular user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "username": "regularuser",
            "password": "password123"
        }
    )
    assert response.json()["role"] == "user"
    
    # Create moderator manually (would be done by admin)
    moderator = User(
        email="mod@example.com",
        username="moderator",
        password_hash=get_password_hash("password123"),
        role="moderator",
        balance=5.0
    )
    session.add(moderator)
    
    # Create admin manually
    admin = User(
        email="admin@example.com",
        username="admin",
        password_hash=get_password_hash("password123"),
        role="admin",
        balance=5.0
    )
    session.add(admin)
    session.commit()
    
    # Verify roles are stored correctly
    assert moderator.role == "moderator"
    assert admin.role == "admin"
