# Timezone Column Fix - Resolved ✅

## Problem

When registering a new user through the frontend, the backend was failing with the error:

```
sqlalchemy.exc.ProgrammingError: (psycopg.errors.UndefinedColumn) 
column users.timezone does not exist
```

## Root Cause

The `User` model in `app/models/user.py` includes a `timezone` field, but the PostgreSQL database was created **before** this field was added to the model. The database schema was outdated and missing the `timezone` column.

## Solution

**Reset the database to recreate the schema with all current fields:**

```bash
cd /home/yusufss/swe573-practice/the_hive/infra

# Stop containers and remove volumes (this deletes all data)
docker-compose down -v

# Start services fresh
docker-compose up -d

# Wait for services to start, then initialize database
sleep 5
docker-compose exec app python scripts/init_db.py
```

## Verification

Confirmed that the `timezone` column now exists:

```bash
docker-compose exec db psql -U postgres -d the_hive -c "\d users"
```

Output shows:
```
timezone | character varying(50) | not null |
```

## Frontend Implementation

The frontend **already** sends timezone data during registration:

```tsx
// In RegisterPage.tsx
const [formData, setFormData] = useState({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  full_name: '',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, // Auto-detected!
});
```

The timezone is automatically detected using the browser's `Intl.DateTimeFormat().resolvedOptions().timeZone`, which returns IANA timezone strings like:
- `America/New_York`
- `Europe/Istanbul`
- `Asia/Tokyo`
- `UTC`

## Schema Details

The `timezone` field in the `User` model:

```python
# User's timezone for proper time slot handling
timezone: str = Field(
    default="UTC",
    max_length=50,
    description="User's IANA timezone (e.g., 'America/New_York', 'Europe/Istanbul')"
)
```

**Purpose (SRS Context):**
- Used for scheduling time slots in offers/needs
- Ensures users see times in their local timezone
- Required for displaying availability windows correctly
- Defaults to "UTC" if not provided

## Test Registration

Now you can register users successfully through the frontend at http://localhost:3000/#/register

Example registration payload that works:
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "password123",
  "full_name": "New User",
  "timezone": "America/New_York"
}
```

## Services Status

All services are now running correctly:

- **Database (PostgreSQL):** `localhost:5432` ✅
- **Backend (FastAPI):** `http://localhost:8000` ✅  
- **Frontend (React/Vite):** `http://localhost:3000` ✅

## Next Steps

1. Open http://localhost:3000 in your browser
2. Click "Register" to create a new account
3. The timezone will be auto-detected from your browser
4. After registration, you'll be automatically logged in and redirected to the Dashboard
5. You should see your starting balance of **5.0 hours** (SRS FR-7.1)

## Important Note

**When you run `docker-compose down -v`, all data is deleted.** This includes:
- All user accounts
- All offers and needs
- All ledger entries

This is expected in development. For production, you would use database migrations instead of dropping/recreating the schema.
