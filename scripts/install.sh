#!/bin/bash
################################################################################
# ggNet Installation Script
#
# Installs ggNet diskless boot management system on Debian 11+ / Ubuntu 22+
# This script is idempotent and can be run multiple times safely.
#
# Usage:
#   sudo ./scripts/install.sh
#   sudo ./scripts/install.sh --skip-packages  # Skip apt install
#   sudo ./scripts/install.sh --setup-db       # Also setup database
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GGNET_USER="ggnet"
INSTALL_DIR="/opt/ggnet"
DATA_DIR="/srv/ggnet"
CONFIG_DIR="/etc/ggnet"
LOG_DIR="/var/log/ggnet"

# Parse arguments
SKIP_PACKAGES=false
SETUP_DB=false

for arg in "$@"; do
    case $arg in
        --skip-packages) SKIP_PACKAGES=true ;;
        --setup-db) SETUP_DB=true ;;
        --help)
            echo "ggNet Installation Script"
            echo ""
            echo "Usage: sudo $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-packages  Skip apt package installation"
            echo "  --setup-db       Setup PostgreSQL database"
            echo "  --help           Show this help"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ggNet Installation Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo

################################################################################
# Step 1: Validate Prerequisites
################################################################################

echo -e "${BLUE}[1/10] Validating prerequisites...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ This script must be run as root${NC}"
    echo "   Usage: sudo $0"
    exit 1
fi

# Check OS version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}✅ OS: $NAME $VERSION_ID${NC}"
    
    # Validate supported OS
    case "$ID" in
        debian)
            if [ "${VERSION_ID%%.*}" -lt 11 ]; then
                echo -e "${RED}❌ Debian 11+ required (detected: $VERSION_ID)${NC}"
                exit 1
            fi
            ;;
        ubuntu)
            if [ "${VERSION_ID%%.*}" -lt 22 ]; then
                echo -e "${RED}❌ Ubuntu 22+ required (detected: $VERSION_ID)${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${YELLOW}⚠️  Unsupported OS: $ID${NC}"
            echo "   Supported: Debian 11+, Ubuntu 22+"
            read -p "Continue anyway? (yes/no): " confirm
            if [ "$confirm" != "yes" ]; then
                exit 1
            fi
            ;;
    esac
else
    echo -e "${RED}❌ Cannot determine OS version${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}✅ Project directory: $PROJECT_DIR${NC}"
echo

################################################################################
# Step 2: Install System Packages
################################################################################

if [ "$SKIP_PACKAGES" = false ]; then
    echo -e "${BLUE}[2/10] Installing system packages...${NC}"
    
    # Update package lists
    apt-get update
    
    # Install packages
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        nginx \
        python3 \
        python3-pip \
        python3-venv \
        nodejs \
        npm \
        isc-dhcp-server \
        tftpd-hpa \
        nfs-kernel-server \
        mdadm \
        jq \
        rsync \
        curl \
        wget \
        git \
        sudo \
        sqlite3 \
        qemu-utils \
        || { echo -e "${RED}❌ Package installation failed${NC}"; exit 1; }
    
    echo -e "${GREEN}✅ Packages installed${NC}"
else
    echo -e "${YELLOW}[2/10] Skipping package installation${NC}"
fi

echo

################################################################################
# Step 3: Create System User and Directories
################################################################################

echo -e "${BLUE}[3/10] Creating system user and directories...${NC}"

# Create ggnet user
if ! id "$GGNET_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash -c "ggNet System User" $GGNET_USER
    echo -e "${GREEN}✅ User $GGNET_USER created${NC}"
else
    echo -e "${YELLOW}ℹ️  User $GGNET_USER already exists${NC}"
fi

# Create directories
mkdir -p $INSTALL_DIR
mkdir -p $DATA_DIR/{array,images,tftp,nfs,logs}
mkdir -p $CONFIG_DIR
mkdir -p $LOG_DIR

echo -e "${GREEN}✅ Directories created:${NC}"
echo "   $INSTALL_DIR"
echo "   $DATA_DIR"
echo "   $CONFIG_DIR"
echo "   $LOG_DIR"

# Set ownership
chown -R $GGNET_USER:$GGNET_USER $INSTALL_DIR
chown -R $GGNET_USER:$GGNET_USER $DATA_DIR
chown -R $GGNET_USER:$GGNET_USER $LOG_DIR

# CONFIG_DIR should be root-owned for security
chown -R root:$GGNET_USER $CONFIG_DIR
chmod 750 $CONFIG_DIR

echo -e "${GREEN}✅ Permissions set${NC}"
echo

################################################################################
# Step 4: Copy Application Files
################################################################################

echo -e "${BLUE}[4/10] Copying application files...${NC}"

