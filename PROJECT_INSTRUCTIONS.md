# The Hive - Project Instructions

## Project Overview

**The Hive** is a time-banking community platform that enables users to exchange services using a time-based currency system. The application follows a full-stack architecture with a FastAPI backend and a React TypeScript frontend.

## Architecture

### Technology Stack

**Backend:**
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic v2 for request/response schemas
- **Testing**: pytest with httpx TestClient
- **Code Quality**: Black (100 char line length), Ruff linter
- **Python Version**: 3.11+

**Frontend:**
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) v5
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **Maps**: Leaflet with react-leaflet
- **Date Handling**: date-fns
- **Code Quality**: ESLint with TypeScript

**Infrastructure:**
- **Containerization**: Docker with docker-compose
- **Database**: PostgreSQL
- **Deployment**: Multi-service Docker setup

## Project Structure

```
the_hive/
├── app/                        # FastAPI Backend
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers (REST endpoints)
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User profile endpoints
│   │   ├── offers.py          # Offer CRUD endpoints
│   │   ├── needs.py           # Need CRUD endpoints
│   │   ├── participants.py    # Participant management
│   │   ├── handshake.py       # Service exchange handshake
│   │   ├── search.py          # Search functionality
│   │   ├── ratings.py         # Rating system
│   │   ├── dashboard.py       # Dashboard data
│   │   ├── map.py             # Map visualization endpoints
│   │   ├── forum.py           # Community forum
│   │   ├── notifications.py   # Notification system
│   │   ├── tags.py            # Tag management
│   │   ├── semantic_tags.py   # Semantic tag system
│   │   ├── reports.py         # Reporting system
│   │   └── moderation.py      # Moderation endpoints
│   ├── core/                   # Core application logic
│   │   ├── config.py          # Settings (Pydantic Settings)
│   │   ├── db.py              # Database connection & session management
│   │   ├── security.py        # Password hashing, JWT encoding/decoding
│   │   ├── auth.py            # Authentication dependencies
│   │   ├── logging.py         # Structured JSON logging
│   │   ├── ledger.py          # TimeBank ledger operations
│   │   ├── notifications.py   # Notification service
│   │   ├── websocket.py       # WebSocket support
│   │   ├── moderation.py     # Moderation logic
│   │   ├── offers_needs.py    # Business logic for offers/needs
│   │   └── semantic_tags.py  # Semantic tag processing
│   ├── models/                 # SQLModel database models
│   │   ├── base.py           # Base model classes
│   │   ├── user.py           # User model with roles
│   │   ├── offer.py          # Offer model
│   │   ├── need.py           # Need model
│   │   ├── participant.py    # Participant model
│   │   ├── ledger.py         # LedgerEntry & Transfer models
│   │   ├── rating.py         # Rating model
│   │   ├── tag.py            # Tag model
│   │   ├── semantic_tag.py   # Semantic tag models
│   │   ├── forum.py          # Forum topic model
│   │   ├── report.py         # Report model
│   │   ├── notification.py   # Notification model
│   │   └── associations.py   # Many-to-many association tables
│   └── schemas/                # Pydantic request/response schemas
│       ├── auth.py           # Auth schemas (UserRegister, UserLogin, Token)
│       ├── user.py           # User profile schemas
│       ├── offer.py          # Offer schemas
│       ├── need.py           # Need schemas
│       ├── participant.py   # Participant schemas
│       ├── rating.py         # Rating schemas
│       ├── tag.py            # Tag schemas
│       ├── semantic_tag.py  # Semantic tag schemas
│       ├── forum.py         # Forum schemas
│       ├── report.py        # Report schemas
│       ├── notification.py # Notification schemas
│       ├── dashboard.py     # Dashboard schemas
│       ├── map.py           # Map schemas
│       ├── search.py        # Search schemas
│       ├── ledger.py        # Ledger schemas
│       └── time_slot.py     # Time slot schemas
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.tsx           # Main app component with routing
│   │   ├── main.tsx          # React entry point
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Layout.tsx   # Main layout wrapper
│   │   │   ├── ProtectedRoute.tsx # Auth route guard
│   │   │   └── ...          # Other components
│   │   ├── pages/            # Route page components
│   │   ├── services/         # API client services
│   │   │   ├── api.ts       # Axios instance with interceptors
│   │   │   └── auth.ts      # Auth service
│   │   ├── contexts/         # React contexts (AuthContext, etc.)
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript type definitions
│   │   │   └── index.ts     # Main type exports
│   │   ├── utils/            # Utility functions
│   │   │   ├── config.ts    # Frontend config
│   │   │   ├── date.ts      # Date utilities
│   │   │   ├── location.ts  # Location utilities
│   │   │   └── avatars.ts   # Avatar utilities
│   │   └── theme.ts          # MUI theme configuration
│   ├── package.json          # Frontend dependencies
│   └── tsconfig.json         # TypeScript configuration
├── tests/                     # Backend test suite
│   ├── test_auth.py         # Authentication tests
│   ├── test_needs.py        # Need CRUD tests
│   ├── test_offers.py       # Offer CRUD tests
│   ├── test_handshake.py    # Handshake tests
│   ├── test_ledger.py       # Ledger tests
│   ├── test_ratings.py      # Rating tests
│   ├── test_moderation.py   # Moderation tests
│   └── ...                  # Other test files
├── scripts/                   # Utility scripts
│   ├── init_db.py           # Database initialization
│   └── seed_semantic_tags.py # Seed data scripts
├── infra/                     # Infrastructure
│   └── docker-compose.yml    # Multi-service Docker setup
├── pyproject.toml            # Backend dependencies & config
└── README.md                 # Project documentation
```

