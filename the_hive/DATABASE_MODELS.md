# Database Models - The Hive

This document summarizes all database models created for The Hive MVP, aligned with SRS §3.5.1.

## ✅ Completed Models

### Core Models

#### 1. **User** (`app/models/user.py`)
- **Purpose**: Authentication and profile management
- **SRS Requirements**: FR-1.1, FR-7.1, NFR-5
- **Fields**:
  - `id` (PK)
  - `email` (unique, indexed)
  - `username` (unique, indexed)
  - `password_hash` (salted hash per NFR-5)
  - `full_name`, `description`
  - `role` (UserRole enum: USER, MODERATOR, ADMIN)
  - `balance` (default 5.0 per FR-7.1)
  - `location_lat`, `location_lon`, `location_name` (approximate location)
  - `is_active`
  - `created_at`, `updated_at`

#### 2. **Tag** (`app/models/tag.py`)
- **Purpose**: Semantic categorization
- **SRS Requirements**: FR-8.1, FR-8.3, FR-8.4
- **Fields**:
  - `id` (PK)
  - `name` (unique, indexed)
  - `description`
  - `parent_id` (FK to tags - simple hierarchy)
  - `usage_count`
  - `created_at`, `updated_at`

### Service Exchange Models

#### 3. **Offer** (`app/models/offer.py`)
- **Purpose**: Services users are willing to provide
- **SRS Requirements**: FR-3.1, FR-3.6, FR-4.1
- **Fields**:
  - `id` (PK)
  - `creator_id` (FK to users)
  - `title`, `description`
  - `is_remote`, `location_lat`, `location_lon`, `location_name`
  - `start_date`, `end_date` (7-day default)
  - `capacity` (default 1), `accepted_count`
  - `status` (OfferStatus enum: ACTIVE, FULL, EXPIRED, COMPLETED, CANCELLED)
  - `available_slots` (JSON string for calendar)
  - `created_at`, `updated_at`

#### 4. **Need** (`app/models/need.py`)
- **Purpose**: Service requests from users
- **SRS Requirements**: FR-3.1, FR-3.6
- **Fields**:
  - `id` (PK)
  - `creator_id` (FK to users)
  - `title`, `description`
  - `is_remote`, `location_lat`, `location_lon`, `location_name`
  - `start_date`, `end_date` (7-day default)
  - `capacity` (default 1), `accepted_count`
  - `status` (NeedStatus enum: ACTIVE, FULL, EXPIRED, COMPLETED, CANCELLED)
  - `created_at`, `updated_at`

### Association Tables

#### 5. **OfferTag** (`app/models/associations.py`)
- **Purpose**: Link Offers to Tags
- **SRS Requirements**: FR-3.5, FR-8.1
- **Fields**: `id` (PK), `offer_id` (FK), `tag_id` (FK)

#### 6. **NeedTag** (`app/models/associations.py`)
- **Purpose**: Link Needs to Tags
- **SRS Requirements**: FR-3.5, FR-8.1
- **Fields**: `id` (PK), `need_id` (FK), `tag_id` (FK)

### Handshake & Exchange Tracking

#### 7. **Participant** (`app/models/participant.py`)
- **Purpose**: Track user participation in exchanges (Handshake mechanism)
- **SRS Requirements**: FR-5, FR-7.6
- **Fields**:
  - `id` (PK)
  - `offer_id` (FK to offers), `need_id` (FK to needs)
  - `user_id` (FK to users)
  - `role` (ParticipantRole enum: PROVIDER, REQUESTER)
  - `status` (ParticipantStatus enum: PENDING, ACCEPTED, DECLINED, COMPLETED, CANCELLED)
  - `hours_contributed`
  - `message` (optional message when offering help per FR-5.1)
  - `selected_slot` (datetime)
  - `created_at`, `updated_at`

### TimeBank Accounting

#### 8. **LedgerEntry** (`app/models/ledger.py`)
- **Purpose**: Double-entry ledger for TimeBank accounting
- **SRS Requirements**: FR-7.2, FR-7.5, FR-7.6
- **Fields**:
  - `id` (PK)
  - `user_id` (FK to users)
  - `debit`, `credit`, `balance`
  - `transaction_type` (TransactionType enum: EXCHANGE, INITIAL, ADJUSTMENT, PENALTY)
  - `description`
  - `participant_id` (FK to participants)
  - `created_at` (indexed for audit trail)

