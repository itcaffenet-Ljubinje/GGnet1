#!/bin/bash

#############################################################################
# ggNet Backend - Linux Server Setup Script
#
# This script prepares a Debian/Ubuntu server for ggNet deployment
# Includes ZFS, MD RAID, and all required dependencies
#
# Usage: sudo bash setup_linux_server.sh
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
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
    print_error "Please run as root (sudo)"
    exit 1
fi

print_info "Starting ggNet Backend Linux Server Setup..."

#############################################################################
# 1. SYSTEM UPDATE
#############################################################################
print_info "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

print_success "System updated"

#############################################################################
# 2. INSTALL REQUIRED PACKAGES
#############################################################################
print_info "Installing required packages..."

# Core utilities
apt-get install -y -qq \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    lsof \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

print_success "Core utilities installed"

#############################################################################
# 3. INSTALL STORAGE MANAGEMENT TOOLS
#############################################################################
print_info "Installing storage management tools..."

# MD RAID tools
apt-get install -y -qq \
    mdadm

# ZFS tools
print_info "Installing ZFS..."
apt-get install -y -qq \
    zfsutils-linux

# LVM tools
apt-get install -y -qq \
    lvm2

# SMART monitoring
apt-get install -y -qq \
    smartmontools

# Disk utilities
apt-get install -y -qq \
    parted \
    gdisk \
    hdparm

print_success "Storage management tools installed"

#############################################################################
# 4. INSTALL NETWORK SERVICES
#############################################################################
print_info "Installing network services..."

# DHCP server
apt-get install -y -qq \
    isc-dhcp-server

# TFTP server
apt-get install -y -qq \
    tftpd-hpa

# NFS server
apt-get install -y -qq \
    nfs-kernel-server

# Samba (optional, for Windows compatibility)
apt-get install -y -qq \
    samba

print_success "Network services installed"

#############################################################################
# 5. INSTALL DATABASE
#############################################################################
print_info "Installing PostgreSQL..."

apt-get install -y -qq \
    postgresql \
    postgresql-contrib \
    libpq-dev

# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

print_success "PostgreSQL installed and started"

#############################################################################
# 6. INSTALL PYTHON DEPENDENCIES
#############################################################################
print_info "Setting up Python environment..."

# Upgrade pip
python3 -m pip install --upgrade pip -qq

# Install virtualenv
python3 -m pip install virtualenv -qq

print_success "Python environment ready"

#############################################################################
# 7. CREATE GGNET USER AND DIRECTORIES
#############################################################################
print_info "Creating ggNet user and directories..."

# Create ggnet user if doesn't exist
if ! id -u ggnet > /dev/null 2>&1; then
    useradd -r -m -d /srv/ggnet -s /bin/bash ggnet
    print_success "User 'ggnet' created"
else
    print_warning "User 'ggnet' already exists"
fi

# Create required directories
mkdir -p /srv/ggnet/array/images
mkdir -p /srv/ggnet/array/writebacks
mkdir -p /srv/ggnet/array/snapshots
mkdir -p /srv/ggnet/backend
mkdir -p /srv/ggnet/logs
mkdir -p /var/log/ggnet

# Set permissions
chown -R ggnet:ggnet /srv/ggnet
chmod -R 755 /srv/ggnet

print_success "Directories created"

#############################################################################
# 8. CONFIGURE ZFS (if not already configured)
#############################################################################
print_info "Checking ZFS configuration..."

# Load ZFS module
modprobe zfs || print_warning "ZFS module already loaded or not available"

# Check if ZFS pools exist
if ! zpool list > /dev/null 2>&1; then
    print_warning "No ZFS pools detected. You'll need to create one manually."
    print_info "Example: zpool create pool0 mirror /dev/sda /dev/sdb"
else
    print_success "ZFS pools detected:"
    zpool list
fi

#############################################################################
# 9. CONFIGURE MD RAID (check only)
#############################################################################
print_info "Checking MD RAID configuration..."