## Backend Coding Standards

### FastAPI Route Handlers

1. **Router Structure**: Each feature module has its own router in `app/api/`
   ```python
   from fastapi import APIRouter
   router = APIRouter(prefix="/users", tags=["users"])
   ```

2. **Dependency Injection**: Use FastAPI dependencies for database sessions and authentication
   ```python
   from app.core.auth import CurrentUser
   from app.core.db import SessionDep
   
   @router.get("/me")
   def get_my_profile(
       current_user: CurrentUser,
       session: SessionDep,
   ) -> UserProfileResponse:
       ...
   ```

3. **Response Models**: Always specify `response_model` for type safety and OpenAPI docs
   ```python
   @router.get("/{user_id}", response_model=UserProfileResponse)
   def get_user_profile(...) -> UserProfileResponse:
       ...
   ```

4. **Error Handling**: Use HTTPException with appropriate status codes
   ```python
   from fastapi import HTTPException, status
   
   if not user:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="User not found"
       )
   ```

5. **SRS References**: Include SRS requirement references in docstrings
   ```python
   """
   Get current user's profile.
   
   SRS FR-2: Profile Management
   
   Returns:
       Current user's profile with stats
   """
   ```

### Database Models (SQLModel)

1. **Model Definition**: Use SQLModel with table=True for database tables
   ```python
   from sqlmodel import SQLModel, Field, Relationship
   
   class User(SQLModel, table=True):
       __tablename__ = "users"
       id: Optional[int] = Field(default=None, primary_key=True)
       email: str = Field(unique=True, index=True, max_length=255)
       ...
   ```

2. **Relationships**: Use Relationship for foreign keys
   ```python
   tags: list["UserTag"] = Relationship(back_populates="user")
   ```

3. **Enums**: Use Python Enum for status/role fields
   ```python
   from enum import Enum
   
   class UserRole(str, Enum):
       USER = "user"
       MODERATOR = "moderator"
       ADMIN = "admin"
   ```

4. **Timestamps**: Use `datetime.utcnow` for created_at/updated_at
   ```python
   created_at: datetime = Field(default_factory=datetime.utcnow)
   updated_at: datetime = Field(default_factory=datetime.utcnow)
   ```

### Pydantic Schemas

1. **Request Schemas**: Use BaseModel for request validation
   ```python
   from pydantic import BaseModel, Field
   
   class UserProfileUpdate(BaseModel):
       full_name: str | None = Field(None, max_length=255)
       description: str | None = Field(None, max_length=1000)
   ```

2. **Response Schemas**: Use `model_config = {"from_attributes": True}` for ORM conversion
   ```python
   class UserProfileResponse(BaseModel):
       id: int
       username: str
       ...
       model_config = {"from_attributes": True}
   ```

3. **Field Validation**: Use Pydantic validators for complex validation
   ```python
   from pydantic import field_validator
   
   @field_validator("email")
   @classmethod
   def validate_email(cls, v: str) -> str:
       ...
   ```

### Authentication & Authorization

1. **JWT Tokens**: Use `app.core.security` for token encoding/decoding
2. **Password Hashing**: Use bcrypt via `get_password_hash()` and `verify_password()`
3. **Dependencies**: Use `CurrentUser`, `AdminUser`, `ModeratorUser` for role-based access
   ```python
   from app.core.auth import CurrentUser, ModeratorUser
   
   @router.get("/moderator-only")
   def moderator_endpoint(current_user: ModeratorUser):
       ...
   ```

