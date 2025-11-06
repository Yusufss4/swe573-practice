#!/usr/bin/env python3
"""
Quick verification that auth modules import correctly.
Run this outside Docker to verify code syntax.
"""
import sys


def check_imports():
    """Check that all auth modules can be imported."""
    print("Checking auth module imports...")
    
    try:
        print("  → app.core.security")
        from app.core.security import (
            verify_password,
            get_password_hash,
            create_access_token,
            decode_access_token
        )
        print("    ✅ Security utilities")
        
        print("  → app.core.auth")
        from app.core.auth import (
            get_current_user,
            require_role,
            CurrentUser,
            AdminUser,
            ModeratorUser
        )
        print("    ✅ Auth dependencies")
        
        print("  → app.schemas.auth")
        from app.schemas.auth import (
            UserRegister,
            UserLogin,
            Token,
            TokenData,
            UserResponse
        )
        print("    ✅ Auth schemas")
        
        print("  → app.api.auth")
        from app.api.auth import router
        print("    ✅ Auth router")
        
        print("\n✅ All auth modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_password_hashing():
    """Basic password hashing test."""
    print("\nTesting password hashing...")
    
    try:
        from app.core.security import get_password_hash, verify_password
        
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password, "Password should be hashed"
        assert hashed.startswith("$2b$"), "Should use bcrypt"
        assert verify_password(password, hashed), "Verification should succeed"
        assert not verify_password("wrong", hashed), "Wrong password should fail"
        
        print("  ✅ bcrypt hashing works")
        print(f"  ✅ Hash format: {hashed[:29]}...")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def check_jwt_token():
    """Basic JWT token test."""
    print("\nTesting JWT token generation...")
    
    try:
        from app.core.security import create_access_token, decode_access_token
        
        data = {"sub": 1, "username": "testuser", "role": "user"}
        token = create_access_token(data)
        
        assert len(token) > 0, "Token should not be empty"
        assert token.count(".") == 2, "JWT should have 3 parts"
        
        decoded = decode_access_token(token)
        assert decoded is not None, "Token should decode"
        assert decoded["sub"] == 1, "User ID should match"
        assert decoded["username"] == "testuser", "Username should match"
        assert decoded["role"] == "user", "Role should match"
        
        print("  ✅ JWT encoding works")
        print("  ✅ JWT decoding works")
        print(f"  ✅ Token: {token[:50]}...")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("AUTH SYSTEM CODE VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        check_imports(),
        check_password_hashing(),
        check_jwt_token(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED")
        print("=" * 60)
        print("\nAuth code is valid!")
        print("\nNext: Run full tests with Docker:")
        print("  docker-compose exec web pytest tests/test_auth.py -v")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
