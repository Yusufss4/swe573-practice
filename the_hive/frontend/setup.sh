#!/bin/bash

# The Hive - Frontend Setup Script
# Run this script to set up the frontend for the first time

set -e

echo "🐝 The Hive - Frontend Setup"
echo "=============================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    echo "Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "📝 Please review and update .env file if needed:"
    cat .env
else
    echo "✓ .env file already exists"
fi
echo ""

echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The frontend will be available at: http://localhost:5173"
echo "Make sure the backend is running at: http://localhost:8000"
echo ""
echo "Or use Docker to start everything:"
echo "  cd ../infra"
echo "  docker-compose up"
