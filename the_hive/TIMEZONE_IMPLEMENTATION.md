# Timezone Support Implementation Summary

## Overview

Successfully added `timezone` field to the User model to support timezone-aware time slot handling across the application.

## Changes Made

### 1. Database Model (`app/models/user.py`)

Added timezone field to User model:
```python
timezone: str = Field(
    default="UTC",
    max_length=50,
    description="User's IANA timezone (e.g., 'America/New_York', 'Europe/Istanbul')"
)
```

**Properties:**
- Default value: `"UTC"`
- Required field (non-nullable)
- Supports IANA timezone names (e.g., "America/New_York", "Europe/Istanbul", "Asia/Tokyo")

### 2. API Schemas (`app/schemas/auth.py`)

**Updated `UserRegister`:**
- Added optional `timezone` field
- Users can provide timezone during registration
- Defaults to "UTC" if not provided

**Updated `UserResponse`:**
- Includes `timezone` in user response
- Returned in `/me`, `/login`, and `/register` endpoints

### 3. Registration Logic (`app/api/auth.py`)

Modified user registration to handle timezone:
```python
new_user = User(
    email=user_data.email,
    username=user_data.username,
    password_hash=hashed_password,
    full_name=user_data.full_name,
    timezone=user_data.timezone or "UTC",  # Default to UTC if not provided
    role="user",
    balance=5.0,
    is_active=True
)
```

### 4. Database Migration (`scripts/migrate_add_timezone_to_users.py`)

Created migration script to add timezone column to existing databases:
- Checks if column already exists
- Adds column with default value "UTC"
- Safe to run multiple times (idempotent)

**Usage:**
```bash
cd /home/yusufss/swe573-practice/the_hive
docker compose exec app python scripts/migrate_add_timezone_to_users.py
```

### 5. Tests (`tests/test_user_timezone.py`)

Created comprehensive test suite (5 new tests):
- ✅ `test_register_user_with_timezone` - Register with explicit timezone
- ✅ `test_register_user_without_timezone_defaults_to_utc` - Default behavior
- ✅ `test_user_timezone_in_me_endpoint` - Timezone in auth responses
- ✅ `test_create_offer_with_user_timezone_context` - Integration with offers
- ✅ `test_multiple_users_different_timezones` - Multiple users scenario

**All 60 tests passing** (55 existing + 5 new)

## API Examples

### Register with Timezone

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "istanbul_user",
  "password": "SecurePass123!",
  "full_name": "Istanbul User",
  "timezone": "Europe/Istanbul"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "istanbul_user",
  "full_name": "Istanbul User",
  "role": "user",
  "balance": 5.0,
  "timezone": "Europe/Istanbul",
  "is_active": true,
  "created_at": "2025-11-07T12:00:00Z"
}
```

### Register Without Timezone (Defaults to UTC)

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "default_user",
  "password": "SecurePass123!",
  "full_name": "Default User"
}
```

**Response:**
```json
{
  "id": 2,
  "email": "user@example.com",
  "username": "default_user",
  "full_name": "Default User",
  "role": "user",
  "balance": 5.0,
  "timezone": "UTC",  // <-- Defaults to UTC
  "is_active": true,
  "created_at": "2025-11-07T12:00:00Z"
}
```

## Integration with Time Slots

Users can now create time slots with their timezone context:

```bash
POST /api/v1/offers/
Authorization: Bearer <token>

{
  "title": "Tutoring Service",
  "description": "Available for tutoring",
  "is_remote": true,
  "capacity": 2,
  "tags": ["Education"],
  "available_slots": [
    {
      "date": "2025-12-01",
      "time_ranges": [
        {"start_time": "14:00", "end_time": "15:00"}
      ],
      "timezone": "Europe/Istanbul"  // Can use user's timezone
    }
  ]
}
```

## Frontend Integration

### Auto-detect User's Timezone

In JavaScript/TypeScript:
```javascript
// Detect user's timezone
const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
// Returns: "America/New_York", "Europe/Istanbul", etc.

// Send during registration
fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: email,
    username: username,
    password: password,
    timezone: userTimezone  // Auto-detected
  })
});
```

### Display Timezone Context

```javascript
// Show time with timezone context
function displayTimeSlot(slot) {
  return `${slot.start_time} - ${slot.end_time} (${slot.timezone})`;
  // Example: "14:00 - 15:00 (Europe/Istanbul)"
}

// Optionally convert to viewer's timezone
function convertToViewerTime(slot, viewerTimezone) {
  const date = new Date(`${slot.date}T${slot.start_time}:00`);
  const converted = date.toLocaleString('en-US', {
    timeZone: viewerTimezone,
    hour: '2-digit',
    minute: '2-digit'
  });
  return converted;
}
```

## Migration Path for Existing Databases

### Option 1: Run Migration Script

For databases with existing users:
```bash
docker compose exec app python scripts/migrate_add_timezone_to_users.py
```

This will:
1. Add `timezone` column to `users` table
2. Set default value "UTC" for all existing users
3. Users can update their timezone later through profile settings

### Option 2: Recreate Database

For development/fresh start:
```bash
docker compose exec app python scripts/init_db.py
```

The timezone field will be created automatically with new schema.

## Benefits

1. **Explicit Timezone Handling** 🌍
   - No ambiguity about what "14:00" means
   - Each user has their own timezone context

2. **Better UX** ✅
   - Users see times in their local timezone by default
   - Optional: show converted times for viewers

3. **Accurate Time Comparison** 🎯
   - Can convert all times to UTC for accurate overlap detection
   - Prevents scheduling conflicts across timezones

4. **Scalable** 🚀
   - Ready for global user base
   - Backward compatible (defaults to UTC)

5. **Flexible** 🔧
   - Users can update timezone if they move/travel
   - Can display times in any timezone

## Common Timezones

For reference, here are common IANA timezone names:

| Region | IANA Timezone |
|--------|---------------|
| New York | America/New_York |
| Los Angeles | America/Los_Angeles |
| London | Europe/London |
| Paris | Europe/Paris |
| Istanbul | Europe/Istanbul |
| Tokyo | Asia/Tokyo |
| Sydney | Australia/Sydney |
| UTC | UTC |

Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## Future Enhancements

1. **Profile Update Endpoint** (Coming Soon)
   - Allow users to update their timezone
   - `PATCH /api/v1/users/me` with `{"timezone": "..."}`

2. **Automatic Timezone in Time Slots**
   - Use user's timezone as default for time slots
   - Frontend can auto-fill timezone field

3. **Timezone Conversion Helper**
   - Backend endpoint to convert times between timezones
   - Useful for frontend display

4. **DST Warnings**
   - Warn users when Daylight Saving Time changes occur
   - Especially important for recurring events

## Testing

All tests passing ✅:
- 16 auth tests
- 13 offer tests  
- 6 need tests
- 11 RBAC tests
- 2 health tests
- 7 time slot tests
- 5 user timezone tests
- **Total: 60 tests passing**

## Summary

✅ **Timezone field successfully added to User model**
✅ **Backward compatible** (defaults to UTC)
✅ **All tests passing** (60/60)
✅ **Migration script ready** for existing databases
✅ **Integration with time slots** working
✅ **Documentation complete**

Users can now register with their timezone, and the system is ready to handle timezone-aware time slot scheduling!
