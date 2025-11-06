#!/bin/bash
# Start script for The Hive application

set -e

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your settings."
fi

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

echo "🐝 Starting The Hive..."
echo "📍 Host: $HOST"
echo "🔌 Port: $PORT"
echo "📚 Docs: http://localhost:$PORT/docs"
echo "❤️  Health: http://localhost:$PORT/healthz"
echo ""

# Start the application
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
