#!/bin/bash

# The Hive Frontend - Quick Start Script
# This script helps you get the frontend up and running quickly

set -e  # Exit on error

echo "================================"
echo "The Hive Frontend - Quick Start"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the frontend directory."
    echo "   cd /home/yusufss/swe573-practice/the_hive_frontend"
    exit 1
fi

echo "📦 Step 1: Installing dependencies..."
echo "This may take a few minutes..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

echo "🔍 Step 2: Checking backend availability..."
if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "⚠️  Backend not detected on port 8000"
    echo "   Please start the backend first:"
    echo "   cd /home/yusufss/swe573-practice/the_hive"
    echo "   make run"
    echo ""
    echo "   Press Enter to continue anyway, or Ctrl+C to exit..."
    read
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Start the development server:"
echo "      npm run dev"
echo ""
echo "   2. Open your browser to:"
echo "      http://localhost:3000"
echo ""
echo "   3. Register a new account and start testing!"
echo ""
echo "📚 For more information, see:"
echo "   - README.md - Quick start guide"
echo "   - SETUP_GUIDE.md - Detailed integration guide"
echo "   - IMPLEMENTATION_SUMMARY.md - Complete overview"
echo ""
echo "🚀 Happy coding!"
