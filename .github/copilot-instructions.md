# The Hive - AI Coding Agent Instructions

## Project Overview
**The Hive** is a full-stack time-banking platform where users exchange services tracked in hours. FastAPI backend + React/TypeScript frontend, built on double-entry bookkeeping principles with strict SRS requirements traceability.

**Tech Stack:**
- Backend: FastAPI, SQLModel, PostgreSQL, JWT auth, pytest
- Frontend: React 18, TypeScript, Vite, Material-UI, TanStack Query, Leaflet maps
- Infrastructure: Docker Compose, nginx

## Architecture Philosophy

### Monorepo Structure
```
the_hive/
├── app/              # FastAPI backend
├── frontend/         # React TypeScript frontend
├── tests/            # Backend pytest suite
├── scripts/          # Utility scripts (init_db.py)
├── infra/            # Docker orchestration
└── pyproject.toml    # Backend dependencies
```

### Core Domain Models (app/models/)
- **Users** start with 5.0h balance, can go -10.0h (reciprocity limit)
- **Offers/Needs** expire after 7 days by default, support capacity limits
- **Participants** implement handshake workflow (PENDING → ACCEPTED → COMPLETED)
- **Ledger** uses double-entry bookkeeping (every exchange creates paired debit/credit entries)

### SRS Requirement Tracing
**Every file has SRS comments** - e.g., `# SRS FR-7.2: Provider gains hours, requester loses hours`
- Always preserve these when editing
- Add new ones when implementing features
- Reference format: `FR-X.Y` (functional) or `NFR-X` (non-functional)
- See `tests/test_golden_path_need.py` for comprehensive SRS validation example

### Backend API Architecture Pattern
```
app/api/{resource}.py      # Endpoints with SRS doc comments
app/models/{resource}.py   # SQLModel with validation
app/schemas/{resource}.py  # Pydantic request/response DTOs
app/core/{domain}.py       # Business logic (ledger, auth, moderation)
```

### Frontend Architecture Pattern
```
frontend/src/
├── components/      # Reusable UI (Layout, LocationPicker, TimeSlotPicker, ProtectedRoute)
├── pages/           # Route pages (Login, Register, CreateOffer, OfferDetail, MapView, etc.)
├── services/        # API clients (api.ts: axios config, auth.ts: auth methods)
├── contexts/        # React contexts (AuthContext: global auth state)
├── types/           # TypeScript types matching backend schemas
├── utils/           # Helpers (config, date formatting, location)
└── theme.ts         # Material-UI theme (orange primary, blue secondary)
```

**Frontend Conventions:**
- TanStack Query for API state management (caching, optimistic updates)
- Axios interceptors auto-attach JWT tokens, handle 401 redirects
- Environment config via `.env` with `VITE_` prefix
- React Router v6 for navigation
- Leaflet + OpenStreetMap for maps (no exact addresses per NFR-7)

## Critical Patterns

### 1. Dependency Injection (FastAPI)
```python
from app.core.auth import CurrentUser, AdminUser
from app.core.db import SessionDep  # Annotated[Session, Depends(get_session)]

@router.post("/")
def create_item(
    current_user: CurrentUser,  # Auto-injected authenticated user
    session: SessionDep,        # Auto-injected DB session
) -> ItemResponse:
    ...
```

### 2. Double-Entry Ledger (`app/core/ledger.py`)
**Never** manually update `User.balance` - always use `create_ledger_entry()`:
```python
# Provider CREDIT (earning)
provider_entry = create_ledger_entry(
    session=session, user_id=provider_id, credit=hours, debit=0.0
)
# Requester DEBIT (spending)
requester_entry = create_ledger_entry(
    session=session, user_id=requester_id, debit=hours, credit=0.0
)
```
Ledger entries create audit trail and automatically update user balance.

### 3. Tag Auto-Creation (`app/core/offers_needs.py`)
Tags are auto-created from strings - never require pre-existing tags:
```python
associate_tags_to_offer(session, offer.id, ["gardening", "weekend"])
# Creates tags if they don't exist, associates them
```

### 4. Status Transitions
**Offers/Needs:** `ACTIVE → FULL → EXPIRED/ARCHIVED`
**Participants:** `PENDING → ACCEPTED → COMPLETED`

Always validate state before transitions. Check `accepted_count < capacity` before accepting participants.

### 5. Testing Pattern
Tests use in-memory SQLite with fixtures:
```python
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(email="test@example.com", username="testuser", ...)
    session.add(user)
    session.commit()
    return user

def test_endpoint(client: TestClient, auth_headers: dict):
    response = client.post("/api/v1/offers/", headers=auth_headers, json={...})
    assert response.status_code == 201
```

Auth headers fixture creates JWT tokens with `create_access_token()`.

