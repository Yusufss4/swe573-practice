# Authentication System Testing Guide

This guide provides examples for testing the authentication system.

## Overview

The authentication system implements:
- **User Registration** (SRS FR-1.1, FR-1.2)
- **User Login** (SRS FR-1.3)
- **JWT Token Authentication** (SRS FR-1.5)
- **Password Hashing with bcrypt** (SRS NFR-5)
- **Role-based Access Control** (user, moderator, admin)

## Running Automated Tests

```bash
# Run all auth tests
pytest tests/test_auth.py -v

# Run role-based access control tests
pytest tests/test_rbac.py -v

# Run sanity check script
python scripts/sanity_check_auth.py
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login and get JWT token | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |
| POST | `/api/v1/auth/logout` | Logout (client-side token deletion) | No |

## 1. Register a New User

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "SecurePass123!",
    "full_name": "Alice Wonder"
  }'
```

### Response (201 Created)

```json
{
  "id": 1,
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Wonder",
  "role": "user",
  "balance": 5.0,
  "is_active": true,
  "created_at": "2025-11-06T10:30:00"
}
```

### Validation Rules

- **email**: Must be valid email format
- **username**: 3-50 characters, unique
- **password**: Minimum 8 characters
- **full_name**: Optional, max 100 characters

### Error Responses

```json
// 400 - Username already exists
{
  "detail": "Username already registered"
}

// 400 - Email already exists
{
  "detail": "Email already registered"
}

// 422 - Invalid email format
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## 2. Login

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePass123!"
  }'
```

### Response (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Expiry**: 7 days (168 hours)

### Error Responses

```json
// 401 - Wrong credentials
{
  "detail": "Incorrect username or password"
}

// 400 - Inactive user
{
  "detail": "Inactive user account"
}
```

## 3. Get Current User Info

### Request

```bash
# Save token from login
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Response (200 OK)

```json
{
  "id": 1,
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Wonder",
  "role": "user",
  "balance": 5.0,
  "is_active": true,
  "created_at": "2025-11-06T10:30:00"
}
```

### Error Responses

```json
// 403 - No token provided
{
  "detail": "Not authenticated"
}

// 401 - Invalid token
{
  "detail": "Could not validate credentials"
}

// 401 - User not found
{
  "detail": "User not found"
}
```

## 4. Logout

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout"
```

### Response (200 OK)

```json
{
  "message": "Successfully logged out. Please delete your token."
}
```

**Note**: JWT tokens are stateless. The client must delete the stored token.

## Role-Based Access Control

### User Roles

1. **user** (default) - Regular community member
2. **moderator** - Can moderate content and handle reports
3. **admin** - Full system access

### Testing Role Guards

Create test endpoints (for development):

```python
from app.core.auth import CurrentUser, AdminUser, ModeratorUser, require_role

# Any authenticated user
@router.get("/user-endpoint")
def user_only(current_user: CurrentUser):
    return {"message": f"Hello {current_user.username}"}

# Moderators and admins only
@router.get("/moderator-endpoint")
def moderator_only(current_user: ModeratorUser):
    return {"message": "Moderator access"}

# Admins only
@router.get("/admin-endpoint")
def admin_only(current_user: AdminUser):
    return {"message": "Admin access"}

# Custom roles
@router.get("/custom", dependencies=[Depends(require_role("admin", "moderator"))])
def custom_roles():
    return {"message": "Custom role access"}
```

### Testing 403 Forbidden

```bash
# Login as regular user
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "SecurePass123!"}' \
  | jq -r '.access_token' > /tmp/user_token.txt

USER_TOKEN=$(cat /tmp/user_token.txt)

# Try to access admin endpoint (should get 403)
curl -X GET "http://localhost:8000/api/v1/test/admin-only" \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Expected Response (403)**:

```json
{
  "detail": "Access denied. Required roles: admin"
}
```

## Complete Workflow Example

```bash
#!/bin/bash
set -e

BASE_URL="http://localhost:8000/api/v1"

echo "1. Register user..."
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }' | jq '.'

echo -e "\n2. Login..."
TOKEN=$(curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }' | jq -r '.access_token')

echo "Token: ${TOKEN:0:50}..."

echo -e "\n3. Get user info..."
curl -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n4. Test without token (should fail)..."
curl -X GET "$BASE_URL/auth/me" || echo "Failed as expected"

echo -e "\n✅ Authentication workflow complete!"
```

## Python Testing Example

```python
import httpx

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register
register_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
}
response = httpx.post(f"{BASE_URL}/auth/register", json=register_data)
assert response.status_code == 201
user = response.json()
print(f"Registered: {user['username']}")

# 2. Login
login_data = {"username": "testuser", "password": "TestPass123!"}
response = httpx.post(f"{BASE_URL}/auth/login", json=login_data)
assert response.status_code == 200
token = response.json()["access_token"]
print(f"Token: {token[:50]}...")

# 3. Get current user
headers = {"Authorization": f"Bearer {token}"}
response = httpx.get(f"{BASE_URL}/auth/me", headers=headers)
assert response.status_code == 200
user = response.json()
print(f"Current user: {user['username']}, role: {user['role']}, balance: {user['balance']}")

# 4. Test invalid token (should fail)
bad_headers = {"Authorization": "Bearer invalid_token"}
response = httpx.get(f"{BASE_URL}/auth/me", headers=bad_headers)
assert response.status_code == 401
print("Invalid token rejected as expected")
```

## Security Notes

1. **HTTPS Required**: In production, always use HTTPS (SRS NFR-4)
2. **Password Hashing**: Passwords are hashed with bcrypt (SRS NFR-5)
3. **Token Storage**: Store tokens securely (e.g., httpOnly cookies or secure storage)
4. **Token Expiry**: Tokens expire after 7 days
5. **No Password in Response**: Password hash is never returned in API responses

## Troubleshooting

### "Could not validate credentials"
- Token expired (7 days)
- Token malformed
- Secret key changed
- User deleted

### "Inactive user account"
- User's `is_active` flag is False
- Contact admin to reactivate

### "Access denied. Required roles: ..."
- User role insufficient for endpoint
- Verify user role with `/auth/me`

### "Username already registered"
- Choose different username
- Username must be unique

## SRS Compliance Checklist

- ✅ FR-1.1: Unique username, email, password
- ✅ FR-1.2: Email format and password complexity validation
- ✅ FR-1.3: Login and logout functionality
- ✅ FR-1.4: Password encryption (bcrypt)
- ✅ FR-1.5: Session-based authentication (JWT)
- ✅ FR-7.1: Starting balance of 5 hours
- ✅ NFR-4: HTTPS connections (enforced in production)
- ✅ NFR-5: Passwords stored as salted hashes
- ✅ Role-based access control (user, moderator, admin)
- ✅ 403 Forbidden for insufficient permissions
