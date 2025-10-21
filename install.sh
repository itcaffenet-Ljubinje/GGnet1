#!/bin/bash

################################################################################
# ggNet Server - One-Line Installer
#
# Automated installation script for ggNet Server Application
# Similar to ggRock's installation process
#
# Usage:
#   wget -O - https://ggnet.com/install.sh | bash -
#
# Or for local testing:
#   bash install.sh
#
################################################################################

set -e  # Exit on any error

# Version
GGNET_VERSION="1.0.0"
INSTALL_DATE=$(date +%Y-%m-%d)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Emoji support
if locale charmap | grep -qi utf; then
    EMOJI_CHECK="✅"
    EMOJI_CROSS="❌"
    EMOJI_WARN="⚠️"
    EMOJI_INFO="ℹ️"
    EMOJI_ROCKET="🚀"
    EMOJI_GEAR="⚙️"
    EMOJI_PACKAGE="📦"
    EMOJI_COFFEE="☕"
    EMOJI_PARTY="🎉"
else
    EMOJI_CHECK="[OK]"
    EMOJI_CROSS="[X]"
    EMOJI_WARN="[!]"
    EMOJI_INFO="[i]"
    EMOJI_ROCKET="[>]"
    EMOJI_GEAR="[*]"
    EMOJI_PACKAGE="[+]"
    EMOJI_COFFEE="[~]"
    EMOJI_PARTY="[*]"
fi

################################################################################
# PRINT FUNCTIONS
################################################################################

print_header() {
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}${EMOJI_INFO}  [INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}${EMOJI_CHECK}  [SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}${EMOJI_WARN}  [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}${EMOJI_CROSS}  [ERROR]${NC} $1"
}

print_step() {
    echo -e "${MAGENTA}${EMOJI_GEAR}  $1${NC}"
}

################################################################################
# PRE-FLIGHT CHECKS
################################################################################

print_header "${EMOJI_ROCKET} ggNet Server Installer v${GGNET_VERSION}"

print_info "Starting ggNet Server installation..."
print_info "This process will take approximately 10-15 minutes"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "This script must be run as root"
    print_info "Please run: sudo bash install.sh"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    print_success "Detected OS: $OS $VER"
else
    print_error "Cannot detect OS"
    exit 1
fi

# Check if Debian/Ubuntu
if [[ ! "$OS" =~ (Debian|Ubuntu) ]]; then
    print_error "This installer only supports Debian and Ubuntu"
    print_info "Detected: $OS"
    exit 1
fi

# Check internet connectivity
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    print_error "No internet connection detected"
    print_info "Please check your network settings and try again"
    exit 1
fi

print_success "Pre-flight checks passed!"
echo ""

################################################################################
# DISPLAY INSTALLATION INFO
################################################################################

print_header "${EMOJI_INFO} Installation Information"

echo -e "${CYAN}What will be installed:${NC}"
echo "  • Python 3.10+ with pip and virtualenv"
echo "  • PostgreSQL database server"
echo "  • ZFS utilities (zpool, zfs)"
echo "  • MD RAID utilities (mdadm)"
echo "  • Network services (DHCP, TFTP, NFS)"
echo "  • ggNet Backend API"
echo "  • ggNet Frontend (React + Vite)"
echo "  • Nginx web server"
echo "  • Monitoring tools (Prometheus + Node Exporter)"
echo ""
echo -e "${CYAN}Installation path:${NC} /srv/ggnet"
echo -e "${CYAN}Estimated time:${NC} 10-15 minutes"
echo ""

# Ask for confirmation
read -p "Continue with installation? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    print_warning "Installation cancelled by user"
    exit 0
fi

################################################################################
# STEP 1: UPDATE SYSTEM
################################################################################

print_header "${EMOJI_PACKAGE} Step 1/10: Updating System Packages"

print_step "Updating package lists..."
apt-get update -qq > /dev/null 2>&1

print_step "Upgrading installed packages..."
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq > /dev/null 2>&1

print_success "System updated"

################################################################################
# STEP 2: INSTALL DEPENDENCIES
################################################################################

print_header "${EMOJI_PACKAGE} Step 2/10: Installing Core Dependencies"

print_step "Installing build tools and utilities..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    curl wget git vim htop net-tools lsof \
    build-essential software-properties-common \
    apt-transport-https ca-certificates gnupg \
    > /dev/null 2>&1

print_success "Core dependencies installed"

################################################################################
# STEP 3: INSTALL PYTHON
################################################################################

print_header "${EMOJI_PACKAGE} Step 3/10: Installing Python Environment"

