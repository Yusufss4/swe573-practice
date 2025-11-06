# Database Setup and Usage

## Overview

This application uses:
- **SQLModel**: ORM combining SQLAlchemy 2.0 and Pydantic
- **PostgreSQL**: Database (via psycopg3 driver)
- **Alembic**: Database migrations

## Quick Start

### 1. Configure Database URL

Edit `.env` file:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/the_hive
```

### 2. Create Database

```bash
# Using createdb
createdb the_hive

# Or using psql
psql -U postgres -c "CREATE DATABASE the_hive;"
```

### 3. Test Connection

```bash
# Via Python
python -c "from app.core.db import check_db_connection; print(check_db_connection())"

# Via health endpoint
curl http://localhost:8000/healthz
```

## Using Database Sessions

### In FastAPI Endpoints

```python
from fastapi import APIRouter
from app.core.db import SessionDep  # Type alias for dependency
from sqlmodel import select
from app.models.user import User

router = APIRouter()

@router.get("/users")
async def get_users(session: SessionDep):
    """SessionDep automatically injects database session."""
    users = session.exec(select(User)).all()
    return users
```

### Manual Session Usage

```python
from app.core.db import engine
from sqlmodel import Session, select

with Session(engine) as session:
    statement = select(User).where(User.email == "test@example.com")
    user = session.exec(statement).first()
```

## Creating Models

### Basic Model

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    """User model."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### With Relationships

```python
from typing import Optional, List
from sqlmodel import Field, Relationship

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    # One-to-many relationship
    users: List["User"] = Relationship(back_populates="team")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(foreign_key="team.id")
    
    # Many-to-one relationship
    team: Optional[Team] = Relationship(back_populates="users")
```

## Database Operations

### Create

```python
def create_user(session: SessionDep, email: str, username: str):
    user = User(email=email, username=username)
    session.add(user)
    session.commit()
    session.refresh(user)  # Get auto-generated fields
    return user
```

### Read

```python
from sqlmodel import select

# Get all
users = session.exec(select(User)).all()

# Get one
user = session.exec(select(User).where(User.id == 1)).first()

# Get by primary key
user = session.get(User, 1)

# With filters
statement = select(User).where(User.email.contains("@example.com"))
users = session.exec(statement).all()

# With pagination
statement = select(User).offset(0).limit(10)
users = session.exec(statement).all()
```

### Update

```python
user = session.get(User, 1)
user.email = "new@example.com"
session.add(user)
session.commit()
session.refresh(user)
```

### Delete

```python
user = session.get(User, 1)
session.delete(user)
session.commit()
```

## Connection Configuration

### Engine Settings

Located in `app/core/db.py`:

```python
engine = create_engine(
    database_url,
    echo=settings.DEBUG,  # Log SQL in debug mode
    pool_pre_ping=True,   # Verify connections
    poolclass=NullPool,   # Disable pooling (dev)
)
```

### Production Settings

For production, enable connection pooling:

```python
engine = create_engine(
    database_url,
    pool_size=5,          # Number of connections to maintain
    max_overflow=10,      # Additional connections allowed
    pool_pre_ping=True,
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

## Troubleshooting

### Connection Errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U postgres -d the_hive -c "SELECT version();"

# Test from Python
python -c "from app.core.db import check_db_connection; print(check_db_connection())"
```

### Driver Issues

Make sure psycopg is installed:
```bash
pip install psycopg[binary]
```

### Permission Errors

```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE the_hive TO postgres;
```

## Best Practices

1. **Use SessionDep for endpoints**: Type-safe and automatic cleanup
2. **Use context managers**: Ensures sessions are closed
3. **Commit explicitly**: Don't rely on auto-commit
4. **Handle exceptions**: Rollback on errors
5. **Use indexes**: For frequently queried columns
6. **Lazy load carefully**: Avoid N+1 query problems

## Next Steps

1. Create your first model in `app/models/`
2. Set up Alembic migrations (see MIGRATIONS.md)
3. Add database initialization to startup
4. Create repository pattern for data access
5. Add database tests

## Resources

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg3 Documentation](https://www.psycopg.org/psycopg3/)