## Developer Workflow

### Running Locally
```bash
# Start database + backend + frontend (RECOMMENDED)
cd infra && docker-compose up

# OR local backend development
python scripts/init_db.py  # Initialize database
uvicorn app.main:app --reload

# OR use Makefile shortcuts
make run          # Start dev server
make test         # Run tests
make test-cov     # With coverage
make format       # Black + Ruff auto-fix
make lint         # Run ruff linter
```

**Frontend Development:**
```bash
cd frontend
npm install           # Install dependencies
cp .env.example .env  # Configure environment
npm run dev           # Start Vite dev server (http://localhost:5173)
npm run build         # Production build (TypeScript check + bundle)
npm run lint          # ESLint
```

### Docker Services (from infra/)
- **Database**: PostgreSQL on port 5432 (postgres/postgres)
- **Backend**: FastAPI on port 8000 (http://localhost:8000/docs for Swagger)
- **Frontend**: Vite dev server on port 5173
- **Health check**: http://localhost:8000/healthz

### Testing
```bash
pytest tests/                          # All tests
pytest tests/test_offers.py -v        # Specific file
pytest -k "test_create_offer"         # Pattern match
PYTHONPATH=. pytest tests/            # If import issues
```

**Golden Path Test:** See `tests/test_golden_path_need.py` for a comprehensive workflow demonstration showing the complete lifecycle of a Need from creation through completion with TimeBank balance updates.

### Database
- **PostgreSQL** in production/docker (connection pooling disabled via `NullPool`)
- **SQLite** in tests (in-memory)
- Models are SQLModel (SQLAlchemy + Pydantic combined)
- No migrations - uses `SQLModel.metadata.create_all()` for schema generation
- Database initialized via `scripts/init_db.py`

## Configuration (`app/core/config.py`)
Settings use `pydantic-settings` with `.env` support:
```python
from app.core.config import settings

settings.DATABASE_URL  # Auto-loaded from .env or defaults
settings.SECRET_KEY
settings.CORS_ORIGINS  # Comma-separated string auto-parsed to list
```

**Backend .env:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/the_hive
SECRET_KEY=your-secret-key-here
ADMIN_SESSION_SECRET=admin-secret-key
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend .env:**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_MAP_DEFAULT_LAT=41.0082
VITE_MAP_DEFAULT_LNG=28.9784
VITE_MAP_DEFAULT_ZOOM=12
```

## Common Operations

### Adding New Endpoint
1. Create schema in `app/schemas/{resource}.py` (request/response DTOs)
2. Add business logic to `app/core/{domain}.py` if complex
3. Create endpoint in `app/api/{resource}.py` with SRS comments
4. Register router in `app/main.py`
5. Write tests in `tests/test_{resource}.py`

### Authentication
- JWT tokens via `HTTPBearer` security scheme
- Role-based access: `CurrentUser`, `AdminUser`, `ModeratorUser`
- Password hashing uses `bcrypt` (see `app/core/security.py`)

### Location Handling
- **Never store exact addresses** (NFR-7 privacy requirement)
- Use approximate coordinates: `location_lat`, `location_lon`, `location_name`
- Required for non-remote offers/needs

## Code Quality

### Style
- **Black** formatter (100 char line length)
- **Ruff** linter
- Type hints required (Python 3.11+)
- Use `from collections.abc import Generator` not `typing.Generator`

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Enums: `UPPER_CASE` values, `PascalCase` class

### API Response Pattern
Build response objects explicitly to include relationships:
```python
def _build_offer_response(session: Session, offer: Offer) -> OfferResponse:
    tags = get_offer_tags(session, offer.id)
    return OfferResponse(..., tags=tags)
```
Don't rely on SQLModel relationships - fetch explicitly for control.

## Key Files Reference
- `app/main.py` - FastAPI app setup, router registration
- `app/core/db.py` - Database engine, session management
- `app/core/auth.py` - JWT auth, role dependencies
- `app/core/ledger.py` - TimeBank double-entry logic
- `app/core/moderation.py` - Content filtering for comments
- `app/models/associations.py` - Many-to-many tables (OfferTag, NeedTag)
- `frontend/src/services/api.ts` - Axios config with JWT interceptors
- `frontend/src/contexts/AuthContext.tsx` - Global auth state management

## Gotchas
- Session commit/refresh required after inserts for auto-generated IDs
- `CORS_ORIGINS` parsed from comma-separated string via validator
- Database URL needs `postgresql+psycopg://` prefix (auto-converted in `app/core/db.py`)
- Tests need `app.dependency_overrides.clear()` in teardown
- Expired offers/needs currently require manual archiving (no background scheduler yet)
- Frontend uses `localStorage` for JWT tokens - cleared on 401 responses