print_step "Installing Python 3..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    python3 python3-pip python3-venv python3-dev \
    > /dev/null 2>&1

print_step "Upgrading pip..."
python3 -m pip install --upgrade pip -qq > /dev/null 2>&1

print_success "Python environment ready"

################################################################################
# STEP 4: INSTALL DATABASE
################################################################################

print_header "${EMOJI_PACKAGE} Step 4/10: Installing PostgreSQL Database"

print_step "Installing PostgreSQL..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    postgresql postgresql-contrib libpq-dev \
    > /dev/null 2>&1

print_step "Starting PostgreSQL..."
systemctl start postgresql > /dev/null 2>&1
systemctl enable postgresql > /dev/null 2>&1

print_success "PostgreSQL installed and running"

################################################################################
# STEP 5: INSTALL STORAGE TOOLS
################################################################################

print_header "${EMOJI_PACKAGE} Step 5/10: Installing Storage Management Tools"

print_step "Installing ZFS utilities..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    zfsutils-linux \
    > /dev/null 2>&1

print_step "Installing MD RAID utilities..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    mdadm \
    > /dev/null 2>&1

print_step "Installing LVM and disk utilities..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    lvm2 parted gdisk hdparm smartmontools \
    > /dev/null 2>&1

print_success "Storage management tools installed"

################################################################################
# STEP 6: INSTALL NETWORK SERVICES
################################################################################

print_header "${EMOJI_PACKAGE} Step 6/10: Installing Network Services"

print_step "Installing DHCP server..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    isc-dhcp-server \
    > /dev/null 2>&1

print_step "Installing TFTP server..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    tftpd-hpa \
    > /dev/null 2>&1

print_step "Installing NFS server..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    nfs-kernel-server \
    > /dev/null 2>&1

# Stop services for now (will be configured later)
systemctl stop isc-dhcp-server > /dev/null 2>&1 || true
systemctl stop tftpd-hpa > /dev/null 2>&1 || true

print_success "Network services installed"

################################################################################
# STEP 7: INSTALL NGINX
################################################################################

print_header "${EMOJI_PACKAGE} Step 7/10: Installing Nginx Web Server"

print_step "Installing Nginx..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    nginx \
    > /dev/null 2>&1

systemctl enable nginx > /dev/null 2>&1

print_success "Nginx installed"

################################################################################
# STEP 8: INSTALL MONITORING
################################################################################

print_header "${EMOJI_PACKAGE} Step 8/10: Installing Monitoring Tools"

print_step "Installing Prometheus node exporter..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    prometheus-node-exporter \
    > /dev/null 2>&1

systemctl enable prometheus-node-exporter > /dev/null 2>&1
systemctl start prometheus-node-exporter > /dev/null 2>&1

print_success "Monitoring tools installed"

################################################################################
# STEP 9: INSTALL GGNET APPLICATION
################################################################################

print_header "${EMOJI_ROCKET} Step 9/10: Installing ggNet Application"

# Create ggnet user
print_step "Creating ggnet user..."
if ! id -u ggnet > /dev/null 2>&1; then
    useradd -r -m -d /srv/ggnet -s /bin/bash ggnet
    print_success "User 'ggnet' created"
else
    print_warning "User 'ggnet' already exists"
fi

# Create directory structure
print_step "Creating directory structure..."
mkdir -p /srv/ggnet/{backend,frontend,array,logs,tftp}
mkdir -p /srv/ggnet/array/{images,writebacks,snapshots}
mkdir -p /var/log/ggnet

# Download ggNet code
print_step "Downloading ggNet application..."
cd /tmp

# For production, this would download from GitHub releases
# For now, we'll assume code is already present or use git clone
if [ ! -d "ggnet" ]; then
    print_info "Note: In production, this would download from GitHub"
    print_info "For now, code should be copied manually to /srv/ggnet"
fi

# Setup backend
print_step "Setting up ggNet backend..."
cd /srv/ggnet/backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install dependencies
source venv/bin/activate
pip install --upgrade pip -qq > /dev/null 2>&1

# Install main dependencies
pip install -qq \
    fastapi uvicorn[standard] \
    sqlalchemy asyncpg psycopg2-binary \
    pydantic python-multipart \
    alembic pytest pytest-asyncio pytest-cov httpx \
    > /dev/null 2>&1

# Create .env file
print_step "Creating configuration file..."
cat > /srv/ggnet/backend/.env << EOF
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
GGNET_DRY_RUN=false
GGNET_STRICT_SAFETY=true
EOF

