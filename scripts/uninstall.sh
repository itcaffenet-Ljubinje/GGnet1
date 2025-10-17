#!/bin/bash
################################################################################
# ggNet Uninstallation Script
#
# Removes ggNet components and optionally removes data and RAID array.
# This script is safe and prompts before destructive operations.
#
# Usage:
#   sudo ./scripts/uninstall.sh
#   sudo ./scripts/uninstall.sh --purge-all    # Remove everything including data
#   sudo ./scripts/uninstall.sh --keep-data    # Keep data directories
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
GGNET_USER="ggnet"
INSTALL_DIR="/opt/ggnet"
DATA_DIR="/srv/ggnet"
CONFIG_DIR="/etc/ggnet"
LOG_DIR="/var/log/ggnet"

# Parse arguments
PURGE_ALL=false
KEEP_DATA=false

for arg in "$@"; do
    case $arg in
        --purge-all) PURGE_ALL=true ;;
        --keep-data) KEEP_DATA=true ;;
        --help)
            echo "ggNet Uninstallation Script"
            echo ""
            echo "Usage: sudo $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --purge-all   Remove everything including data (no prompts)"
            echo "  --keep-data   Keep data directories (images, writebacks)"
            echo "  --help        Show this help"
            exit 0
            ;;
    esac
done

echo -e "${RED}========================================${NC}"
echo -e "${RED}  ggNet Uninstallation Script${NC}"
echo -e "${RED}========================================${NC}"
echo
echo -e "${YELLOW}⚠️  WARNING: This will remove ggNet components${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ This script must be run as root${NC}"
    echo "   Usage: sudo $0"
    exit 1
fi

# Main confirmation
if [ "$PURGE_ALL" = false ]; then
    echo "This script will:"
    echo "  - Stop ggNet services"
    echo "  - Remove systemd units"
    echo "  - Remove Nginx configuration"
    echo "  - Remove application files from $INSTALL_DIR"
    echo
    read -p "Continue with uninstallation? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Uninstall cancelled."
        exit 0
    fi
fi

################################################################################
# Step 1: Stop Services
################################################################################

echo -e "${BLUE}[1/7] Stopping services...${NC}"

# Stop backend
if systemctl is-active --quiet ggnet-backend; then
    systemctl stop ggnet-backend
    echo -e "${GREEN}✅ Stopped ggnet-backend${NC}"
else
    echo -e "${YELLOW}ℹ️  ggnet-backend is not running${NC}"
fi

# Disable backend
if systemctl is-enabled --quiet ggnet-backend 2>/dev/null; then
    systemctl disable ggnet-backend
    echo -e "${GREEN}✅ Disabled ggnet-backend${NC}"
fi

echo

################################################################################
# Step 2: Remove Systemd Units
################################################################################

echo -e "${BLUE}[2/7] Removing systemd units...${NC}"

rm -f /etc/systemd/system/ggnet-backend.service
rm -f /etc/systemd/system/ggnet-frontend.service

systemctl daemon-reload
systemctl reset-failed || true

echo -e "${GREEN}✅ Systemd units removed${NC}"
echo

################################################################################
# Step 3: Remove Nginx Configuration
################################################################################

echo -e "${BLUE}[3/7] Removing Nginx configuration...${NC}"

rm -f /etc/nginx/sites-enabled/ggnet
rm -f /etc/nginx/sites-available/ggnet

# Test and reload Nginx
if nginx -t 2>/dev/null; then
    systemctl reload nginx || systemctl restart nginx
    echo -e "${GREEN}✅ Nginx configuration removed${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx configuration error (non-fatal)${NC}"
fi

echo

################################################################################
# Step 4: Remove Application Files
################################################################################

echo -e "${BLUE}[4/7] Removing application files...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    # Create backup before removal
    BACKUP_DIR="/tmp/ggnet-uninstall-backup-$(date +%Y%m%d-%H%M%S)"
    echo -e "${YELLOW}ℹ️  Creating backup at $BACKUP_DIR${NC}"
    mkdir -p $BACKUP_DIR
    
    # Backup config and logs
    [ -d "$CONFIG_DIR" ] && cp -r $CONFIG_DIR $BACKUP_DIR/ || true
    [ -d "$LOG_DIR" ] && cp -r $LOG_DIR $BACKUP_DIR/ || true
    
    # Remove installation directory
    rm -rf $INSTALL_DIR
    echo -e "${GREEN}✅ Removed $INSTALL_DIR${NC}"
    echo -e "${YELLOW}   Backup saved to: $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}ℹ️  $INSTALL_DIR does not exist${NC}"
fi

# Remove configuration
if [ -d "$CONFIG_DIR" ]; then
    rm -rf $CONFIG_DIR
    echo -e "${GREEN}✅ Removed $CONFIG_DIR${NC}"
fi

# Remove logs
if [ -d "$LOG_DIR" ]; then
    rm -rf $LOG_DIR
    echo -e "${GREEN}✅ Removed $LOG_DIR${NC}"
fi

echo

################################################################################
# Step 5: Handle Data Directory
################################################################################

echo -e "${BLUE}[5/7] Handling data directory...${NC}"

if [ "$PURGE_ALL" = true ]; then
    # Remove all data without prompting
    if [ -d "$DATA_DIR" ]; then
        echo -e "${RED}⚠️  Removing all data from $DATA_DIR${NC}"
        rm -rf $DATA_DIR
        echo -e "${GREEN}✅ Data directory removed${NC}"
    fi
