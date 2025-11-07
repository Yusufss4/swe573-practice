# Available Time Slots Feature

## Overview

Both **Offers** and **Needs** now support specifying available time slots when creating or updating service listings. This feature allows users to indicate specific dates and times when they are available to provide or receive services, matching the UI design shown in the project requirements.

## Implementation Summary

### New Components

1. **Schema Models** (`app/schemas/time_slot.py`)
   - `TimeRange`: Represents a time range (e.g., "14:00" to "15:00")
   - `AvailableTimeSlot`: Groups time ranges by date (e.g., October 22 with multiple slots)

2. **Database Schema**
   - **Offers**: Already had `available_slots` TEXT column (stores JSON)
   - **Needs**: Added `available_slots` TEXT column (stores JSON)

3. **API Updates**
   - Updated `OfferCreate`, `OfferUpdate`, `OfferResponse` schemas
   - Updated `NeedCreate`, `NeedUpdate`, `NeedResponse` schemas
   - Modified offer/need creation and update endpoints to handle time slots
   - Added JSON serialization/deserialization for time slots

4. **Tests**
   - Created comprehensive test suite (`tests/test_time_slots.py`)
   - 7 tests covering creation, updates, and validation
   - All 55 tests passing (including 48 existing + 7 new)

## Data Structure

### Time Slot Format

```json
{
  "available_slots": [
    {
      "date": "2025-12-01",
      "time_ranges": [
        {"start_time": "14:00", "end_time": "15:00"},
        {"start_time": "15:00", "end_time": "16:00"}
      ]
    },
    {
      "date": "2025-12-02",
      "time_ranges": [
        {"start_time": "10:00", "end_time": "11:00"}
      ]
    }
  ]
}
```

### Validation Rules

- **Date format**: Must be `YYYY-MM-DD` (e.g., "2025-12-01")
- **Time format**: Must be `HH:MM` in 24-hour format (e.g., "14:00", "09:30")
- **Time range**: `end_time` must be after `start_time`
- **Optional**: Time slots are completely optional (can be `null` for flexible scheduling)

## API Examples

### Create an Offer with Time Slots

```bash
POST /api/v1/offers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Web Development Tutoring",
  "description": "I can help you learn HTML, CSS, JavaScript, and React.",
  "is_remote": true,
  "capacity": 3,
  "tags": ["Coding", "Education", "Web Development"],
  "available_slots": [
    {
      "date": "2025-10-22",
      "time_ranges": [
        {"start_time": "14:00", "end_time": "15:00"},
        {"start_time": "15:00", "end_time": "16:00"}
      ]
    },
    {
      "date": "2025-10-23",
      "time_ranges": [
        {"start_time": "10:00", "end_time": "11:00"}
      ]
    }
  ]
}
```

### Create a Need with Time Slots

```bash
POST /api/v1/needs/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Need Python Help",
  "description": "Looking for help with Django project",
  "is_remote": true,
  "capacity": 1,
  "tags": ["Python", "Django"],
  "available_slots": [
    {
      "date": "2025-12-05",
      "time_ranges": [
        {"start_time": "14:00", "end_time": "16:00"}
      ]
    }
  ]
}
```

### Update Time Slots

```bash
PATCH /api/v1/offers/{offer_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "available_slots": [
    {
      "date": "2025-12-10",
      "time_ranges": [
        {"start_time": "09:00", "end_time": "10:00"}
      ]
    }
  ]
}
```

### Flexible Scheduling (No Time Slots)

```bash
POST /api/v1/offers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "General Programming Help",
  "description": "Available for various programming help. We can schedule on an ad-hoc basis.",
  "is_remote": true,
  "capacity": 5,
  "tags": ["Programming"],
  "available_slots": null  // No specific slots - flexible
}
```

## Database Migration

For existing databases, run the migration script to add the `available_slots` column to the `needs` table:

```bash
cd /home/yusufss/swe573-practice/the_hive
docker compose exec app python scripts/migrate_add_slots_to_needs.py
```

**Note**: If you're recreating the database from scratch (using `init_db.py`), the migration is not needed as the column will be created automatically.

## Files Modified

### Created:
- `app/schemas/time_slot.py` - Time slot schema models
- `scripts/migrate_add_slots_to_needs.py` - Database migration script
- `scripts/example_time_slots.py` - Usage examples
- `tests/test_time_slots.py` - Comprehensive test suite

### Modified:
- `app/schemas/offer.py` - Added time slot support to offer schemas
- `app/schemas/need.py` - Added time slot support to need schemas
- `app/models/need.py` - Added `available_slots` field to Need model
- `app/api/offers.py` - JSON serialization for time slots
- `app/api/needs.py` - JSON serialization for time slots

## Test Coverage

All tests passing (55/55):
- ✅ Create offer with time slots
- ✅ Create offer without time slots (flexible)
- ✅ Update offer time slots
- ✅ Create need with time slots
- ✅ Validate time range (end_time > start_time)
- ✅ Validate time format (HH:MM)
- ✅ Validate date format (YYYY-MM-DD)
- ✅ All existing auth, offers, needs, RBAC, and health tests

## Usage

See `scripts/example_time_slots.py` for detailed usage examples:

```bash
python3 scripts/example_time_slots.py
```

## Future Enhancements

Potential improvements for future versions:
- Time zone support
- Recurring time slots (e.g., "every Monday 14:00-15:00")
- Booked vs available slot tracking
- Calendar integration (iCal export)
- Conflict detection when booking overlapping slots
