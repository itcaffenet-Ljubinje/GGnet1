#!/bin/bash

#############################################################################
# ggNet Backend - Application Setup Script
#
# This script sets up the ggNet backend application on Linux
# Run this AFTER setup_linux_server.sh
#
# Usage: bash setup_backend.sh (as ggnet user)
#############################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Get backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_info "Backend directory: $BACKEND_DIR"

#############################################################################
# 1. CREATE VIRTUAL ENVIRONMENT
#############################################################################
print_info "Creating Python virtual environment..."

cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

#############################################################################
# 2. INSTALL PYTHON DEPENDENCIES
#############################################################################
print_info "Installing Python dependencies..."

pip install --upgrade pip -q

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    print_success "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing manually..."
    
    pip install -q \
        fastapi \
        uvicorn[standard] \
        sqlalchemy \
        asyncpg \
        pydantic \
        python-multipart \
        psycopg2-binary \
        alembic \
        pytest \
        pytest-asyncio \
        pytest-cov \
        httpx
    
    print_success "Dependencies installed"
fi

#############################################################################
# 3. CREATE CONFIGURATION FILE
#############################################################################
print_info "Creating configuration file..."

if [ ! -f ".env" ]; then
    cat > .env << EOF
# ggNet Backend Configuration
DATABASE_URL=postgresql+asyncpg://ggnet:ggnet@localhost/ggnet
SECRET_KEY=$(openssl rand -hex 32)
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production

# Storage paths
STORAGE_ROOT=/srv/ggnet/array
IMAGES_PATH=/srv/ggnet/array/images
WRITEBACKS_PATH=/srv/ggnet/array/writebacks
SNAPSHOTS_PATH=/srv/ggnet/array/snapshots

# Array settings
DEFAULT_ARRAY_TYPE=zfs
RESERVED_SPACE_PERCENT=15
EOF
    print_success "Configuration file created (.env)"
else
    print_warning ".env file already exists, skipping"
fi

#############################################################################
# 4. CREATE REQUIRED DIRECTORIES
#############################################################################
print_info "Creating required directories..."

mkdir -p /srv/ggnet/array/images
mkdir -p /srv/ggnet/array/writebacks
mkdir -p /srv/ggnet/array/snapshots
mkdir -p /srv/ggnet/logs
mkdir -p /var/log/ggnet

print_success "Directories created"

#############################################################################
# 5. SET PERMISSIONS
#############################################################################
print_info "Setting permissions..."

# Ensure ggnet user owns everything
sudo chown -R ggnet:ggnet /srv/ggnet
sudo chown -R ggnet:ggnet /var/log/ggnet

# Set proper permissions
chmod -R 755 /srv/ggnet
chmod 600 .env

print_success "Permissions set"

#############################################################################
# 6. DATABASE SETUP
#############################################################################
print_info "Setting up database..."

# Check if database exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw ggnet; then
    print_warning "Database 'ggnet' already exists"
else
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE ggnet;
CREATE USER ggnet WITH PASSWORD 'ggnet';
GRANT ALL PRIVILEGES ON DATABASE ggnet TO ggnet;
EOF
    print_success "Database and user created"
fi

#############################################################################
# 7. RUN DATABASE MIGRATIONS
#############################################################################
print_info "Running database migrations..."

cd "$BACKEND_DIR"

# Check if alembic is initialized
if [ -d "alembic" ]; then
    alembic upgrade head
    print_success "Database migrations applied"
else
    print_warning "Alembic not initialized. Run: alembic init alembic"
fi

#############################################################################
# 8. RUN TESTS (OPTIONAL)
#############################################################################
print_info "Running tests..."

if pytest tests/ -v -x 2>&1 | tail -n 5; then
    print_success "Tests passed!"
else
    print_warning "Some tests failed. Review test output."
fi

#############################################################################
# 9. SUMMARY
#############################################################################
echo ""
echo "==========================================================================="
print_success "ggNet Backend Setup COMPLETE!"
echo "==========================================================================="
echo ""
print_info "Application ready to start!"
echo ""
print_info "Start manually:"
echo "  source venv/bin/activate"
echo "  cd $BACKEND_DIR"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
print_info "Or start as service:"
echo "  sudo systemctl start ggnet-backend"
echo "  sudo systemctl enable ggnet-backend"
echo ""
print_info "Check status:"
echo "  sudo systemctl status ggnet-backend"
echo "  curl http://localhost:8000/health"
echo ""
print_info "View logs:"
echo "  sudo journalctl -u ggnet-backend -f"
echo "  tail -f /var/log/ggnet/backend.log"
echo ""
echo "==========================================================================="