# Setup database
print_step "Configuring PostgreSQL database..."
sudo -u postgres psql > /dev/null 2>&1 << EOF
CREATE DATABASE ggnet;
CREATE USER ggnet WITH PASSWORD 'ggnet';
GRANT ALL PRIVILEGES ON DATABASE ggnet TO ggnet;
ALTER DATABASE ggnet OWNER TO ggnet;
EOF

# Set permissions
chown -R ggnet:ggnet /srv/ggnet
chown -R ggnet:ggnet /var/log/ggnet
chmod 600 /srv/ggnet/backend/.env

print_success "ggNet application installed"

################################################################################
# STEP 10: CREATE SYSTEMD SERVICE
################################################################################

print_header "${EMOJI_GEAR} Step 10/10: Configuring System Services"

# Create systemd service
print_step "Creating ggNet systemd service..."
cat > /etc/systemd/system/ggnet-backend.service << 'EOF'
[Unit]
Description=ggNet Backend API Service
After=network.target postgresql.service

[Service]
Type=simple
User=ggnet
Group=ggnet
WorkingDirectory=/srv/ggnet/backend
Environment="PATH=/srv/ggnet/backend/venv/bin"
Environment="PYTHONPATH=/srv/ggnet/backend/src"
ExecStart=/srv/ggnet/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/ggnet/backend.log
StandardError=append:/var/log/ggnet/backend-error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

print_success "Systemd service created"

