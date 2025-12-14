# The Hive

A time-banking community platform - Full-stack application with FastAPI backend and React frontend.

## Architecture

```
the_hive/
├── app/                        # FastAPI Backend
│   ├── main.py                 # FastAPI application
│   ├── api/                    # API endpoints
│   ├── core/                   # Core (config, db, security, auth, logging)
│   ├── models/                 # SQLModel database models
│   └── schemas/                # Pydantic request/response schemas
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route pages
│   │   ├── services/           # API clients
│   │   ├── contexts/           # React contexts
│   │   └── types/              # TypeScript types
│   └── package.json            # Frontend dependencies
├── tests/                      # Backend test suite
├── scripts/                    # Utility scripts
│   ├── init_db.py             # Database initialization
│   └── seed_semantic_tags.py  # Semantic tags seeding
├── infra/                      # Docker orchestration
│   └── docker-compose.yml      # Multi-service setup
└── pyproject.toml              # Backend dependencies
```

## Quick Start

### Using Docker

```bash
cd the_hive/infra
docker compose up
```

Services available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: PostgreSQL on port 5433

## Database Seeding

### Initialize Database

The database initialization script creates all tables and seeds comprehensive test data including:
- 10 test users (including 1 moderator)
- 15 tags across various categories
- 15 active offers with various configurations
- 12 needs with various configurations
- Participants/applications for handshake workflow
- Ratings for completed exchanges
- Forum topics and comments
- Ledger entries

**Run the initialization script:**

```bash
cd the_hive/infra
docker compose exec backend python scripts/init_db.py
```

**Reset and reseed the database:**

```bash
cd the_hive/infra
docker compose exec backend python scripts/init_db.py --reset
```

### Seed Semantic Tags

The semantic tags seeding script creates a hierarchical tag system with parent-child relationships and synonyms.

**Run the semantic tags seeding script:**

```bash
cd the_hive/infra
docker compose exec backend python scripts/seed_semantic_tags.py
```

**What it creates:**
- Top-level categories: physical-work, digital-work, creative-work, education, household
- Subcategories with parent relationships (e.g., gardening -> lawn-mowing, pruning, planting)
- Synonym relationships (e.g., programming <-> coding)
- Tag aliases for flexible searching

**Note:** This script is idempotent - it won't create duplicates if run multiple times.

## Running Tests

### Using Docker

```bash
cd the_hive/infra
docker compose exec backend pytest tests/ -v --tb=short
```

Or use the test script:

```bash
cd the_hive
./run_tests.sh
```

### Test Coverage

The test suite includes:
- Authentication tests
- Forum tests
- Golden path tests
- Handshake tests
- Health checks
- Ledger tests
- Map tests
- Moderation tests
- Needs tests
- Notifications tests
- Offers tests
- Participants tests
- Ratings tests
- RBAC tests
- Search tests
- Social media tests
- Time slots tests

## Configuration

### Backend Environment Variables

The backend uses environment variables configured in the docker-compose.yml file. Key variables include:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `CORS_ORIGINS`: Allowed CORS origins

### Frontend Environment Variables

The frontend uses environment variables configured in the docker-compose.yml file. Key variables include:
- `VITE_API_BASE_URL`: Backend API base URL
- `VITE_MAP_DEFAULT_LAT`: Default map latitude
- `VITE_MAP_DEFAULT_LNG`: Default map longitude
- `VITE_MAP_DEFAULT_ZOOM`: Default map zoom level

## Default Test Users

After seeding the database, you can log in with:

**Regular Users (all use password: `UserPass123!`):**
- Username: `alice`
- Username: `bob`
- Username: `carol`
- Username: `david`
- Username: `emma`
- Username: `frank`
- Username: `grace`
- Username: `henry`
- Username: `iris`
- Username: `jack`

**Moderator:**
- Username: `moderator`
- Password: `ModeratorPass123!`

All users start with 5 hours in their TimeBank balance.

## Key Features

### Backend (FastAPI)
- JWT authentication with role-based access control (User/Moderator/Admin)
- Offers and Needs CRUD with auto-expiration and capacity management
- Handshake mechanism for service exchange
- TimeBank ledger with double-entry bookkeeping
- Tag system with auto-creation and semantic hierarchy
- Comment moderation and reporting
- Badge system for user recognition
- Community forum (Discussions & Events)
- PostgreSQL database with SQLModel

### Frontend (React + TypeScript)
- Material-UI component library
- React Router for navigation
- TanStack Query for API state management
- React Context for authentication
- TypeScript for type safety
- Leaflet maps for geographic visualization
- Responsive design

## License

MIT License
