# Docker Setup Guide

## Updated Dockerfile

The Dockerfile now includes:
- ✅ `scripts/` directory
- ✅ `tests/` directory
- ✅ All necessary project files

## Rebuild the Container

After updating the Dockerfile, you need to rebuild the container:

```bash
# Stop existing containers
cd infra
docker-compose down

# Rebuild the image
docker-compose build

# Start containers
docker-compose up -d

# Check if it's running
docker-compose ps
```

## Verify Scripts are Available

```bash
# Enter the container
docker-compose exec app bash

# Check if scripts directory exists
ls -la /app/scripts/

# You should see:
# - init_db.py
# - sanity_check_auth.py
# - test_auth_quick.sh
# - verify_auth_code.py
```

## Running Scripts in Docker

### Initialize Database
```bash
docker-compose exec app python scripts/init_db.py
```

### Run Auth Sanity Check
```bash
docker-compose exec app python scripts/sanity_check_auth.py
```

### Run Quick Auth Tests
```bash
docker-compose exec app bash scripts/test_auth_quick.sh
```

### Run Pytest
```bash
# All auth tests
docker-compose exec app pytest tests/test_auth.py -v

# All RBAC tests
docker-compose exec app pytest tests/test_rbac.py -v

# All tests
docker-compose exec app pytest tests/ -v
```

## Volume Mounts

The docker-compose.yml now mounts these directories as volumes:
- `../app:/app/app` - Live code reload
- `../scripts:/app/scripts` - Access to scripts
- `../tests:/app/tests` - Access to tests

This means you can edit files locally and they'll be available in the container immediately (no rebuild needed for changes).

## Common Commands

```bash
# View logs
docker-compose logs -f app

# Enter container shell
docker-compose exec app bash

# Run Python in container
docker-compose exec app python -c "print('Hello from Docker')"

# Check database connection
docker-compose exec app python -c "from app.core.db import check_db_connection; print(check_db_connection())"

# Run migrations (when ready)
docker-compose exec app alembic upgrade head

# Stop containers
docker-compose down

# Stop and remove volumes (careful - deletes database!)
docker-compose down -v
```

## Troubleshooting

### "No such file or directory: scripts"

**Solution**: Rebuild the container after Dockerfile changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### "Permission denied" for scripts

**Solution**: Make scripts executable
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Database connection issues

**Solution**: Wait for database to be ready
```bash
# Check database is healthy
docker-compose ps

# Wait for db health check
docker-compose up -d db
sleep 10
docker-compose up -d app
```

### Import errors in container

**Solution**: Ensure dependencies are installed
```bash
docker-compose exec app pip list
docker-compose exec app pip install -e .
```

## Quick Start Workflow

```bash
# 1. Start everything
cd infra
docker-compose up -d

# 2. Wait for services to be ready (check logs)
docker-compose logs -f

# 3. Initialize database
docker-compose exec app python scripts/init_db.py

# 4. Run sanity checks
docker-compose exec app python scripts/sanity_check_auth.py

# 5. Run tests
docker-compose exec app pytest tests/test_auth.py -v

# 6. Access API
curl http://localhost:8000/healthz
curl http://localhost:8000/docs

# 7. Test auth endpoints
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"Password123!"}'
```

## Development vs Production

### Development (current setup)
- Volume mounts for live reload
- Debug mode enabled
- Simplified secrets

### Production (future)
- No volume mounts (baked into image)
- Environment variables from secure store
- HTTPS only
- Production secrets
- Resource limits

## Next Steps

1. ✅ Rebuild container with scripts
2. ✅ Initialize database
3. ✅ Run auth sanity checks
4. ✅ Test API endpoints
5. ⏭️ Implement next feature (Offers/Needs)