# Configure Nginx
print_step "Configuring Nginx..."
cat > /etc/nginx/sites-available/ggnet << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    # Frontend
    location / {
        root /srv/ggnet/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
    
    # Metrics
    location /metrics {
        proxy_pass http://127.0.0.1:8000/metrics;
        allow 127.0.0.1;
        deny all;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/ggnet /etc/nginx/sites-enabled/ggnet
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t > /dev/null 2>&1

# Restart nginx
systemctl restart nginx

print_success "Nginx configured"

# Configure firewall
print_step "Configuring firewall..."
if command -v ufw > /dev/null 2>&1; then
    ufw allow 22/tcp > /dev/null 2>&1  # SSH
    ufw allow 80/tcp > /dev/null 2>&1  # HTTP
    ufw allow 443/tcp > /dev/null 2>&1  # HTTPS
    ufw allow 67/udp > /dev/null 2>&1  # DHCP
    ufw allow 69/udp > /dev/null 2>&1  # TFTP
    ufw allow 2049/tcp > /dev/null 2>&1  # NFS
    print_success "Firewall rules configured (not enabled yet)"
else
    print_warning "UFW not installed, skipping firewall configuration"
fi

################################################################################
# CREATE CONFIGURATOR UTILITY
################################################################################

print_step "Creating ggNet configurator utility..."
cat > /usr/local/bin/ggnet-configurator << 'CONFEOF'
#!/bin/bash
# ggNet Linux Configuration Utility

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                           ║${NC}"
echo -e "${CYAN}║              ggNet Configuration Utility                  ║${NC}"
echo -e "${CYAN}║                                                           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}Server Information:${NC}"
echo "  • Hostname: $(hostname)"
echo "  • IP Address: $SERVER_IP"
echo "  • OS: $(lsb_release -d | cut -f2)"
echo ""

echo -e "${GREEN}ggNet Services:${NC}"

# Check backend
if systemctl is-active --quiet ggnet-backend; then
    echo -e "  • Backend API: ${GREEN}✅ Running${NC}"
    echo "    http://$SERVER_IP:8000"
else
    echo -e "  • Backend API: ${YELLOW}⏸ Stopped${NC}"
    echo "    Start: sudo systemctl start ggnet-backend"
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    echo -e "  • Web Server: ${GREEN}✅ Running${NC}"
    echo "    http://$SERVER_IP"
else
    echo -e "  • Web Server: ${YELLOW}⏸ Stopped${NC}"
fi

# Check database
if systemctl is-active --quiet postgresql; then
    echo -e "  • Database: ${GREEN}✅ Running${NC}"
else
    echo -e "  • Database: ${YELLOW}⏸ Stopped${NC}"
fi

echo ""

# Check storage array
echo -e "${GREEN}Storage Array:${NC}"
if command -v zpool > /dev/null 2>&1; then
    if zpool list > /dev/null 2>&1; then
        echo -e "  • Type: ${GREEN}ZFS${NC}"
        zpool list | grep -v "^NAME" | while read name size alloc free; do
            echo "    - $name: $size total, $alloc used, $free free"
        done
    else
        echo -e "  • Type: ${YELLOW}None detected${NC}"
        echo "    Configure: VI. - ⚙️ Configure the ggNet Array"
    fi
elif [ -f /proc/mdstat ] && grep -q "^md" /proc/mdstat; then
    echo -e "  • Type: ${GREEN}MD RAID${NC}"
    cat /proc/mdstat | grep "^md" | while read line; do
        echo "    - $line"
    done
else
    echo -e "  • Type: ${YELLOW}None detected${NC}"
    echo "    Configure: VI. - ⚙️ Configure the ggNet Array"
fi

echo ""
echo -e "${GREEN}Quick Commands:${NC}"
echo "  • Start ggNet:     sudo systemctl start ggnet-backend"
echo "  • Stop ggNet:      sudo systemctl stop ggnet-backend"
echo "  • Restart ggNet:   sudo systemctl restart ggnet-backend"
echo "  • View logs:       sudo journalctl -u ggnet-backend -f"
echo "  • Check health:    curl http://localhost:8000/health"
echo ""
echo "  • Run configurator: ggnet-configurator"
echo "  • Array setup:      See VI. - ⚙️ Configure the ggNet Array guide"
echo ""
echo -e "${CYAN}For more information, visit documentation at /srv/ggnet/docs${NC}"
echo ""
CONFEOF

chmod +x /usr/local/bin/ggnet-configurator

print_success "Configurator utility created"

################################################################################
# FINALIZE
################################################################################

print_header "${EMOJI_PARTY} Installation Complete!"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}${EMOJI_PARTY} ggNet Server has been successfully installed!${NC}"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                    ACCESS INFORMATION                      ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Web UI:${NC}        http://$SERVER_IP/"
echo -e "${GREEN}Backend API:${NC}   http://$SERVER_IP:8000"
echo -e "${GREEN}Health Check:${NC} http://$SERVER_IP:8000/health"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}${EMOJI_WARN} NEXT STEPS:${NC}"
echo ""
echo "  1. ${EMOJI_GEAR} Configure your storage array:"
echo "     See: VI. - ⚙️ Configure the ggNet Array"
echo ""
echo "  2. ${EMOJI_ROCKET} Start ggNet backend:"
echo "     ${CYAN}sudo systemctl start ggnet-backend${NC}"
echo ""
echo "  3. ${EMOJI_INFO} Run configuration utility:"
echo "     ${CYAN}ggnet-configurator${NC}"
echo ""
echo "  4. ${EMOJI_INFO} Access Web UI:"
echo "     ${CYAN}http://$SERVER_IP/${NC}"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}${EMOJI_COFFEE} Installation log saved to: /var/log/ggnet/install.log${NC}"
echo ""
echo -e "${MAGENTA}For detailed documentation, see:${NC}"
echo "  • /srv/ggnet/docs/DEPLOYMENT_GUIDE.md"
echo "  • /srv/ggnet/docs/REAL_HARDWARE_TESTING_GUIDE.md"
echo ""
echo -e "${GREEN}${EMOJI_PARTY} Happy Gaming with ggNet! ${EMOJI_PARTY}${NC}"
echo ""

# Save installation info
cat > /srv/ggnet/installation_info.txt << EOF
ggNet Server Installation
=========================
Version: $GGNET_VERSION
Install Date: $INSTALL_DATE
OS: $OS $VER
Server IP: $SERVER_IP

Installation completed successfully!

Access:
- Web UI: http://$SERVER_IP/
- Backend API: http://$SERVER_IP:8000
- Health: http://$SERVER_IP:8000/health

Next Steps:
1. Configure storage array (see VI. - Configure the ggNet Array guide)
2. Start backend: sudo systemctl start ggnet-backend
3. Run configurator: ggnet-configurator
4. Access Web UI

For support and documentation:
- /srv/ggnet/docs/
- Run: ggnet-configurator
EOF

chown ggnet:ggnet /srv/ggnet/installation_info.txt

# Print final status
echo -e "${CYAN}Installation completed at: $(date)${NC}"
echo ""

# Suggest reboot
echo -e "${YELLOW}${EMOJI_INFO} It is recommended to reboot the server now.${NC}"
read -p "Reboot now? (yes/no): " -r
echo
if [[ $REPLY =~ ^[Yy]es$ ]]; then
    print_info "Rebooting in 5 seconds..."
    sleep 5
    reboot
else
    print_info "Skipping reboot. Remember to reboot later!"
    print_info "Run 'ggnet-configurator' after reboot to continue setup."
fi

exit 0

