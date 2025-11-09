# The Hive 🐝

A time-banking community platform - Full-stack application with FastAPI backend and React frontend.

## 🏗️ Architecture

```
the_hive/
├── app/                        # FastAPI Backend
│   ├── main.py                 # FastAPI application
│   ├── api/                    # API endpoints (auth, offers, needs, users)
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
│   ├── Dockerfile              # Frontend Docker config
│   └── package.json            # Frontend dependencies
├── tests/                      # Backend test suite
├── scripts/                    # Utility scripts
├── infra/                      # Docker orchestration
│   └── docker-compose.yml      # Multi-service setup
└── pyproject.toml              # Backend dependencies
```

## 🚀 Quick Start

### With Docker (Recommended)

```bash
cd infra
docker-compose up
```

Services available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Database**: PostgreSQL on port 5432

### Local Development

#### Backend
```bash
# Install dependencies
pip install -e .

# Setup database
python scripts/init_db.py

# Run server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Copy environment config
cp .env.example .env

# Start dev server
npm run dev
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

## 🧪 Testing

### Backend Tests
```bash
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test  # (To be implemented)
```

## 💡 Key Features

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

## 🔧 Configuration

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

## 📄 License

MIT License
