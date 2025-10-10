#!/bin/bash

# GGRock Management System - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "🚀 GGRock Management System Setup"
echo "=================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if pnpm is installed, offer to install it
if ! command -v pnpm &> /dev/null; then
    echo "⚠️  pnpm is not installed."
    read -p "Would you like to install pnpm? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install -g pnpm
        echo "✅ pnpm installed successfully"
    else
        echo "Using npm instead..."
        PKG_MANAGER="npm"
    fi
else
    echo "✅ pnpm version: $(pnpm --version)"
    PKG_MANAGER="pnpm"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if [ "$PKG_MANAGER" = "pnpm" ]; then
    pnpm install
else
    npm install
fi
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    
    # Prompt for GGRock API URL
    read -p "Enter GGRock API URL (default: http://localhost:5000): " api_url
    api_url=${api_url:-http://localhost:5000}
    
    # Prompt for WebSocket URL
    read -p "Enter GGRock WebSocket URL (default: ws://localhost:5000): " ws_url
    ws_url=${ws_url:-ws://localhost:5000}
    
    # Prompt for VNC URL
    read -p "Enter noVNC URL (default: http://localhost:6080): " vnc_url
    vnc_url=${vnc_url:-http://localhost:6080}
    
    # Create .env file
    cat > .env << EOF
# GGRock API Configuration
VITE_GGROCK_API_URL=${api_url}
VITE_GGROCK_WS_URL=${ws_url}
VITE_GGROCK_VNC_URL=${vnc_url}

# Application Configuration
VITE_APP_NAME=GGRock Management System
VITE_APP_VERSION=0.1.0

# Feature Flags
VITE_ENABLE_VNC=true
VITE_ENABLE_GRAFANA=true
VITE_GRAFANA_URL=http://localhost:3000
EOF
    
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Check if GGRock backend is accessible
echo ""
echo "🔍 Checking GGRock backend connectivity..."
source .env
if curl -s -o /dev/null -w "%{http_code}" "${VITE_GGROCK_API_URL}/health" | grep -q "200\|404"; then
    echo "✅ GGRock backend is accessible"
else
    echo "⚠️  Warning: Cannot connect to GGRock backend at ${VITE_GGROCK_API_URL}"
    echo "   Make sure the GGRock backend is running before starting the application."
fi

# Offer to start development server
echo ""
echo "✅ Setup complete!"
echo ""
read -p "Would you like to start the development server now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting development server..."
    echo "   The application will be available at http://localhost:3000"
    echo ""
    if [ "$PKG_MANAGER" = "pnpm" ]; then
        pnpm dev
    else
        npm run dev
    fi
else
    echo ""
    echo "To start the development server later, run:"
    if [ "$PKG_MANAGER" = "pnpm" ]; then
        echo "  pnpm dev"
    else
        echo "  npm run dev"
    fi
    echo ""
    echo "The application will be available at http://localhost:3000"
fi