### Database Queries

1. **SQLModel Queries**: Use SQLModel's select() for queries
   ```python
   from sqlmodel import select
   
   statement = select(User).where(User.username == username)
   user = session.exec(statement).first()
   ```

2. **Session Management**: Always use `SessionDep` dependency, never create sessions manually
3. **Transactions**: Use try/except with rollback for error handling
   ```python
   try:
       session.add(user)
       session.commit()
       session.refresh(user)
   except Exception:
       session.rollback()
       raise
   ```

### Logging

1. **Structured Logging**: Use JSON-formatted logs via `app.core.logging`
   ```python
   from app.core.logging import get_logger
   
   logger = get_logger(__name__)
   logger.info("User created", extra={"extra_fields": {"user_id": user.id}})
   ```

2. **Log Levels**: Use appropriate levels (INFO, WARNING, ERROR)

### Configuration

1. **Settings**: Use Pydantic Settings in `app/core/config.py`
   ```python
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       DATABASE_URL: str
       SECRET_KEY: str
       ...
   ```

2. **Environment Variables**: Load from `.env` file (see `SettingsConfigDict`)

### Testing

1. **Test Structure**: Use pytest with fixtures for database sessions
   ```python
   @pytest.fixture(name="session")
   def session_fixture():
       engine = create_engine("sqlite:///:memory:", ...)
       SQLModel.metadata.create_all(engine)
       with Session(engine) as session:
           yield session
   ```

2. **Test Client**: Use FastAPI TestClient with dependency overrides
   ```python
   @pytest.fixture(name="client")
   def client_fixture(session: Session):
       app.dependency_overrides[get_session] = lambda: session
       client = TestClient(app)
       yield client
       app.dependency_overrides.clear()
   ```

3. **Test Naming**: Use descriptive test function names starting with `test_`
   ```python
   def test_register_user(client: TestClient):
       """Test user registration (SRS FR-1.1, FR-1.2)."""
       ...
   ```

## Frontend Coding Standards

### React Components

1. **Component Structure**: Use functional components with TypeScript
   ```typescript
   interface Props {
     userId: number
   }
   
   export default function UserProfile({ userId }: Props) {
     ...
   }
   ```

2. **File Naming**: Use PascalCase for component files (e.g., `UserProfile.tsx`)

### TypeScript Types

1. **Type Definitions**: Define types in `src/types/index.ts` matching backend schemas
   ```typescript
   export interface User {
     id: number
     username: string
     email: string
     balance: number
     ...
   }
   ```

2. **Type Safety**: Always type function parameters and return values
   ```typescript
   function getUser(id: number): Promise<User> {
     ...
   }
   ```

### API Client

1. **Axios Instance**: Use the configured `apiClient` from `src/services/api.ts`
   ```typescript
   import apiClient from '@/services/api'
   
   export const getUser = async (id: number): Promise<User> => {
     const response = await apiClient.get(`/users/${id}`)
     return response.data
   }
   ```

2. **Error Handling**: Axios interceptors handle 401 redirects automatically
3. **Request Interceptors**: JWT token is automatically attached from localStorage

### State Management

1. **Server State**: Use TanStack Query for API data
   ```typescript
   import { useQuery } from '@tanstack/react-query'
   
   const { data, isLoading } = useQuery({
     queryKey: ['user', userId],
     queryFn: () => getUser(userId)
   })
   ```

2. **Client State**: Use React Context for global state (e.g., AuthContext)
   ```typescript
   const { user, login, logout } = useAuth()
   ```

### Routing

1. **React Router**: Use React Router v6 with nested routes
   ```typescript
   <Routes>
     <Route path="/" element={<Layout />}>
       <Route index element={<HomePage />} />
       <Route path="profile/:username" element={<ProfilePage />} />
     </Route>
   </Routes>
   ```

2. **Protected Routes**: Use `ProtectedRoute` component for auth-required pages
   ```typescript
   <Route path="profile/me" element={
     <ProtectedRoute>
       <MyProfile />
     </ProtectedRoute>
   } />
   ```

### UI Components

1. **Material-UI**: Use MUI components for consistent styling
   ```typescript
   import { Button, TextField, Box } from '@mui/material'
   ```

2. **Theme**: Use centralized theme from `src/theme.ts`
   ```typescript
   import { ThemeProvider } from '@mui/material/styles'
   import theme from './theme'
   ```

3. **Responsive Design**: Use MUI's responsive breakpoints
   ```typescript
   <Box sx={{ display: { xs: 'block', md: 'flex' } }}>
   ```

### Code Organization

