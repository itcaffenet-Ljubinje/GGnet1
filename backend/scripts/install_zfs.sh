#!/bin/bash
#
# Install ZFS on Debian/Ubuntu Server
#
# This script installs ZFS kernel modules and utilities
# Required for ggNet storage array management
#
# Usage:
#   sudo bash install_zfs.sh
#

set -e

echo "======================================================================"
echo "ggNet - ZFS Installation Script"
echo "======================================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ ERROR: This script must be run as root"
    echo "   Run: sudo bash install_zfs.sh"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "❌ ERROR: Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Install ZFS based on OS
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "[1/4] Updating package lists..."
    apt-get update
    
    echo ""
    echo "[2/4] Installing ZFS packages..."
    
    # Install ZFS
    if [ "$OS" = "ubuntu" ]; then
        apt-get install -y zfsutils-linux
    elif [ "$OS" = "debian" ]; then
        # Debian requires contrib repo for ZFS
        echo "deb http://deb.debian.org/debian $(lsb_release -sc) contrib" | tee /etc/apt/sources.list.d/contrib.list
        apt-get update
        apt-get install -y linux-headers-$(uname -r)
        apt-get install -y zfs-dkms zfsutils-linux
    fi
    
    echo ""
    echo "[3/4] Loading ZFS kernel module..."
    modprobe zfs || echo "⚠️  Warning: Could not load ZFS module (may need reboot)"
    
    echo ""
    echo "[4/4] Verifying installation..."
    
    if command -v zpool &> /dev/null; then
        echo "✅ ZFS installed successfully!"
        zpool --version
        zfs --version
    else
        echo "❌ ERROR: ZFS installation failed"
        exit 1
    fi
    
else
    echo "❌ ERROR: Unsupported OS: $OS"
    echo "   Supported: Ubuntu, Debian"
    exit 1
fi

echo ""
echo "======================================================================"
echo "✅ ZFS Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Create ZFS pool:"
echo "   sudo zpool create pool0 mirror /dev/sdb /dev/sdc"
echo ""
echo "2. Verify pool:"
echo "   sudo zpool status"
echo ""
echo "3. Create ggNet storage structure:"
echo "   sudo zfs create pool0/ggnet"
echo "   sudo zfs create pool0/ggnet/images"
echo "   sudo zfs create pool0/ggnet/snapshots"
echo "   sudo zfs create pool0/ggnet/writebacks"
echo ""
echo "4. Set ownership:"
echo "   sudo chown -R ggnet:ggnet /pool0/ggnet"
echo ""
echo "5. Verify in ggNet UI:"
echo "   http://$(hostname -I | awk '{print $1}')/storage"
echo ""

