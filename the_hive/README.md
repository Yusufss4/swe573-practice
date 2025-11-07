# The Hive 🐝

A time-banking community platform backend built with FastAPI.

## 🏗️ Architecture

```
the_hive/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── api/                    # API endpoints (auth, offers, needs, users)
│   ├── core/                   # Core (config, db, security, auth, logging)
│   ├── models/                 # SQLModel database models
│   └── schemas/                # Pydantic request/response schemas
├── migrations/                 # Alembic migrations
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
├── infra/                      # Docker configuration
└── pyproject.toml              # Dependencies
```

## 🚀 Quick Start

### With Docker (Recommended)

```bash
cd infra
docker compose up
```

API available at http://localhost:8000

### Local Development

```bash
# Install dependencies
pip install -e .

# Setup database
python scripts/init_db.py

# Run server
uvicorn app.main:app --reload
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

## 🧪 Testing

```bash
pytest tests/
```

## � Key Features

- JWT authentication with role-based access control
- Offers and Needs CRUD with auto-expiration
- Tag system with auto-creation
- TimeBank balance tracking
- PostgreSQL database
- Docker deployment ready

## 🔧 Configuration

Create `.env` file or use environment variables:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/the_hive
SECRET_KEY=your-secret-key-here
```

## 📄 License

MIT License
