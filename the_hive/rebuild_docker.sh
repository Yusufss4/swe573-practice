#!/bin/bash
# Rebuild and restart Docker containers

set -e

echo "======================================"
echo "REBUILDING DOCKER CONTAINERS"
echo "======================================"
echo

cd "$(dirname "$0")/infra"

echo "1. Stopping existing containers..."
docker-compose down

echo
echo "2. Rebuilding images..."
docker-compose build

echo
echo "3. Starting containers..."
docker-compose up -d

echo
echo "4. Waiting for services to be ready..."
sleep 5

echo
echo "5. Checking container status..."
docker-compose ps

echo
echo "======================================"
echo "✅ CONTAINERS REBUILT AND RUNNING"
echo "======================================"
echo
echo "Next steps:"
echo "  1. Initialize database:"
echo "     docker-compose exec app python scripts/init_db.py"
echo
echo "  2. Run sanity checks:"
echo "     docker-compose exec app python scripts/sanity_check_auth.py"
echo
echo "  3. Run tests:"
echo "     docker-compose exec app pytest tests/test_auth.py -v"
echo
echo "  4. View logs:"
echo "     docker-compose logs -f app"
echo