1. **Imports**: Group imports (external, internal, types)
   ```typescript
   import { useState } from 'react'
   import { Button } from '@mui/material'
   import { getUser } from '@/services/api'
   import type { User } from '@/types'
   ```

2. **Path Aliases**: Use `@/` alias for `src/` directory (configured in tsconfig.json)

## API Design Patterns

### RESTful Endpoints

1. **URL Structure**: `/api/v1/{resource}/{id?}/{action?}`
   - `GET /api/v1/users` - List users
   - `GET /api/v1/users/{id}` - Get user
   - `PUT /api/v1/users/me` - Update current user
   - `POST /api/v1/users/me/avatar` - Upload avatar

2. **HTTP Methods**: 
   - `GET` for retrieval
   - `POST` for creation
   - `PUT` for full updates
   - `DELETE` for deletion

3. **Status Codes**:
   - `200` - Success
   - `201` - Created
   - `400` - Bad Request
   - `401` - Unauthorized
   - `403` - Forbidden
   - `404` - Not Found
   - `500` - Internal Server Error

### Pagination

1. **Query Parameters**: Use `skip` and `limit`
   ```python
   skip: int = Query(0, ge=0)
   limit: int = Query(20, ge=1, le=100)
   ```

2. **Response Format**:
   ```python
   class PaginatedResponse(BaseModel):
       items: list[Item]
       total: int
       skip: int
       limit: int
   ```

### Error Responses

1. **Error Format**: Consistent error response structure
   ```json
   {
     "detail": "Error message here"
   }
   ```

## Code Quality

### Python

1. **Formatting**: Black with 100 character line length
2. **Linting**: Ruff linter
3. **Type Hints**: Use type hints for all function parameters and return values
4. **Docstrings**: Include docstrings for public functions/classes with SRS references

### TypeScript

1. **Linting**: ESLint with TypeScript rules
2. **Formatting**: Prettier (if configured)
3. **Type Safety**: Strict TypeScript mode enabled

## Environment Configuration

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/the_hive
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_MAP_DEFAULT_LAT=41.0082
VITE_MAP_DEFAULT_LNG=28.9784
VITE_MAP_DEFAULT_ZOOM=12
```

## Development Workflow

1. **Backend Development**:
   ```bash
   pip install -e .
   python scripts/init_db.py
   uvicorn app.main:app --reload
   ```

2. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Testing**:
   ```bash
   pytest tests/
   ```

4. **Docker Development**:
   ```bash
   cd infra
   docker-compose up
   ```

## Key Features & Business Logic

### TimeBank System
- Users start with 5 hours balance (SRS FR-7.1)
- Double-entry ledger system for transactions
- Hours transferred during handshake completion

### Offers & Needs
- Auto-expiration based on `expires_at`
- Capacity management (max participants)
- Status: ACTIVE, FULL, EXPIRED, ARCHIVED

### Authentication
- JWT tokens with 30-minute access token, 7-day refresh token
- Role-based access: User, Moderator, Admin
- Password hashing with bcrypt

### Moderation
- User suspension and banning
- Report system for content moderation
- Moderator dashboard for review

### Search & Tags
- Semantic tag hierarchy
- Full-text search on offers/needs
- Tag-based filtering

## Best Practices

1. **Always validate input** using Pydantic schemas
2. **Use dependency injection** for database sessions and auth
3. **Handle errors gracefully** with appropriate HTTP status codes
4. **Log important operations** with structured logging
5. **Write tests** for new features
6. **Reference SRS requirements** in code comments/docstrings
7. **Keep components small and focused** (single responsibility)
8. **Use TypeScript types** to match backend schemas
9. **Follow RESTful conventions** for API endpoints
10. **Use environment variables** for configuration

## Common Patterns

### Creating a New API Endpoint

1. Define Pydantic schemas in `app/schemas/`
2. Create route handler in `app/api/`
3. Add router to `app/main.py`
4. Write tests in `tests/`
5. Update frontend types in `frontend/src/types/index.ts`
6. Create API service function in `frontend/src/services/`
7. Create React component/page if needed

### Adding a New Database Model

1. Create model in `app/models/`
2. Import in `app/core/db.py` init_db()
3. Create Pydantic schemas in `app/schemas/`
4. Create API endpoints in `app/api/`
5. Write tests

### Adding Frontend Feature

1. Define TypeScript types in `src/types/index.ts`
2. Create API service in `src/services/`
3. Create React component/page
4. Add route in `App.tsx`
5. Use TanStack Query for data fetching

---

**Note**: This document should be updated as the project evolves. Always refer to existing code patterns when implementing new features.

