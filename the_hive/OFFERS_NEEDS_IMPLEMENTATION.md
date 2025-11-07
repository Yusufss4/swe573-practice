# Offers and Needs API Implementation

## ✅ Completed Requirements

### SRS Compliance

| Requirement | Description | Status |
|-------------|-------------|--------|
| FR-3.1 | Create offers/needs with all fields | ✅ |
| FR-3.2 | Can extend/renew, not shorten | ✅ |
| FR-3.3 | Auto-archive expired items | ✅ |
| FR-3.4 | Remote flag support | ✅ |
| FR-3.5 | Semantic tag assignment | ✅ |
| FR-3.6 | Capacity tracking | ✅ |
| FR-3.7 | Capacity constraints | ✅ |
| FR-4.1 | Available time slots (Offers only) | ✅ |
| FR-8.1 | Semantic tags | ✅ |
| FR-8.3 | Users can create tags freely | ✅ |
| FR-12.1 | Auto-archive system | ✅ |
| FR-12.2 | Expired items hidden by default | ✅ |

### Constraints

✅ **7-day default duration** - All offers/needs created with 7-day validity  
✅ **Default capacity = 1** - Capacity defaults to 1 participant  
✅ **Approximate locations only** - No exact addresses stored  
✅ **Can extend, not shorten** - No endpoint to reduce end_date  
✅ **Location required for non-remote** - Validation enforced  
✅ **Cannot decrease capacity below accepted count** - Validation enforced

## 📁 Files Created

### Models (Already Existed)
- `app/models/offer.py` - Offer model with status enum
- `app/models/need.py` - Need model with status enum
- `app/models/tag.py` - Tag model for semantic tagging
- `app/models/associations.py` - OfferTag and NeedTag junction tables

### Schemas
1. **`app/schemas/offer.py`** - Offer CRUD schemas
   - `OfferCreate` - Create with tags and slots
   - `OfferUpdate` - Partial update
   - `OfferExtend` - Extend end date
   - `OfferResponse` - Response with tags
   - `OfferListResponse` - Paginated list

2. **`app/schemas/need.py`** - Need CRUD schemas
   - `NeedCreate` - Create with tags
   - `NeedUpdate` - Partial update
   - `NeedExtend` - Extend end date
   - `NeedResponse` - Response with tags
   - `NeedListResponse` - Paginated list

### Core Utilities
3. **`app/core/offers_needs.py`** - Utility functions
   - `get_or_create_tag()` - Auto-create tags
   - `associate_tags_to_offer/need()` - Link tags
   - `get_offer/need_tags()` - Retrieve tags
   - `update_offer/need_tags()` - Replace tags
   - `archive_expired_items()` - Batch archive
   - `check_and_archive_item()` - On-read hook

### API Endpoints
4. **`app/api/offers.py`** - Offer endpoints
   - POST `/offers/` - Create
   - GET `/offers/` - List (public, active only)
   - GET `/offers/my` - My offers (includes expired)
   - GET `/offers/{id}` - Get specific
   - PATCH `/offers/{id}` - Update
   - POST `/offers/{id}/extend` - Extend duration
   - DELETE `/offers/{id}` - Cancel (soft delete)

5. **`app/api/needs.py`** - Need endpoints
   - POST `/needs/` - Create
   - GET `/needs/` - List (public, active only)
   - GET `/needs/my` - My needs (includes expired)
   - GET `/needs/{id}` - Get specific
   - PATCH `/needs/{id}` - Update
   - POST `/needs/{id}/extend` - Extend duration
   - DELETE `/needs/{id}` - Cancel (soft delete)

### Tests
6. **`tests/test_offers.py`** - 15+ test cases
7. **`tests/test_needs.py`** - 10+ test cases

### Scripts
8. **`scripts/sanity_check_offers_needs.py`** - Sanity checks

### Configuration
9. **`app/main.py`** - Registered routers

## 🚀 API Endpoints

### Offers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/offers/` | Yes | Create offer |
| GET | `/api/v1/offers/` | No | List active offers |
| GET | `/api/v1/offers/my` | Yes | List my offers |
| GET | `/api/v1/offers/{id}` | No | Get specific offer |
| PATCH | `/api/v1/offers/{id}` | Yes | Update offer |
| POST | `/api/v1/offers/{id}/extend` | Yes | Extend duration |
| DELETE | `/api/v1/offers/{id}` | Yes | Cancel offer |

### Needs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/needs/` | Yes | Create need |
| GET | `/api/v1/needs/` | No | List active needs |
| GET | `/api/v1/needs/my` | Yes | List my needs |
| GET | `/api/v1/needs/{id}` | No | Get specific need |
| PATCH | `/api/v1/needs/{id}` | Yes | Update need |
| POST | `/api/v1/needs/{id}/extend` | Yes | Extend duration |
| DELETE | `/api/v1/needs/{id}` | Yes | Cancel need |

## 📝 Usage Examples

### Create an Offer

```bash
curl -X POST "http://localhost:8000/api/v1/offers/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Tutoring",
    "description": "I can help you learn Python programming basics and best practices",
    "is_remote": true,
    "capacity": 3,
    "tags": ["tutoring", "python", "programming"],
    "available_slots": ["2025-11-10T14:00:00Z", "2025-11-12T16:00:00Z"]
  }'
```

Response:
```json
{
  "id": 1,
  "creator_id": 1,
  "title": "Python Tutoring",
  "description": "I can help you learn Python programming basics and best practices",
  "is_remote": true,
  "capacity": 3,
  "accepted_count": 0,
  "status": "active",
  "start_date": "2025-11-06T10:00:00",
  "end_date": "2025-11-13T10:00:00",
  "tags": ["tutoring", "python", "programming"],
  "available_slots": ["2025-11-10T14:00:00Z", "2025-11-12T16:00:00Z"],
  "created_at": "2025-11-06T10:00:00"
}
```

