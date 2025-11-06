# Quick Start Guide - The Hive 🐝

## Instant Setup (3 Steps)

### 1. Install Dependencies
```bash
cd the_hive
pip install -e .
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 3. Run the Application
```bash
./start.sh
# OR
uvicorn app.main:app --reload
# OR
make run
```

## Verify Installation

### Test the Health Endpoint
```bash
curl http://localhost:8000/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "app": "the_hive",
  "environment": "development",
  "version": "0.1.0"
}
```

### Run Tests
```bash
make test
# OR
pytest tests/ -v
```

### Access API Documentation
Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Using Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev          # Install with dev dependencies
make test         # Run tests
make test-cov     # Run tests with coverage
make run          # Start development server
make clean        # Clean cache files
```

## Using Docker

```bash
# Start with Docker Compose (includes PostgreSQL)
cd infra
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## Project Structure Overview

```
the_hive/
├── app/
│   ├── main.py          # FastAPI app + /healthz endpoint
│   ├── core/
│   │   ├── config.py    # Settings (pydantic-settings)
│   │   └── logging.py   # JSON logging
│   ├── api/            # Future: API routes
│   ├── models/         # Future: Database models
│   ├── schemas/        # Future: Pydantic schemas
│   ├── services/       # Future: Business logic
│   ├── auth/           # Future: Authentication
│   ├── admin/          # Future: Admin panel
│   └── moderation/     # Future: Content moderation
├── tests/              # Test suite
├── infra/              # Docker configs
├── migrations/         # Alembic migrations
└── pyproject.toml      # Dependencies
```

## Next Steps

1. **Add Database Models**: Create SQLModel models in `app/models/`
2. **Setup Alembic**: Initialize database migrations
3. **Create API Routes**: Add endpoints in `app/api/`
4. **Add Authentication**: Implement JWT auth in `app/auth/`
5. **Setup Admin Panel**: Configure sqladmin in `app/admin/`

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Module Import Errors
```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/the_hive:$PYTHONPATH
# OR use pytest from project root
cd the_hive && pytest
```

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Create database: `createdb the_hive`

## Requirements

- ✅ Python 3.11+
- ✅ PostgreSQL 14+ (for production)
- ✅ pip or uv package manager

## Support

Check the main [README.md](README.md) for detailed documentation.

---

**Happy coding! 🐝**
