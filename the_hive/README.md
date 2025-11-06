# The Hive 🐝

A clean, production-ready FastAPI backend application with PostgreSQL database support.

## 🏗️ Architecture

This project follows the "All-in-FastAPI" approach with a well-organized structure:

```
the_hive/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes and endpoints
│   │   └── __init__.py
│   ├── core/                   # Core application configuration
│   │   ├── __init__.py
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   └── logging.py          # JSON-structured logging
│   ├── models/                 # SQLModel database models
│   │   └── __init__.py
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   └── __init__.py
│   ├── services/               # Business logic layer
│   │   └── __init__.py
│   ├── admin/                  # Admin panel (sqladmin)
│   │   └── __init__.py
│   ├── auth/                   # Authentication & authorization
│   │   └── __init__.py
│   └── moderation/             # Content moderation
│       └── __init__.py
├── migrations/                 # Alembic database migrations
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_health.py
├── infra/                      # Infrastructure configs (Docker, etc.)
├── pyproject.toml              # Project dependencies
├── .env.example                # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Features

- ✅ **FastAPI** - Modern, fast web framework
- ✅ **Uvicorn** - ASGI server with auto-reload
- ✅ **SQLModel** - SQL databases with Python type hints
- ✅ **PostgreSQL** - Robust relational database
- ✅ **Alembic** - Database migration tool
- ✅ **Pydantic Settings** - Type-safe configuration management
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **SQLAdmin** - Database admin interface
- ✅ **Structured Logging** - JSON-formatted logs
- ✅ **Health Check** - `/healthz` endpoint for monitoring
- ✅ **CORS** - Cross-Origin Resource Sharing support
- ✅ **Pytest** - Comprehensive testing framework
- ✅ **Docker-ready** - Easy containerization

## 📋 Requirements

- Python 3.11+
- PostgreSQL 14+
- pip or uv package manager

## 🛠️ Setup

### 1. Clone and Navigate

```bash
cd the_hive
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
# Or for development with extra tools:
pip install -e ".[dev]"
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**Important:** Update these values in `.env`:
- `DATABASE_URL` - Your PostgreSQL connection string
- `SECRET_KEY` - Generate a strong secret key
- `ADMIN_SESSION_SECRET` - Generate another secret key

### 5. Setup Database

Make sure PostgreSQL is running and create the database:

```bash
createdb the_hive
# Or using psql:
# psql -U postgres -c "CREATE DATABASE the_hive;"
```

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## 📊 Health Check

The application includes a health check endpoint for monitoring:

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "healthy",
  "app": "the_hive",
  "environment": "development",
  "version": "0.1.0"
}
```

## 🔧 Configuration

Configuration is managed through environment variables using `pydantic-settings`. See `.env.example` for all available options.

Key settings:
- `APP_ENV`: `development`, `staging`, or `production`
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `ADMIN_SESSION_SECRET`: Admin panel session key
- `CORS_ORIGINS`: Allowed CORS origins

## 📝 Logging

The application uses structured JSON logging for easy parsing and analysis:

```json
{
  "timestamp": "2024-01-01T12:00:00.000000Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "Starting application",
  "module": "main",
  "function": "lifespan",
  "line": 25
}
```

## 🐳 Docker Deployment

(To be added in `infra/` directory)

```dockerfile
# Example Dockerfile structure
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗄️ Database Migrations

Initialize Alembic (first time):

```bash
alembic init migrations
```

Create a migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

## 🔐 Security

- JWT-based authentication ready
- Password hashing with bcrypt
- Environment-based secrets
- CORS protection
- SQL injection protection via SQLModel

## 🤝 Contributing

1. Follow the existing code structure
2. Write tests for new features
3. Use type hints
4. Follow PEP 8 style guide
5. Update documentation

## 📄 License

MIT License

## 🆘 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using FastAPI**
