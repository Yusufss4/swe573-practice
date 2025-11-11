#!/bin/bash
# The Hive - Production Deployment Script
# Usage: ./deploy.sh [SERVER_IP]

set -e

echo "================================="
echo "The Hive - Deployment Script"
echo "================================="
echo ""

# Check if IP provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh YOUR_SERVER_IP"
    echo "Example: ./deploy.sh 123.45.67.89"
    exit 1
fi

SERVER_IP=$1
echo "Deploying to: $SERVER_IP"
echo ""

# Generate secrets
echo "Generating security keys..."
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)

echo "✓ Generated SECRET_KEY"
echo "✓ Generated ADMIN_SESSION_SECRET"
echo "✓ Generated DB_PASSWORD"
echo ""

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
# Production Environment Configuration
APP_NAME=the_hive
APP_ENV=production
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/the_hive
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=the_hive

# Security
SECRET_KEY=${SECRET_KEY}
ADMIN_SESSION_SECRET=${ADMIN_SECRET}

# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://${SERVER_IP},http://${SERVER_IP}:80

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false

# Frontend
VITE_API_BASE_URL=http://${SERVER_IP}/api/v1
EOF

echo "✓ Created .env file"
echo ""

echo "================================="
echo "Deployment files ready!"
echo "================================="
echo ""
echo "Next steps on your server ($SERVER_IP):"
echo ""
echo "1. Copy files to server:"
echo "   scp docker-compose.prod.yml nginx.prod.conf .env root@${SERVER_IP}:~/the-hive/"
echo ""
echo "2. SSH to server:"
echo "   ssh root@${SERVER_IP}"
echo ""
echo "3. Navigate and start:"
echo "   cd ~/the-hive"
echo "   docker compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "4. Initialize database:"
echo "   docker compose -f docker-compose.prod.yml exec backend python scripts/init_db.py"
echo ""
echo "5. Access application:"
echo "   http://${SERVER_IP}"
echo ""
echo "================================="
