"""Debug test to check token payload."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.core.security import get_password_hash, decode_access_token
from app.core.db import get_session
from app.main import app
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


def test_token_payload_debug(client: TestClient, session: Session):
    """Debug test to see what's in the token."""
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
    session.refresh(user)
    
    print(f"\nCreated user ID: {user.id}")
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": password}
    )
    
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response body: {login_response.json()}")
    
    token = login_response.json()["access_token"]
    
    # Check SECRET_KEY being used
    from app.core.config import settings
    from app.core.security import ALGORITHM
    import jwt
    
    print(f"\nSECRET_KEY: {settings.SECRET_KEY}")
    print(f"ALGORITHM: {ALGORITHM}")
    print(f"\nToken: {token}")
    
    # Try to decode manually
    try:
        manual_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        print(f"\nManual decode SUCCESS: {manual_payload}")
    except Exception as e:
        print(f"\nManual decode FAILED: {e}")
    
    # Decode token to see payload
    payload = decode_access_token(token)
    print(f"\nDecoded token payload via function: {payload}")
    
    if payload:
        print(f"Token 'sub' field: {payload.get('sub')}")
        print(f"Token 'sub' type: {type(payload.get('sub'))}")
        
        # Check if user exists in database
        fetched_user = session.get(User, payload.get('sub'))
        print(f"\nFetched user from DB: {fetched_user}")
        print(f"Fetched user ID: {fetched_user.id if fetched_user else None}")
    
    # Now try the /me endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"\n/me response status: {response.status_code}")
    print(f"/me response body: {response.json()}")