#### 9. **Transfer** (`app/models/ledger.py`)
- **Purpose**: TimeBank transfers between users
- **SRS Requirements**: FR-7.2, FR-7.7
- **Fields**:
  - `id` (PK)
  - `sender_id` (FK to users)
  - `receiver_id` (FK to users)
  - `amount` (must be > 0)
  - `transaction_type`
  - `participant_id` (FK to participants)
  - `timestamp` (indexed)
  - `notes`

### Community & Moderation

#### 10. **Comment** (`app/models/comment.py`)
- **Purpose**: User feedback after exchanges
- **SRS Requirements**: FR-10.1, FR-10.2, FR-10.3
- **Fields**:
  - `id` (PK)
  - `from_user_id` (FK to users)
  - `to_user_id` (FK to users)
  - `content`
  - `participant_id` (FK to participants - exchange reference)
  - `is_moderated`, `is_approved`, `moderation_reason`
  - `is_visible`
  - `timestamp` (indexed), `moderated_at`

#### 11. **Report** (`app/models/report.py`)
- **Purpose**: Report inappropriate content/behavior
- **SRS Requirements**: FR-11, NFR-8
- **Fields**:
  - `id` (PK)
  - `reporter_id` (FK to users)
  - `reported_user_id`, `reported_offer_id`, `reported_need_id`, `reported_comment_id` (FKs)
  - `reason` (ReportReason enum: SPAM, HARASSMENT, INAPPROPRIATE, SCAM, MISINFORMATION, OTHER)
  - `description`
  - `status` (ReportStatus enum: PENDING, UNDER_REVIEW, RESOLVED, DISMISSED)
  - `moderator_id` (FK to users)
  - `moderator_action` (ReportAction enum: NONE, WARNING, CONTENT_REMOVED, USER_SUSPENDED, USER_BANNED)
  - `moderator_notes`
  - `created_at` (indexed), `reviewed_at`, `resolved_at`

## Database Schema Validation

✅ All tables created successfully  
✅ Foreign key constraints valid  
✅ Seed data inserted: 1 user + 1 offer + 1 tag + 1 ledger entry  
✅ Constraints enforced:
- Approximate locations only (lat/lon/name fields)
- Capacity default 1 (enforced in model)
- 7-day offer expiration (enforced via default factory)
- Starting balance 5 hours (enforced in model default)

## Enumerations

All enums are stored as PostgreSQL ENUM types:

- **UserRole**: USER, MODERATOR, ADMIN
- **OfferStatus / NeedStatus**: ACTIVE, FULL, EXPIRED, COMPLETED, CANCELLED
- **ParticipantRole**: PROVIDER, REQUESTER
- **ParticipantStatus**: PENDING, ACCEPTED, DECLINED, COMPLETED, CANCELLED
- **TransactionType**: EXCHANGE, INITIAL, ADJUSTMENT, PENALTY
- **ReportReason**: SPAM, HARASSMENT, INAPPROPRIATE, SCAM, MISINFORMATION, OTHER
- **ReportStatus**: PENDING, UNDER_REVIEW, RESOLVED, DISMISSED
- **ReportAction**: NONE, WARNING, CONTENT_REMOVED, USER_SUSPENDED, USER_BANNED

## Indexes Created

Performance-critical indexes:
- User: `email`, `username` (unique), `role`
- Tag: `name` (unique)
- Offer/Need: `creator_id`, `status`
- OfferTag/NeedTag: `offer_id/need_id`, `tag_id`
- Participant: `offer_id`, `need_id`, `user_id`, `role`, `status`
- LedgerEntry: `user_id`, `transaction_type`, `created_at`
- Transfer: `sender_id`, `receiver_id`, `timestamp`
- Comment: `from_user_id`, `to_user_id`, `timestamp`
- Report: `reporter_id`, `reason`, `status`, `created_at`

## Running the Database

```bash
# Initialize database (create tables + seed data)
python scripts/init_db.py

# Expected output:
# ✅ Database connection successful
# ✅ All tables created successfully
# ✅ Created user: alice (ID: 1, Balance: 5.0h)
# ✅ Created tag: tutoring (ID: 1)
# ✅ Created offer: Python Programming Tutoring (ID: 1, Capacity: 1)
# ✅ Schema validation passed - FK constraints are valid
```

## Next Steps

1. ✅ Models defined
2. ✅ Database initialized
3. ⏳ Create Pydantic schemas for API validation
4. ⏳ Implement CRUD endpoints
5. ⏳ Add authentication & authorization
6. ⏳ Implement TimeBank transaction logic
7. ⏳ Add moderation tools
