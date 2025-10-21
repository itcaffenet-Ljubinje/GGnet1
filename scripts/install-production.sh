#!/bin/bash
################################################################################
# ggNet Production Installation Script
#
# This script installs ggNet in production mode on a Debian/Ubuntu system.
#
# Usage:
#   sudo ./install-production.sh
#
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GGNET_USER="ggnet"
GGNET_GROUP="ggnet"
GGNET_HOME="/opt/ggnet"
BACKEND_DIR="${GGNET_HOME}/backend"
FRONTEND_DIR="${GGNET_HOME}/frontend"
LOG_DIR="/var/log/ggnet"
DATA_DIR="/var/lib/ggnet"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║         ggNet Production Installation Script               ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# Step 1: Check if running as root
################################################################################
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}[1/10] Running as root${NC}"
echo ""

################################################################################
# Step 2: Update system packages
################################################################################
echo -e "${BLUE}[2/10] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y
echo -e "${GREEN}✅ System packages updated${NC}"
echo ""

################################################################################
# Step 3: Install required packages
################################################################################
echo -e "${BLUE}[3/10] Installing required packages...${NC}"
apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    nodejs \
    npm \
    nginx \
    postgresql \
    postgresql-contrib \
    dnsmasq \
    tftpd-hpa \
    nfs-kernel-server \
    syslinux \
    pxelinux \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    zfsutils-linux \
    qemu-utils

echo -e "${GREEN}✅ Required packages installed${NC}"
echo ""

################################################################################
# Step 4: Create ggnet user and group
################################################################################
echo -e "${BLUE}[4/10] Creating ggnet user and group...${NC}"
if ! id "$GGNET_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$GGNET_HOME" -c "ggNet Service User" "$GGNET_USER"
    echo -e "${GREEN}✅ User '$GGNET_USER' created${NC}"
else
    echo -e "${YELLOW}⚠ User '$GGNET_USER' already exists${NC}"
fi
echo ""

################################################################################
# Step 5: Create directories
################################################################################
echo -e "${BLUE}[5/10] Creating directories...${NC}"
mkdir -p "$GGNET_HOME"
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/images"
mkdir -p "$DATA_DIR/writebacks"
mkdir -p "$DATA_DIR/snapshots"
mkdir -p /var/lib/tftpboot
mkdir -p /srv/nfs/ggnet

chown -R "$GGNET_USER:$GGNET_GROUP" "$GGNET_HOME"
chown -R "$GGNET_USER:$GGNET_GROUP" "$LOG_DIR"
chown -R "$GGNET_USER:$GGNET_GROUP" "$DATA_DIR"
chown -R "$GGNET_USER:$GGNET_GROUP" /var/lib/tftpboot
chown -R "$GGNET_USER:$GGNET_GROUP" /srv/nfs/ggnet

echo -e "${GREEN}✅ Directories created${NC}"
echo ""

################################################################################
# Step 6: Install backend
################################################################################
echo -e "${BLUE}[6/10] Installing backend...${NC}"
cd "$GGNET_HOME"

# Clone or copy backend
if [ -d "backend" ]; then
    echo -e "${YELLOW}⚠ Backend directory exists, updating...${NC}"
    cd backend
    git pull || true
else
    echo -e "${GREEN}✅ Backend directory not found, please copy backend files to $BACKEND_DIR${NC}"
    echo -e "${YELLOW}⚠ Continuing with existing setup...${NC}"
fi

# Create virtual environment
if [ ! -d "$BACKEND_DIR/venv" ]; then
    python3.10 -m venv "$BACKEND_DIR/venv"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Install Python dependencies
"$BACKEND_DIR/venv/bin/pip" install --upgrade pip
"$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"

echo -e "${GREEN}✅ Backend installed${NC}"
echo ""

################################################################################
# Step 7: Install frontend
################################################################################
echo -e "${BLUE}[7/10] Installing frontend...${NC}"
cd "$GGNET_HOME"

# Clone or copy frontend
if [ -d "frontend" ]; then
    echo -e "${YELLOW}⚠ Frontend directory exists, updating...${NC}"
    cd frontend
    git pull || true
else
    echo -e "${GREEN}✅ Frontend directory not found, please copy frontend files to $FRONTEND_DIR${NC}"
    echo -e "${YELLOW}⚠ Continuing with existing setup...${NC}"
fi

# Install Node dependencies
cd "$FRONTEND_DIR"
npm ci --production

# Build frontend
npm run build

echo -e "${GREEN}✅ Frontend installed${NC}"
echo ""

################################################################################
# Step 8: Configure PostgreSQL
################################################################################
echo -e "${BLUE}[8/10] Configuring PostgreSQL...${NC}"
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE ggnet;

-- Create user
CREATE USER ggnet WITH PASSWORD 'ggnet_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ggnet TO ggnet;

-- Exit
\q
EOF

echo -e "${GREEN}✅ PostgreSQL configured${NC}"
echo ""

################################################################################
# Step 9: Install systemd services
################################################################################
echo -e "${BLUE}[9/10] Installing systemd services...${NC}"
cp "$BACKEND_DIR/scripts/systemd/ggnet-backend.service" /etc/systemd/system/
cp "$BACKEND_DIR/scripts/systemd/ggnet-frontend.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable ggnet-backend
systemctl enable ggnet-frontend

echo -e "${GREEN}✅ Systemd services installed${NC}"
echo ""

################################################################################
# Step 10: Configure Nginx
################################################################################
echo -e "${BLUE}[10/10] Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/ggnet << 'EOF'
upstream ggnet_backend {
    server 127.0.0.1:8000;
}

upstream ggnet_frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://ggnet_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://ggnet_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend docs
    location /docs {
        proxy_pass http://ggnet_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ggnet /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

echo -e "${GREEN}✅ Nginx configured${NC}"
echo ""

################################################################################
# Installation Complete
################################################################################
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║         Installation Complete!                             ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "1. Configure backend:"
echo -e "   ${YELLOW}sudo nano $BACKEND_DIR/.env${NC}"
echo ""
echo -e "2. Start services:"
echo -e "   ${YELLOW}sudo systemctl start ggnet-backend${NC}"
echo -e "   ${YELLOW}sudo systemctl start ggnet-frontend${NC}"
echo ""
echo -e "3. Check status:"
echo -e "   ${YELLOW}sudo systemctl status ggnet-backend${NC}"
echo -e "   ${YELLOW}sudo systemctl status ggnet-frontend${NC}"
echo ""
echo -e "4. View logs:"
echo -e "   ${YELLOW}sudo journalctl -u ggnet-backend -f${NC}"
echo -e "   ${YELLOW}sudo journalctl -u ggnet-frontend -f${NC}"
echo ""
echo -e "${GREEN}ggNet is now installed and ready to use!${NC}"