# Skip copying if we're already in the install directory
if [ "$(realpath "$PROJECT_DIR")" = "$(realpath "$INSTALL_DIR")" ]; then
    echo -e "${YELLOW}ℹ️  Already in install directory, skipping file copy${NC}"
    echo -e "${GREEN}✅ Application files already in place${NC}"
else
    # Backup existing installation if present
    if [ -d "$INSTALL_DIR/backend" ]; then
        BACKUP_DIR="/tmp/ggnet-backup-$(date +%Y%m%d-%H%M%S)"
        echo -e "${YELLOW}ℹ️  Backing up existing installation to $BACKUP_DIR${NC}"
        mkdir -p $BACKUP_DIR
        cp -r $INSTALL_DIR/* $BACKUP_DIR/ || true
    fi

    # Copy backend
    rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' \
        "$PROJECT_DIR/backend/" "$INSTALL_DIR/backend/"

    # Copy frontend
    rsync -a --exclude='node_modules' --exclude='dist' \
        "$PROJECT_DIR/frontend/" "$INSTALL_DIR/frontend/"

    # Copy PXE files
    rsync -a "$PROJECT_DIR/pxe/" "$DATA_DIR/pxe/"

    # Copy docs (if exists)
    if [ -d "$PROJECT_DIR/docs" ]; then
        mkdir -p $INSTALL_DIR/docs
        rsync -a "$PROJECT_DIR/docs/" "$INSTALL_DIR/docs/"
    else
        echo -e "${YELLOW}⚠️  Docs directory not found, skipping${NC}"
    fi

    echo -e "${GREEN}✅ Application files copied${NC}"
fi

# Fix ownership after copying files
echo "🔧 Setting correct ownership..."
chown -R $GGNET_USER:$GGNET_USER $INSTALL_DIR

echo

################################################################################
# Step 5: Setup Python Virtual Environment
################################################################################

echo -e "${BLUE}[5/10] Setting up Python virtual environment...${NC}"

cd $INSTALL_DIR/backend

# Create virtualenv
if [ ! -d "venv" ]; then
    sudo -u $GGNET_USER python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}ℹ️  Virtual environment already exists${NC}"
fi

# Upgrade pip
sudo -u $GGNET_USER venv/bin/pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies..."
sudo -u $GGNET_USER venv/bin/pip install -r requirements.txt

echo -e "${GREEN}✅ Python dependencies installed${NC}"
echo

################################################################################
# Step 6: Build Frontend
################################################################################

echo -e "${BLUE}[6/10] Building frontend...${NC}"

cd $INSTALL_DIR/frontend

# Check for pnpm, fallback to npm
if command -v pnpm &> /dev/null; then
    PKG_MGR="pnpm"
else
    PKG_MGR="npm"
fi

echo "Using package manager: $PKG_MGR"

# Update npm to latest version if using npm
if [ "$PKG_MGR" = "npm" ]; then
    echo "📦 Updating npm to latest version..."
    npm install -g npm@latest 2>/dev/null || echo "  ⚠️  Couldn't update npm (non-critical)"
fi

# Install dependencies
echo "📦 Installing frontend dependencies..."
# Handle npm optional dependency bug: https://github.com/npm/cli/issues/4828
if [ "$PKG_MGR" = "npm" ]; then
    sudo -u $GGNET_USER npm install || {
        echo "⚠️  npm install failed, trying clean install..."
        sudo -u $GGNET_USER rm -rf node_modules package-lock.json
        sudo -u $GGNET_USER npm install
    }
else
    sudo -u $GGNET_USER $PKG_MGR install
fi

# Build
echo "🔨 Building frontend..."
sudo -u $GGNET_USER $PKG_MGR run build

if [ -d "dist" ]; then
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
    echo "   Output: $INSTALL_DIR/frontend/dist"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

echo

################################################################################
# Step 7: Configure Nginx
################################################################################

echo -e "${BLUE}[7/10] Configuring Nginx...${NC}"

# Create Nginx configuration
cat > /etc/nginx/sites-available/ggnet << 'EOF'
# ggNet Nginx Configuration
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # Frontend static files
    root /opt/ggnet/frontend/dist;
    index index.html;

    # Frontend SPA routing
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # Static assets caching
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # PXE boot scripts (for iPXE HTTP boot)
    location /pxe/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
    }

    # Boot files (kernels, initrd)
    location /boot/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        access_log off;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/ggnet /etc/nginx/sites-enabled/ggnet

# Disable default site if exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
    echo -e "${GREEN}✅ Disabled default Nginx site${NC}"
fi

# Test Nginx configuration
if nginx -t 2>/dev/null; then
    echo -e "${GREEN}✅ Nginx configuration valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration invalid${NC}"
    exit 1
fi

echo

################################################################################
# Step 8: Deploy Systemd Services
################################################################################

echo -e "${BLUE}[8/10] Deploying systemd services...${NC}"

# Backend service
cat > /etc/systemd/system/ggnet-backend.service << EOF
[Unit]
Description=ggNet Backend API Server
Documentation=https://github.com/yourusername/ggnet
After=network.target

[Service]
Type=simple
User=$GGNET_USER
Group=$GGNET_USER
WorkingDirectory=$INSTALL_DIR/backend/src

# Environment
Environment="PATH=$INSTALL_DIR/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=-$CONFIG_DIR/backend.conf

# Start command
ExecStart=$INSTALL_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080

# Restart policy
Restart=on-failure
RestartSec=5
StartLimitInterval=300
StartLimitBurst=5

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ggnet-backend

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Systemd service files created${NC}"

# Reload systemd
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd daemon reloaded${NC}"

echo

################################################################################
# Step 9: Initialize Database (Optional)
################################################################################

if [ "$SETUP_DB" = true ]; then
    echo -e "${BLUE}[9/10] Setting up database...${NC}"
    
    if [ -f "$SCRIPT_DIR/setup_db.sh" ]; then
        bash "$SCRIPT_DIR/setup_db.sh"
    else
        echo -e "${YELLOW}⚠️  Database setup script not found${NC}"
        echo "   Creating database manually..."
        
        # Create SQLite database
        cd $INSTALL_DIR/backend/src
        sudo -u $GGNET_USER ../venv/bin/python ../scripts/seed_db.py || \
            echo -e "${YELLOW}⚠️  Database seeding skipped${NC}"
    fi
else
    echo -e "${YELLOW}[9/10] Skipping database setup${NC}"
    echo "   Run manually: sudo ./scripts/setup_db.sh"
fi

echo

################################################################################
# Step 10: Enable and Start Services
################################################################################

echo -e "${BLUE}[10/10] Starting services...${NC}"

# Enable services
systemctl enable ggnet-backend
echo -e "${GREEN}✅ ggNet backend enabled${NC}"

# Start backend
systemctl start ggnet-backend
echo -e "${GREEN}✅ ggNet backend started${NC}"

# Reload Nginx
systemctl reload nginx || systemctl restart nginx
echo -e "${GREEN}✅ Nginx reloaded${NC}"

# Wait for backend to initialize
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check backend health
for i in {1..10}; do
    if curl -sf http://localhost:8080/api/status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is responding${NC}"
        break
    fi
    
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        echo "   Check logs: journalctl -u ggnet-backend -n 50"
        exit 1
    fi
    
    sleep 2
done

echo

################################################################################
# Final Status
################################################################################

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ggNet Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${BLUE}📊 Installation Summary:${NC}"
echo "   Installation directory: $INSTALL_DIR"
echo "   Data directory: $DATA_DIR"
echo "   Configuration: $CONFIG_DIR"
echo "   Logs: $LOG_DIR"
echo "   User: $GGNET_USER"
echo
echo -e "${BLUE}🌐 Access Points:${NC}"
echo "   Web Interface: http://$SERVER_IP"
echo "   API Docs: http://$SERVER_IP/docs"
echo "   API Status: http://$SERVER_IP/api/status"
echo
echo -e "${BLUE}🔧 Service Commands:${NC}"
echo "   Status: systemctl status ggnet-backend"
echo "   Logs: journalctl -u ggnet-backend -f"
echo "   Restart: systemctl restart ggnet-backend"
echo
echo -e "${BLUE}📖 Next Steps:${NC}"
echo "   1. Access web interface at http://$SERVER_IP"
echo "   2. Create storage array: sudo ./storage/raid/create_raid10.sh"
echo "   3. Generate PXE configs: python pxe/service.py sync"
echo "   4. Configure DHCP: cp pxe/dhcp/generated-dhcp.conf /etc/dhcp/dhcpd.conf"
echo "   5. Setup NFS: cp pxe/nfs/exports.template /etc/exports"
echo "   6. Register client machines via web interface"
echo
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   Installation: $INSTALL_DIR/docs/"
echo "   Backend: $INSTALL_DIR/backend/README.md"
echo "   PXE Boot: $INSTALL_DIR/../pxe/README.md"
echo "   Storage: $INSTALL_DIR/../storage/STORAGE_COMPLETE.md"
echo
echo -e "${BLUE}🔐 Security Notes:${NC}"
echo "   - Default SQLite database: $INSTALL_DIR/backend/src/ggnet.db"
echo "   - Config file: $CONFIG_DIR/backend.conf (if using PostgreSQL)"
echo "   - Change default passwords before production use"
echo
echo -e "${BLUE}🐛 Troubleshooting:${NC}"
echo "   - Backend logs: journalctl -u ggnet-backend -f"
echo "   - Nginx logs: tail -f /var/log/nginx/error.log"
echo "   - System check: ./scripts/check_system.sh"
echo
echo -e "${GREEN}Installation complete! 🎉${NC}"
echo

exit 0


