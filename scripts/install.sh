#!/bin/bash
#
# ggNet One-Line Installer
# 
# Complete installation script for ggNet diskless boot system
# Supports: Debian 11/12, Ubuntu 20.04/22.04/24.04
#
# Usage:
#   wget -O - https://raw.githubusercontent.com/itcaffenet-Ljubinje/GGnet1/main/install.sh | sudo bash
#
# Or:
#   git clone https://github.com/itcaffenet-Ljubinje/GGnet1.git
#   cd GGnet1
#   sudo bash install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
print_header() {
    echo ""
    echo "==========================================================================="
    echo -e "${BLUE}$1${NC}"
    echo "==========================================================================="
    echo ""
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "This script must be run as root"
    echo "Usage: sudo bash install.sh"
    exit 1
fi

print_header "ggNet Installation Script"

echo "This will install:"
echo "  • ZFS file system"
echo "  • PostgreSQL database"
echo "  • Python backend with FastAPI"
echo "  • React frontend"
echo "  • Nginx web server"
echo "  • Systemd services"
echo ""
echo "Installation directory: /opt/ggnet"
echo ""
read -p "Continue with installation? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled"
    exit 0
fi

#############################################################################
# 1. DETECT OS
#############################################################################
print_header "Step 1: Detecting Operating System"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    print_info "Detected: $PRETTY_NAME"
else
    print_error "Cannot detect OS. Only Debian/Ubuntu supported."
    exit 1
fi

if [ "$OS" != "debian" ] && [ "$OS" != "ubuntu" ]; then
    print_error "Unsupported OS: $OS"
    print_error "Only Debian and Ubuntu are supported"
    exit 1
fi

#############################################################################
# 2. UPDATE SYSTEM
#############################################################################
print_header "Step 2: Updating System Packages"

print_info "Running apt-get update..."
apt-get update

print_info "Upgrading installed packages..."
apt-get upgrade -y

print_success "System updated"

#############################################################################
# 3. INSTALL DEPENDENCIES
#############################################################################
print_header "Step 3: Installing Dependencies"

print_info "Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    gnupg2 \
    lsb-release

print_info "Installing Python 3..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

print_info "Installing PostgreSQL..."
apt-get install -y \
    postgresql \
    postgresql-contrib \
    libpq-dev

print_info "Installing Nginx..."
apt-get install -y nginx

print_info "Installing Node.js 20.x..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

print_info "Installing network tools..."
apt-get install -y \
    iproute2 \
    net-tools \
    dnsutils \
    iputils-ping

print_success "All dependencies installed"

#############################################################################
# 4. INSTALL ZFS
#############################################################################
print_header "Step 4: Installing ZFS"

if [ "$OS" = "debian" ]; then
    print_info "Adding contrib repository for Debian..."
    grep -q "contrib" /etc/apt/sources.list || \
        echo "deb http://deb.debian.org/debian $(lsb_release -sc) contrib" >> /etc/apt/sources.list
    apt-get update
fi

print_info "Installing ZFS packages..."
apt-get install -y linux-headers-$(uname -r)
apt-get install -y zfsutils-linux

if [ "$OS" = "debian" ]; then
    apt-get install -y zfs-dkms
fi

print_info "Loading ZFS kernel module..."
modprobe zfs || print_warning "ZFS module load failed (may require reboot)"

if command -v zpool &> /dev/null; then
    print_success "ZFS installed: $(zpool --version | head -n1)"
else
    print_error "ZFS installation failed"
    exit 1
fi

#############################################################################
# 5. CREATE GGNET USER
#############################################################################
print_header "Step 5: Creating ggNet User"

if id "ggnet" &>/dev/null; then
    print_warning "User 'ggnet' already exists"
else
    useradd -r -m -s /bin/bash -d /opt/ggnet -c "ggNet Service User" ggnet
    print_success "User 'ggnet' created"
fi

#############################################################################
# 6. CLONE/COPY SOURCE CODE
#############################################################################
print_header "Step 6: Setting Up Source Code"

INSTALL_DIR="/opt/ggnet"

if [ -d "$INSTALL_DIR/.git" ]; then
    print_info "Updating existing installation..."
    cd "$INSTALL_DIR"
    sudo -u ggnet git pull origin main
else
    print_info "Installing to $INSTALL_DIR..."
    
    # Check if we're running from cloned repo
    if [ -f "$(pwd)/install.sh" ] && [ -d "$(pwd)/backend" ]; then
        print_info "Copying from current directory..."
        mkdir -p "$INSTALL_DIR"
        cp -r ./* "$INSTALL_DIR/"
        chown -R ggnet:ggnet "$INSTALL_DIR"
    else
        print_info "Cloning from GitHub..."
        git clone https://github.com/itcaffenet-Ljubinje/GGnet1.git "$INSTALL_DIR"
        chown -R ggnet:ggnet "$INSTALL_DIR"
    fi
fi

cd "$INSTALL_DIR"
print_success "Source code ready"

#############################################################################
# 7. SETUP POSTGRESQL DATABASE
#############################################################################
print_header "Step 7: Configuring PostgreSQL Database"

print_info "Starting PostgreSQL service..."
systemctl start postgresql
systemctl enable postgresql

print_info "Creating database and user..."

# Create database and user
sudo -u postgres psql << EOF || print_warning "Database may already exist"
CREATE DATABASE ggnet;
CREATE USER ggnet WITH PASSWORD 'ggnet_secure_password_change_me';
GRANT ALL PRIVILEGES ON DATABASE ggnet TO ggnet;
ALTER DATABASE ggnet OWNER TO ggnet;
\c ggnet
GRANT ALL ON SCHEMA public TO ggnet;
EOF

print_success "PostgreSQL database configured"

#############################################################################
# 8. SETUP PYTHON BACKEND
#############################################################################
print_header "Step 8: Setting Up Python Backend"

cd "$INSTALL_DIR/backend"

print_info "Creating Python virtual environment..."
sudo -u ggnet python3 -m venv venv

print_info "Installing Python dependencies..."
sudo -u ggnet venv/bin/pip install --upgrade pip setuptools wheel
sudo -u ggnet venv/bin/pip install -r requirements.txt

print_info "Creating backend configuration..."
cat > /etc/ggnet/backend.conf << EOF
DATABASE_URL=postgresql://ggnet:ggnet_secure_password_change_me@localhost/ggnet
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
ALLOWED_HOSTS=*
EOF

chmod 640 /etc/ggnet/backend.conf
chown ggnet:ggnet /etc/ggnet/backend.conf

print_info "Initializing database schema..."
cd "$INSTALL_DIR/backend"
sudo -u ggnet bash -c 'source venv/bin/activate && python -c "
import asyncio
import sys
sys.path.insert(0, \"src\")
from db.base import init_db
asyncio.run(init_db())
"'

print_success "Backend setup complete"

#############################################################################
# 9. CREATE SYSTEMD SERVICE
#############################################################################
print_header "Step 9: Creating Systemd Service"

print_info "Creating ggnet-backend.service..."

cat > /etc/systemd/system/ggnet-backend.service << 'EOF'
[Unit]
Description=ggNet Backend API Server
Documentation=https://github.com/itcaffenet-Ljubinje/GGnet1
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=ggnet
Group=ggnet
WorkingDirectory=/opt/ggnet/backend
Environment="PATH=/opt/ggnet/backend/venv/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=-/etc/ggnet/backend.conf
ExecStart=/opt/ggnet/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ggnet-backend
systemctl start ggnet-backend

sleep 3

if systemctl is-active --quiet ggnet-backend; then
    print_success "Backend service started"
else
    print_error "Backend service failed to start"
    print_info "Check logs: sudo journalctl -u ggnet-backend -n 50"
fi

#############################################################################
# 10. BUILD FRONTEND
#############################################################################
print_header "Step 10: Building Frontend"

cd "$INSTALL_DIR/frontend"

print_info "Installing npm dependencies..."
sudo -u ggnet npm install

print_info "Building production frontend..."
sudo -u ggnet npm run build

print_success "Frontend built"

#############################################################################
# 11. CONFIGURE NGINX
#############################################################################
print_header "Step 11: Configuring Nginx"

print_info "Creating Nginx configuration..."

cat > /etc/nginx/sites-available/ggnet << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Allow large file uploads (for OS images)
    client_max_body_size 50G;
    
    # Frontend
    location / {
        root /opt/ggnet/frontend/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for large uploads
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_connect_timeout 300s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ggnet /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

print_info "Testing Nginx configuration..."
nginx -t

print_info "Reloading Nginx..."
systemctl reload nginx
systemctl enable nginx

print_success "Nginx configured"

#############################################################################
# 12. CREATE STORAGE DIRECTORIES
#############################################################################
print_header "Step 12: Creating Storage Directories"

mkdir -p /var/lib/ggnet/{images,snapshots,writebacks}
mkdir -p /var/log/ggnet
mkdir -p /etc/ggnet

chown -R ggnet:ggnet /var/lib/ggnet
chown -R ggnet:ggnet /var/log/ggnet
chown -R ggnet:ggnet /etc/ggnet

print_success "Storage directories created"

#############################################################################
# INSTALLATION COMPLETE
#############################################################################
print_header "Installation Complete!"

SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}✅ ggNet has been successfully installed!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 System Status:"
echo "  • Backend:  $(systemctl is-active ggnet-backend)"
echo "  • Nginx:    $(systemctl is-active nginx)"
echo "  • Database: $(systemctl is-active postgresql)"
echo ""
echo "🌐 Access ggNet:"
echo "  • Web UI:     http://$SERVER_IP"
echo "  • Dashboard:  http://$SERVER_IP/dashboard"
echo "  • API:        http://$SERVER_IP/api/v1/"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs:       sudo journalctl -u ggnet-backend -f"
echo "  • Restart backend: sudo systemctl restart ggnet-backend"
echo "  • Check status:    sudo systemctl status ggnet-backend"
echo ""
echo "📁 Important Paths:"
echo "  • Installation:    /opt/ggnet"
echo "  • Backend:         /opt/ggnet/backend"
echo "  • Frontend:        /opt/ggnet/frontend/dist"
echo "  • Database:        PostgreSQL (ggnet database)"
echo "  • Logs:            /var/log/ggnet"
echo "  • Config:          /etc/ggnet"
echo ""
echo "🗄️  Next Steps - ZFS Storage:"
echo ""
echo "  1. List available drives:"
echo "     lsblk"
echo ""
echo "  2. Create ZFS pool (example with 4 drives):"
echo "     sudo zpool create pool0 \\"
echo "       mirror /dev/sdb /dev/sdc \\"
echo "       mirror /dev/sdd /dev/sde"
echo ""
echo "  3. Create ggNet filesystems:"
echo "     sudo zfs create pool0/ggnet"
echo "     sudo zfs create pool0/ggnet/images"
echo "     sudo zfs create pool0/ggnet/snapshots"
echo "     sudo zfs create pool0/ggnet/writebacks"
echo ""
echo "  4. Set ownership:"
echo "     sudo chown -R ggnet:ggnet /pool0/ggnet"
echo ""
echo "  5. Verify in UI:"
echo "     http://$SERVER_IP/storage"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Installation Complete! Open http://$SERVER_IP in your browser!${NC}"
echo ""
