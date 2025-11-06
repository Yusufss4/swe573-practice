# User API Testing Guide

## Overview

The User API provides complete CRUD operations for managing users in the system.

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### 1. Create User

**POST** `/users/`

Create a new user.

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-06T13:30:00",
  "updated_at": "2025-11-06T13:30:00"
}
```

**Errors:**
- `400 Bad Request` - Email already registered or username already taken
- `422 Unprocessable Entity` - Invalid data format

---

### 2. List Users

**GET** `/users/`

Get a list of all users with optional pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)
- `active_only` (optional): Filter only active users (default: false)

```bash
# Get all users
curl "http://localhost:8000/api/v1/users/"

# With pagination
curl "http://localhost:8000/api/v1/users/?skip=0&limit=10"

# Only active users
curl "http://localhost:8000/api/v1/users/?active_only=true"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-11-06T13:30:00",
    "updated_at": "2025-11-06T13:30:00"
  },
  {
    "id": 2,
    "email": "jane@example.com",
    "username": "janedoe",
    "full_name": "Jane Doe",
    "is_active": true,
    "created_at": "2025-11-06T13:31:00",
    "updated_at": "2025-11-06T13:31:00"
  }
]
```

---

### 3. Get User by ID

**GET** `/users/{user_id}`

Get details of a specific user.

```bash
curl "http://localhost:8000/api/v1/users/1"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-06T13:30:00",
  "updated_at": "2025-11-06T13:30:00"
}
```

**Errors:**
- `404 Not Found` - User does not exist

---

### 4. Update User

**PATCH** `/users/{user_id}`

Update user details (partial update).

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "is_active": false
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "full_name": "John Smith",
  "is_active": false,
  "created_at": "2025-11-06T13:30:00",
  "updated_at": "2025-11-06T13:35:00"
}
```

**Errors:**
- `404 Not Found` - User does not exist
- `422 Unprocessable Entity` - Invalid data format

---

### 5. Delete User

**DELETE** `/users/{user_id}`

Delete a user permanently.

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1"
```

**Response (204 No Content):**
No response body.

**Errors:**
- `404 Not Found` - User does not exist

---

## Complete Testing Workflow

### Setup Database

```bash
# Create database tables
cd /home/yusufss/swe573-practice/the_hive
python scripts/init_db.py
```

### Start the Server

```bash
cd /home/yusufss/swe573-practice/the_hive
uvicorn app.main:app --reload
```

### Test Sequence

```bash
# 1. Create users
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "username": "alice", "full_name": "Alice Wonder"}'

curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@example.com", "username": "bob", "full_name": "Bob Builder"}'

# 2. List all users
curl "http://localhost:8000/api/v1/users/"

# 3. Get specific user
curl "http://localhost:8000/api/v1/users/1"

# 4. Update user
curl -X PATCH "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Alice in Wonderland"}'

# 5. Delete user
curl -X DELETE "http://localhost:8000/api/v1/users/2"

# 6. Verify deletion
curl "http://localhost:8000/api/v1/users/2"  # Should return 404
```

---

## Using Swagger UI

Navigate to http://localhost:8000/docs to use the interactive API documentation:

1. Expand the `/api/v1/users/` endpoint
2. Click "Try it out"
3. Fill in the request body
4. Click "Execute"
5. View the response

---

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create user
response = requests.post(
    f"{BASE_URL}/users/",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User"
    }
)
user = response.json()
print(f"Created user: {user}")

# List users
response = requests.get(f"{BASE_URL}/users/")
users = response.json()
print(f"Total users: {len(users)}")

# Get user
user_id = user["id"]
response = requests.get(f"{BASE_URL}/users/{user_id}")
print(f"User details: {response.json()}")

# Update user
response = requests.patch(
    f"{BASE_URL}/users/{user_id}",
    json={"full_name": "Updated Name"}
)
print(f"Updated user: {response.json()}")

# Delete user
response = requests.delete(f"{BASE_URL}/users/{user_id}")
print(f"Delete status: {response.status_code}")
```

---

## Running Tests

```bash
cd /home/yusufss/swe573-practice/the_hive
pytest tests/test_users.py -v
```

---

## Database Check

Verify database is working:

```bash
curl "http://localhost:8000/healthz"
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  ...
}
```

---

## Common Issues

### Database not connected

**Error:** `"database": "disconnected"` in health check

**Solution:**
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in `.env`
3. Run `python scripts/init_db.py` to create tables

### Duplicate email/username

**Error:** `400 Bad Request - Email already registered`

**Solution:** Use a different email or username

### User not found

**Error:** `404 Not Found`

**Solution:** Verify the user ID exists by listing all users first

---

## Next Steps

- Add authentication to protect endpoints
- Add user roles and permissions
- Add password hashing
- Add email verification
- Add pagination metadata
- Add search and filtering
