# 🐳 Docker Quick Start Guide

## The Easiest Way to Run The Hive

This guide shows you how to run the entire application (database, backend, and frontend) using Docker.

## Prerequisites

- Docker installed and running
- Docker Compose installed (usually comes with Docker Desktop)

Check if you have them:
```bash
docker --version
docker-compose --version
```

## 🚀 Start Everything (Development Mode)

From the backend's infra directory, run:

```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose up
```

This single command starts:
- ✅ **PostgreSQL database** on port 5432
- ✅ **FastAPI backend** on port 8000  
- ✅ **React frontend** on port 3000 (with hot reload!)

**First time setup?** It will take 2-5 minutes to download images and build. Subsequent starts are much faster!

### Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

### View Logs

```bash
# All services
docker-compose logs -f

# Just frontend
docker-compose logs -f frontend

# Just backend
docker-compose logs -f app
```

### Stop Everything

Press `Ctrl+C` in the terminal, or:

```bash
docker-compose down
```

## 🎨 What You Get

### Development Features
- ✅ **Hot Reload** - Edit code, see changes instantly
- ✅ **No npm install** - Dependencies installed in container
- ✅ **Isolated Environment** - No conflicts with your system
- ✅ **Database Included** - PostgreSQL ready to use
- ✅ **Networking** - Services can talk to each other

### Services Running

```
┌──────────────────────────────────────┐
│  PostgreSQL Database (port 5432)     │
│  - Auto-initialized on first run     │
│  - Data persisted in Docker volume   │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  FastAPI Backend (port 8000)         │
│  - API documentation at /docs        │
│  - Health check at /healthz          │
│  - Code hot-reloaded                 │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  React Frontend (port 3000)          │
│  - Vite dev server with hot reload   │
│  - Source maps for debugging         │
│  - Fast refresh                      │
└──────────────────────────────────────┘
```

## 🔄 Common Workflows

### Making Changes to Code

**Backend changes:**
1. Edit Python files in `the_hive/app/`
2. Save the file
3. Backend automatically reloads
4. Check logs: `docker-compose logs -f app`

**Frontend changes:**
1. Edit files in `the_hive_frontend/src/`
2. Save the file
3. Browser automatically refreshes
4. Check logs: `docker-compose logs -f frontend`

### Installing New Dependencies

**Backend (Python):**
```bash
# Add to the_hive/pyproject.toml, then:
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose build app
docker-compose up
```

**Frontend (npm):**
```bash
# Add to the_hive_frontend/package.json, then:
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose build frontend
docker-compose up
```

### Running Tests

**Backend tests:**
```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose run --rm app pytest tests/ -v
```

**Frontend tests:**
```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose run --rm frontend npm test
```

### Database Operations

**View database:**
```bash
docker exec -it the_hive_db psql -U postgres -d the_hive
```

**Reset database:**
```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose down -v  # ⚠️ This deletes all data!
docker-compose up
```

## 🏭 Production Mode

For production deployment with optimized builds:

```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose -f docker-compose.prod.yml up
```

**Differences:**
- Frontend served by nginx (faster, smaller)
- No hot reload (optimized for production)
- Frontend on port 80 (standard HTTP port)
- Minified and optimized assets

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `bind: address already in use`

**Solution:** Stop the conflicting service:
```bash
# Find what's using the port
lsof -i :3000  # or :8000 or :5432

# Kill it or change port in docker-compose.yml
```

### Permission Errors

**Error:** Permission denied

**Solution:**
```bash
sudo docker-compose up
# or
sudo usermod -aG docker $USER
# Then logout and login again
```

### Frontend Can't Connect to Backend

**Check:**
1. Backend is running: `docker-compose ps`
2. Backend is healthy: `curl http://localhost:8000/healthz`
3. CORS is configured correctly

### Container Exits Immediately

**Debug:**
```bash
# Check logs
docker-compose logs frontend

# Try rebuilding
docker-compose build --no-cache frontend
docker-compose up
```

### Changes Not Reflected

**Solution:**
1. Hard refresh browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. Restart container: `docker-compose restart frontend`
3. Rebuild: `docker-compose up --build frontend`

## 🧹 Cleanup

### Remove Containers (Keep Data)
```bash
docker-compose down
```

### Remove Everything (Including Data)
```bash
docker-compose down -v
```

### Remove Images Too
```bash
docker-compose down --rmi all
```

### Full Cleanup
```bash
docker-compose down -v --rmi all
docker system prune -a --volumes
```

## 📊 Useful Commands

```bash
# View running containers
docker-compose ps

# View all logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Restart a service
docker-compose restart frontend

# Rebuild a service
docker-compose build frontend

# Shell into a container
docker exec -it the_hive_frontend sh
docker exec -it the_hive_app bash
docker exec -it the_hive_db psql -U postgres -d the_hive

# Check resource usage
docker stats
```

## 💡 Tips

### Speed Up Rebuilds
- Only rebuild the service you changed
- Use `--no-cache` only when really needed

### Save Resources
- Run only what you need: `docker-compose up frontend app`
- Stop when not in use: `docker-compose down`

### Development Workflow
1. Start: `docker-compose up`
2. Develop: Edit code, it auto-reloads
3. Test: Browser at localhost:3000
4. Debug: Check logs with `docker-compose logs -f`
5. Stop: `Ctrl+C` or `docker-compose down`

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start all | `docker-compose up` |
| Start in background | `docker-compose up -d` |
| Stop all | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Rebuild | `docker-compose up --build` |
| Clean start | `docker-compose down -v && docker-compose up` |
| Shell access | `docker exec -it the_hive_frontend sh` |
| Run tests | `docker-compose run --rm app pytest` |

## 🆘 Need More Help?

- **Docker Issues**: Check `DOCKER.md` in the frontend directory
- **Setup Details**: Check `SETUP_GUIDE.md` in the frontend directory
- **API Documentation**: http://localhost:8000/docs when running
- **Docker Docs**: https://docs.docker.com/

## 🎉 You're All Set!

Just run:
```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose up
```

Then open http://localhost:3000 and start developing! 🚀