elif [ "$KEEP_DATA" = true ]; then
    echo -e "${YELLOW}ℹ️  Keeping data directory: $DATA_DIR${NC}"
else
    # Ask user
    if [ -d "$DATA_DIR" ]; then
        echo "Data directory: $DATA_DIR"
        du -sh $DATA_DIR 2>/dev/null || true
        echo
        read -p "Remove $DATA_DIR (contains images, writebacks, snapshots)? (yes/no): " -r
        echo
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            rm -rf $DATA_DIR
            echo -e "${GREEN}✅ Data directory removed${NC}"
        else
            echo -e "${YELLOW}ℹ️  Keeping $DATA_DIR${NC}"
        fi
    fi
fi

echo

################################################################################
# Step 6: Handle RAID Array
################################################################################

echo -e "${BLUE}[6/7] Checking RAID array...${NC}"

# Check if RAID array exists
if [ -b /dev/md0 ] || grep -q "^md" /proc/mdstat 2>/dev/null; then
    echo -e "${YELLOW}⚠️  RAID array detected${NC}"
    cat /proc/mdstat
    echo
    
    if [ "$PURGE_ALL" = false ]; then
        echo "Found active RAID array(s)"
        echo -e "${RED}WARNING: Removing RAID will DESTROY all data on the array!${NC}"
        read -p "Remove RAID array? (yes/no): " -r
        echo
        
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            # Unmount
            if mount | grep -q "/dev/md"; then
                echo "Unmounting RAID arrays..."
                for mount in $(mount | grep "/dev/md" | awk '{print $3}'); do
                    umount $mount || true
                done
            fi
            
            # Stop arrays
            echo "Stopping RAID arrays..."
            mdadm --stop --scan || true
            
            # Remove from mdadm.conf
            if [ -f /etc/mdadm/mdadm.conf ]; then
                echo "Removing from mdadm.conf..."
                sed -i '/ARRAY.*ggnet/d' /etc/mdadm/mdadm.conf || true
            fi
            
            # Remove from fstab
            if grep -q "/srv/ggnet/array" /etc/fstab 2>/dev/null; then
                echo "Removing from /etc/fstab..."
                sed -i '/\/srv\/ggnet\/array/d' /etc/fstab
            fi
            
            echo -e "${GREEN}✅ RAID array stopped and removed from config${NC}"
            echo -e "${YELLOW}ℹ️  Physical disks are not wiped - data may still be recoverable${NC}"
        else
            echo -e "${YELLOW}ℹ️  Keeping RAID array${NC}"
        fi
    fi
else
    echo -e "${YELLOW}ℹ️  No RAID array detected${NC}"
fi

echo

################################################################################
# Step 7: Remove System User
################################################################################

echo -e "${BLUE}[7/7] Handling system user...${NC}"

if id "$GGNET_USER" &>/dev/null; then
    if [ "$PURGE_ALL" = true ]; then
        # Remove user without prompting
        userdel -r $GGNET_USER 2>/dev/null || userdel $GGNET_USER 2>/dev/null || true
        echo -e "${GREEN}✅ User $GGNET_USER removed${NC}"
    else
        # Ask user
        read -p "Remove system user '$GGNET_USER'? (yes/no): " -r
        echo
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            userdel -r $GGNET_USER 2>/dev/null || userdel $GGNET_USER 2>/dev/null || true
            echo -e "${GREEN}✅ User $GGNET_USER removed${NC}"
        else
            echo -e "${YELLOW}ℹ️  Keeping user $GGNET_USER${NC}"
        fi
    fi
else
    echo -e "${YELLOW}ℹ️  User $GGNET_USER does not exist${NC}"
fi

echo

################################################################################
# Final Status
################################################################################

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ggNet Uninstallation Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${BLUE}📊 What was removed:${NC}"
[ ! -d "$INSTALL_DIR" ] && echo "   ✅ Installation files"
[ ! -f "/etc/systemd/system/ggnet-backend.service" ] && echo "   ✅ Systemd services"
[ ! -f "/etc/nginx/sites-available/ggnet" ] && echo "   ✅ Nginx configuration"
echo
echo -e "${BLUE}📁 What remains:${NC}"
[ -d "$DATA_DIR" ] && echo "   📁 Data directory: $DATA_DIR"
id "$GGNET_USER" &>/dev/null && echo "   👤 User: $GGNET_USER"
[ -b /dev/md0 ] && echo "   💾 RAID array: /dev/md0"
echo
echo -e "${BLUE}🔄 Restore Options:${NC}"
if [ -d "/tmp/ggnet-uninstall-backup"* ]; then
    LATEST_BACKUP=$(ls -td /tmp/ggnet-uninstall-backup-* 2>/dev/null | head -1)
    echo "   Latest backup: $LATEST_BACKUP"
    echo "   To restore config: cp -r $LATEST_BACKUP/ggnet /etc/"
fi
echo
echo -e "${BLUE}💡 Clean System:${NC}"
if [ -d "$DATA_DIR" ] || id "$GGNET_USER" &>/dev/null || [ -b /dev/md0 ]; then
    echo "   To completely remove all traces:"
    echo "   sudo rm -rf $DATA_DIR"
    echo "   sudo userdel -r $GGNET_USER"
    echo "   sudo mdadm --stop /dev/md0 && sudo mdadm --remove /dev/md0"
fi
echo
echo -e "${GREEN}Uninstallation complete! 👋${NC}"
echo

exit 0