### Create an Offer with Location

```bash
curl -X POST "http://localhost:8000/api/v1/offers/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Guitar Lessons",
    "description": "Beginner guitar lessons, acoustic and electric",
    "is_remote": false,
    "location_name": "Brooklyn, NY",
    "location_lat": 40.6782,
    "location_lon": -73.9442,
    "capacity": 1,
    "tags": ["music", "guitar", "lessons"]
  }'
```

### List Active Offers

```bash
curl "http://localhost:8000/api/v1/offers/?skip=0&limit=20"
```

Response:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Python Tutoring",
      ...
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20
}
```

### List My Offers (Including Expired)

```bash
curl "http://localhost:8000/api/v1/offers/my?include_expired=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Extend an Offer

```bash
curl -X POST "http://localhost:8000/api/v1/offers/1/extend" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

### Update an Offer

```bash
curl -X PATCH "http://localhost:8000/api/v1/offers/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python Tutoring",
    "capacity": 5,
    "tags": ["tutoring", "python", "advanced"]
  }'
```

### Create a Need

```bash
curl -X POST "http://localhost:8000/api/v1/needs/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Need Moving Help",
    "description": "Need help moving furniture to new apartment",
    "is_remote": false,
    "location_name": "Manhattan, NY",
    "location_lat": 40.7589,
    "location_lon": -73.9851,
    "capacity": 2,
    "tags": ["moving", "help", "physical"]
  }'
```

## 🔐 Authorization

- **Public endpoints** (no auth): List offers/needs, get specific items
- **Protected endpoints** (auth required): Create, update, extend, delete
- **Ownership validation**: Users can only modify their own items

## ✨ Features

### 1. Automatic Archiving

**On Read Hook**: When listing or getting items, expired ones are automatically archived:
```python
# Before returning list
archive_expired_items(session)
```

**Batch Job Ready**: The `archive_expired_items()` function can be called by a scheduler.

### 2. Status Transitions

```
active → expired (automatic on end_date)
active → full (when accepted_count reaches capacity)
active → completed (manual, after exchange)
active → cancelled (manual delete)
expired → active (extend/renew)
```

### 3. Tag Management

- **Auto-create**: Tags are created automatically when first used
- **Reuse**: Existing tags are reused (case-insensitive)
- **Usage tracking**: `usage_count` incremented on each use
- **Free creation**: Users can create any tag (SRS FR-8.3)

### 4. Capacity Management

- **Default 1**: Capacity defaults to 1 participant
- **Can increase**: Capacity can be increased while active
- **Cannot decrease below accepted**: Validation prevents capacity < accepted_count (SRS FR-3.7)
- **Full status**: When `accepted_count == capacity`, status changes to FULL

### 5. Location Handling

- **Approximate only**: No exact addresses (SRS NFR-7)
- **Optional lat/lon**: Geographic coordinates optional
- **Required for non-remote**: Location name required if `is_remote=false`

### 6. Duration Management

- **7-day default**: All items created with 7-day validity (SRS constraint)
- **Can extend**: Use `/extend` endpoint to add days
- **Can renew**: Expired items can be extended to reactivate
- **Cannot shorten**: No endpoint provided to reduce duration (SRS FR-3.2)

## 🧪 Testing

### Run Tests

```bash
# All offers tests
docker-compose exec app pytest tests/test_offers.py -v

# All needs tests
docker-compose exec app pytest tests/test_needs.py -v

# Sanity checks
docker-compose exec app python scripts/sanity_check_offers_needs.py
```

### Test Coverage

✅ Create with default 7-day duration  
✅ Create with location validation  
✅ List active (expired hidden)  
✅ List my items (includes expired)  
✅ Get specific item  
✅ Update item  
✅ Cannot decrease capacity below accepted  
✅ Extend duration  
✅ Renew expired items  
✅ Delete (cancel) item  
✅ Cannot modify others' items  
✅ Pagination  
✅ Tag association  
✅ Auto-archiving

## 📊 Database Schema

### Offer/Need Fields

```sql
CREATE TABLE offers (
    id INTEGER PRIMARY KEY,
    creator_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    description VARCHAR(2000),
    is_remote BOOLEAN DEFAULT FALSE,
    location_lat FLOAT,
    location_lon FLOAT,
    location_name VARCHAR(255),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    capacity INTEGER DEFAULT 1,
    accepted_count INTEGER DEFAULT 0,
    status VARCHAR(20),  -- active, full, expired, completed, cancelled
    available_slots TEXT,  -- JSON for offers only
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Tag Tables

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    description VARCHAR(500),
    parent_id INTEGER REFERENCES tags(id),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE offer_tags (
    id INTEGER PRIMARY KEY,
    offer_id INTEGER REFERENCES offers(id),
    tag_id INTEGER REFERENCES tags(id)
);

CREATE TABLE need_tags (
    id INTEGER PRIMARY KEY,
    need_id INTEGER REFERENCES needs(id),
    tag_id INTEGER REFERENCES tags(id)
);
```

## 🚧 Future Enhancements

- [ ] Search by tags
- [ ] Filter by location/distance
- [ ] Sort by distance from user
- [ ] Tag hierarchy implementation
- [ ] Scheduled batch archiving job
- [ ] Map-based visualization
- [ ] Advanced filtering (date range, capacity, status)

## ✅ Sanity Checks Satisfied

**Required Tests**:
1. ✅ Create/extend works
2. ✅ Cannot shorten (no endpoint exists)
3. ✅ Expired items hidden from public list
4. ✅ Owners can view their expired items

All requirements from the prompt are fully implemented and tested! 🎉
