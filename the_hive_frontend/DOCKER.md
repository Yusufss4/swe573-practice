# Docker Setup for The Hive Frontend

This directory contains Docker configurations for running the frontend in both development and production modes.

## 🐳 Docker Files Overview

- **Dockerfile** - Production build (multi-stage with nginx)
- **Dockerfile.dev** - Development build (with hot reload)
- **docker-compose.yml** - Standalone frontend compose file
- **nginx.conf** - Nginx configuration for production
- **.dockerignore** - Files to exclude from Docker build

## 🚀 Quick Start

### Option 1: Run with Backend (Recommended)

The easiest way is to run everything from the backend's infra directory:

```bash
cd /home/yusufss/swe573-practice/the_hive/infra

# Development mode (with hot reload)
docker-compose up

# This starts:
# - PostgreSQL database (port 5432)
# - FastAPI backend (port 8000)
# - React frontend (port 3000) with hot reload
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Run Frontend Standalone

If you want to run just the frontend (backend must be running separately):

```bash
cd /home/yusufss/swe573-practice/the_hive_frontend

# Development mode
docker-compose up frontend-dev

# Production mode
docker-compose up frontend
```

## 📋 Available Commands

### Development Mode (with hot reload)

```bash
# Start all services (from the_hive/infra)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after dependency changes
docker-compose up --build frontend
```

### Production Mode

```bash
# Start production services (from the_hive/infra)
docker-compose -f docker-compose.prod.yml up

# Build production image
docker-compose -f docker-compose.prod.yml build frontend

# Start in background
docker-compose -f docker-compose.prod.yml up -d
```

## 🏗️ Docker Architecture

### Development Setup (Dockerfile.dev)
- Base: `node:18-alpine`
- Hot reload: ✅ Enabled via volume mounts
- Source maps: ✅ Full debugging support
- Port: 3000
- Use case: Local development

**Volumes mounted:**
- `./src` - Source code (hot reload)
- `./public` - Static assets
- `./index.html` - HTML template
- `./vite.config.ts` - Vite configuration
- `node_modules` - Excluded for performance

### Production Setup (Dockerfile)
- Multi-stage build for optimization
- Stage 1: Build with `node:18-alpine`
- Stage 2: Serve with `nginx:alpine`
- Port: 80
- Optimizations:
  - Gzip compression
  - Asset caching (1 year for immutable assets)
  - Security headers
  - SPA routing support
  - Minimal image size

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory or set in docker-compose:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=The Hive
```

For production, these are baked into the build at build-time.

### Nginx Configuration

The `nginx.conf` handles:
- SPA routing (all routes → index.html)
- Gzip compression
- Security headers
- Static asset caching
- Health check endpoint at `/health`

## 📊 Service Dependencies

```
┌─────────────┐
│ PostgreSQL  │
│  (port 5432)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Backend    │
│  (port 8000)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Frontend   │
│  (port 3000)│
└─────────────┘
```

## 🎯 Common Tasks

### Rebuild After Dependency Changes

```bash
cd /home/yusufss/swe573-practice/the_hive/infra

# Rebuild frontend only
docker-compose build frontend

# Rebuild and start
docker-compose up --build frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Access Container Shell

```bash
# Development container
docker exec -it the_hive_frontend sh

# Production container
docker exec -it the_hive_frontend_prod sh
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (database data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Issue**: CORS errors or connection refused

**Solutions:**
1. Check backend CORS settings include frontend origin
2. Ensure backend is running: `docker-compose ps`
3. Check backend logs: `docker-compose logs app`
4. Verify network: `docker network inspect the_hive_infra_the_hive_network`

### Hot reload not working

**Issue**: Changes not reflected in browser

**Solutions:**
1. Ensure you're using `docker-compose.yml` (dev mode) not `docker-compose.prod.yml`
2. Check volumes are mounted: `docker inspect the_hive_frontend`
3. Restart container: `docker-compose restart frontend`
4. Clear browser cache

### Port already in use

**Issue**: `Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use`

**Solutions:**
1. Stop existing process: `lsof -ti:3000 | xargs kill -9`
2. Change port in docker-compose.yml: `"3001:3000"`
3. Use different compose file with different ports

### Build fails

**Issue**: npm install errors or build errors

**Solutions:**
1. Check Node version: Should be 18+
2. Clear Docker cache: `docker-compose build --no-cache frontend`
3. Check package.json is valid
4. Ensure enough disk space

### Container exits immediately

**Issue**: Container starts then stops

**Solutions:**
1. Check logs: `docker-compose logs frontend`
2. Verify Dockerfile syntax
3. Check for port conflicts
4. Ensure package.json scripts are correct

## 📈 Performance Tips

### Development
- Use volume mounts for hot reload (already configured)
- Exclude `node_modules` from volumes (already configured)
- Use `--build` only when dependencies change

### Production
- Multi-stage build reduces image size (already configured)
- Nginx serves static files efficiently
- Gzip compression enabled
- Long cache times for static assets

## 🔐 Security Considerations

### Development
- Don't expose development containers to public networks
- Use `.env` files, don't commit secrets

### Production
- Use environment variables for secrets
- Enable HTTPS (add reverse proxy like Traefik or Caddy)
- Regular security updates: `docker-compose pull`
- Security headers configured in nginx.conf

## 📦 Image Sizes

- **Development image**: ~400MB (includes build tools)
- **Production image**: ~25MB (nginx + built assets only)

## 🚢 Deployment

For production deployment:

1. Build production image:
```bash
cd /home/yusufss/swe573-practice/the_hive/infra
docker-compose -f docker-compose.prod.yml build
```

2. Tag for registry:
```bash
docker tag the_hive_frontend_prod your-registry/the-hive-frontend:latest
```

3. Push to registry:
```bash
docker push your-registry/the-hive-frontend:latest
```

4. Deploy on server:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔄 Development Workflow

1. Start services:
   ```bash
   cd /home/yusufss/swe573-practice/the_hive/infra
   docker-compose up
   ```

2. Make changes to frontend code in your editor

3. Changes auto-reload in browser (hot reload)

4. View logs if needed:
   ```bash
   docker-compose logs -f frontend
   ```

5. Stop when done:
   ```bash
   docker-compose down
   ```

## 📚 Related Files

- `/home/yusufss/swe573-practice/the_hive/infra/docker-compose.yml` - Main compose file (dev mode)
- `/home/yusufss/swe573-practice/the_hive/infra/docker-compose.prod.yml` - Production compose file
- `/home/yusufss/swe573-practice/the_hive_frontend/docker-compose.yml` - Standalone frontend compose

## 💡 Tips

- **Development**: Always use the main `docker-compose.yml` for development with hot reload
- **Testing**: Use `docker-compose.prod.yml` to test production build locally
- **Debugging**: Use `docker exec -it the_hive_frontend sh` to access container
- **Logs**: Use `docker-compose logs -f` to follow logs in real-time
- **Clean start**: Use `docker-compose down -v && docker-compose up` for fresh start