if mdadm --detail --scan > /dev/null 2>&1; then
    print_success "MD RAID arrays detected:"
    cat /proc/mdstat
else
    print_warning "No MD RAID arrays detected. You can create one manually."
    print_info "Example: mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{a,b,c,d}"
fi

#############################################################################
# 10. CONFIGURE NETWORK SERVICES
#############################################################################
print_info "Configuring network services..."

# Stop services (will be configured later)
systemctl stop isc-dhcp-server || true
systemctl stop tftpd-hpa || true
systemctl stop nfs-kernel-server || true

print_success "Network services ready for configuration"

#############################################################################
# 11. CONFIGURE FIREWALL (UFW)
#############################################################################
print_info "Configuring firewall..."

# Install UFW if not present
apt-get install -y -qq ufw

# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow backend API
ufw allow 8000/tcp

# Allow DHCP
ufw allow 67/udp
ufw allow 68/udp

# Allow TFTP
ufw allow 69/udp

# Allow NFS
ufw allow 2049/tcp

# Don't enable yet (user decision)
print_warning "Firewall rules configured but NOT enabled"
print_info "To enable: sudo ufw enable"

#############################################################################
# 12. SYSTEM TUNING
#############################################################################
print_info "Applying system tuning..."

# Increase file descriptors
cat >> /etc/sysctl.conf << EOF

# ggNet optimizations
fs.file-max = 2097152
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
vm.swappiness = 10
EOF

# Apply sysctl settings
sysctl -p > /dev/null 2>&1

print_success "System tuning applied"

#############################################################################
# 13. CREATE SYSTEMD SERVICE FILES
#############################################################################
print_info "Creating systemd service files..."

# Backend service
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
ExecStart=/srv/ggnet/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
print_success "Systemd service created: ggnet-backend.service"

#############################################################################
# 14. INSTALL MONITORING TOOLS
#############################################################################
print_info "Installing monitoring tools..."

# Prometheus
apt-get install -y -qq \
    prometheus \
    prometheus-node-exporter

# Enable node exporter
systemctl enable prometheus-node-exporter
systemctl start prometheus-node-exporter

print_success "Monitoring tools installed"

#############################################################################
# 15. SUMMARY
#############################################################################
echo ""
echo "==========================================================================="
print_success "ggNet Backend Linux Server Setup COMPLETE!"
echo "==========================================================================="
echo ""
print_info "Next steps:"
echo "  1. Copy backend code to /srv/ggnet/backend"
echo "  2. Run: sudo -u ggnet bash /srv/ggnet/backend/scripts/setup_backend.sh"
echo "  3. Configure database: sudo -u postgres psql -c \"CREATE DATABASE ggnet;\""
echo "  4. Create ZFS pool or MD RAID array (if needed)"
echo "  5. Start backend: sudo systemctl start ggnet-backend"
echo "  6. Enable on boot: sudo systemctl enable ggnet-backend"
echo ""
print_info "Installed components:"
echo "  ✓ Python 3 + pip + venv"
echo "  ✓ PostgreSQL database"
echo "  ✓ ZFS utilities (zpool, zfs)"
echo "  ✓ MD RAID utilities (mdadm)"
echo "  ✓ LVM utilities (lvm2)"
echo "  ✓ DHCP server (isc-dhcp-server)"
echo "  ✓ TFTP server (tftpd-hpa)"
echo "  ✓ NFS server (nfs-kernel-server)"
echo "  ✓ SMART monitoring (smartmontools)"
echo "  ✓ Prometheus + Node Exporter"
echo ""
print_info "Server information:"
echo "  • ggNet user: ggnet"
echo "  • ggNet home: /srv/ggnet"
echo "  • Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  • Logs: /var/log/ggnet"
echo ""
print_warning "IMPORTANT: Review and test storage operations before production use!"
echo "==========================================================================="

