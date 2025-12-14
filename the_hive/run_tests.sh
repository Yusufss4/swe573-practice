#!/bin/bash
# Run all tests for The Hive application

set -e

echo "🧪 Running all tests for The Hive"
echo "================================="
echo ""

# Check if we're in Docker or local environment
if [ -f "/.dockerenv" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    # Inside Docker
    echo "📦 Running tests inside Docker container..."
    pytest tests/ -v --tb=short
else
    # Outside Docker
    echo "🐳 Running tests via Docker..."
    cd infra
    docker compose exec backend pytest tests/ -v --tb=short
fi
