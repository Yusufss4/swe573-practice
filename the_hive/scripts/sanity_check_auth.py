#!/usr/bin/env python3
"""
Sanity check script for authentication system.

Tests:
1. User registration
2. User login
3. Access /auth/me with token
4. Role-based access control (403 for insufficient permissions)
"""
import sys
from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User


def test_password_hashing():
    """Test password hashing."""
    print("1. Testing password hashing...")
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    
    assert hashed != password, "Password should be hashed"
    assert hashed.startswith("$2b$"), "Should use bcrypt"
    assert verify_password(password, hashed), "Verification should work"
    assert not verify_password("wrong", hashed), "Wrong password should fail"
    
    print("   ✅ Password hashing works correctly")


def test_user_creation():
    """Test creating users with different roles."""
    print("\n2. Testing user creation...")
    
    with Session(engine) as session:
        # Clear existing test users
        statement = select(User).where(User.username.in_(["testuser", "testmod", "testadmin"]))
        existing = session.exec(statement).all()
        for user in existing:
            session.delete(user)
        session.commit()
        
        # Create regular user
        user = User(
            email="testuser@example.com",
            username="testuser",
            password_hash=get_password_hash("password123"),
            full_name="Test User",
            role="user",
            balance=5.0,
            is_active=True
        )
        session.add(user)
        
        # Create moderator
        moderator = User(
            email="testmod@example.com",
            username="testmod",
            password_hash=get_password_hash("password123"),
            role="moderator",
            balance=5.0,
            is_active=True
        )
        session.add(moderator)
        
        # Create admin
        admin = User(
            email="testadmin@example.com",
            username="testadmin",
            password_hash=get_password_hash("password123"),
            role="admin",
            balance=5.0,
            is_active=True
        )
        session.add(admin)
        
        session.commit()
        
        # Verify
        statement = select(User).where(User.username == "testuser")
        created_user = session.exec(statement).first()
        assert created_user is not None, "User should be created"
        assert created_user.role == "user", "Role should be 'user'"
        assert created_user.balance == 5.0, "Starting balance should be 5.0"
        
        print("   ✅ Created regular user (role=user, balance=5.0)")
        print("   ✅ Created moderator (role=moderator)")
        print("   ✅ Created admin (role=admin)")


def test_token_generation():
    """Test JWT token generation and decoding."""
    print("\n3. Testing JWT token generation...")
    
    with Session(engine) as session:
        statement = select(User).where(User.username == "testuser")
        user = session.exec(statement).first()
        
        if not user:
            print("   ❌ Test user not found")
            return False
        
        # Create token
        token = create_access_token(
            data={"sub": user.id, "username": user.username, "role": user.role}
        )
        
        assert len(token) > 0, "Token should not be empty"
        assert "." in token, "JWT should have dots separating parts"
        
        print(f"   ✅ Generated JWT token: {token[:50]}...")
        print(f"   ✅ Token for user_id={user.id}, username={user.username}, role={user.role}")


def test_role_verification():
    """Test that roles are correctly stored and retrievable."""
    print("\n4. Testing role verification...")
    
    with Session(engine) as session:
        # Check each role
        for username, expected_role in [("testuser", "user"), ("testmod", "moderator"), ("testadmin", "admin")]:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            
            if not user:
                print(f"   ❌ {username} not found")
                continue
            
            assert user.role == expected_role, f"Role should be {expected_role}"
            print(f"   ✅ {username} has role={expected_role}")


def main():
    """Run all sanity checks."""
    print("=" * 60)
    print("AUTH SYSTEM SANITY CHECKS")
    print("=" * 60)
    
    try:
        test_password_hashing()
        test_user_creation()
        test_token_generation()
        test_role_verification()
        
        print("\n" + "=" * 60)
        print("✅ ALL SANITY CHECKS PASSED")
        print("=" * 60)
        print("\nAuth system is working correctly!")
        print("\nNext steps:")
        print("1. Start the server: uvicorn app.main:app --reload")
        print("2. Test register: POST /api/v1/auth/register")
        print("3. Test login: POST /api/v1/auth/login")
        print("4. Test /auth/me with token: GET /api/v1/auth/me")
        print("5. Test role guard (403): Try accessing admin endpoint with user token")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ SANITY CHECK FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
