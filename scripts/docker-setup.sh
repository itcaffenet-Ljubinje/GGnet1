#!/bin/bash

# GGRock Management System - Docker Setup Script
# This script automates Docker deployment

set -e

echo "🐳 GGRock Management System - Docker Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker version: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose is available"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker daemon is running"

# Prompt for deployment type
echo ""
echo "Select deployment type:"
echo "1) Development (includes mock API)"
echo "2) Production (requires existing GGRock backend)"
read -p "Enter choice (1 or 2): " deployment_type

if [ "$deployment_type" = "2" ]; then
    # Production deployment
    read -p "Enter GGRock backend URL: " backend_url
    
    # Create production docker-compose override
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  frontend:
    environment:
      - VITE_GGROCK_API_URL=${backend_url}
      - VITE_GGROCK_WS_URL=${backend_url/http/ws}
EOF
    
    COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

# Build and start containers
echo ""
echo "🏗️  Building Docker images..."
docker-compose -f $COMPOSE_FILE build

echo ""
echo "🚀 Starting containers..."
docker-compose -f $COMPOSE_FILE up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
echo ""
echo "📊 Service Status:"
docker-compose -f $COMPOSE_FILE ps

# Display access URLs
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Access URLs:"
echo "  Frontend: http://localhost:3000"
if [ "$deployment_type" = "1" ]; then
    echo "  Mock API: http://localhost:5000"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001 (admin/admin)"
fi
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Rebuild:      docker-compose build --no-cache"

