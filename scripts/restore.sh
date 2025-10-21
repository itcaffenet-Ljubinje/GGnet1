#!/bin/bash
################################################################################
# ggNet Restore Script
#
# This script restores ggNet from a backup.
#
# Usage:
#   sudo ./restore.sh <backup_directory>
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
BACKUP_DIR="$1"
GGNET_HOME="/opt/ggnet"
DATA_DIR="/var/lib/ggnet"
LOG_DIR="/var/log/ggnet"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║              ggNet Restore Script                         ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# Check if running as root
################################################################################
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

################################################################################
# Validate backup directory
################################################################################
if [ -z "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Please provide backup directory${NC}"
    echo -e "${YELLOW}Usage: sudo ./restore.sh <backup_directory>${NC}"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backup directory found: $BACKUP_DIR${NC}"
echo ""

################################################################################
# Confirm restore
################################################################################
echo -e "${YELLOW}⚠ WARNING: This will restore data from backup!${NC}"
echo -e "${YELLOW}⚠ Existing data may be overwritten!${NC}"
echo ""
read -p "Do you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ Restore cancelled${NC}"
    exit 1
fi

################################################################################
# Stop services
################################################################################
echo -e "${BLUE}[1/6] Stopping services...${NC}"
systemctl stop ggnet-backend || true
systemctl stop ggnet-frontend || true
echo -e "${GREEN}✅ Services stopped${NC}"
echo ""

################################################################################
# Restore database
################################################################################
echo -e "${BLUE}[2/6] Restoring database...${NC}"
if [ -f "$BACKUP_DIR/database/ggnet.sql" ]; then
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS ggnet;"
    sudo -u postgres psql -c "CREATE DATABASE ggnet;"
    sudo -u postgres psql ggnet < "$BACKUP_DIR/database/ggnet.sql"
    echo -e "${GREEN}✅ Database restored${NC}"
else
    echo -e "${YELLOW}⚠ Database backup not found, skipping...${NC}"
fi
echo ""

################################################################################
# Restore configuration
################################################################################
echo -e "${BLUE}[3/6] Restoring configuration...${NC}"

# Backend configuration
if [ -f "$BACKUP_DIR/config/backend.env" ]; then
    cp "$BACKUP_DIR/config/backend.env" "$GGNET_HOME/backend/.env"
    echo -e "${GREEN}✅ Backend configuration restored${NC}"
fi

# Frontend configuration
if [ -f "$BACKUP_DIR/config/frontend.env" ]; then
    cp "$BACKUP_DIR/config/frontend.env" "$GGNET_HOME/frontend/.env"
    echo -e "${GREEN}✅ Frontend configuration restored${NC}"
fi

# Nginx configuration
if [ -f "$BACKUP_DIR/config/nginx.conf" ]; then
    cp "$BACKUP_DIR/config/nginx.conf" /etc/nginx/sites-available/ggnet
    nginx -t
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx configuration restored${NC}"
fi

# Systemd services
if [ -f "$BACKUP_DIR/config/ggnet-backend.service" ]; then
    cp "$BACKUP_DIR/config/ggnet-backend.service" /etc/systemd/system/
    systemctl daemon-reload
    echo -e "${GREEN}✅ Backend service restored${NC}"
fi

if [ -f "$BACKUP_DIR/config/ggnet-frontend.service" ]; then
    cp "$BACKUP_DIR/config/ggnet-frontend.service" /etc/systemd/system/
    systemctl daemon-reload
    echo -e "${GREEN}✅ Frontend service restored${NC}"
fi

echo ""

################################################################################
# Restore data
################################################################################
echo -e "${BLUE}[4/6] Restoring data...${NC}"

# Restore images
if [ -f "$BACKUP_DIR/data/images.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/data/images.tar.gz" -C "$DATA_DIR"
    echo -e "${GREEN}✅ Images restored${NC}"
fi

# Restore writebacks
if [ -f "$BACKUP_DIR/data/writebacks.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/data/writebacks.tar.gz" -C "$DATA_DIR"
    echo -e "${GREEN}✅ Writebacks restored${NC}"
fi

# Restore snapshots
if [ -f "$BACKUP_DIR/data/snapshots.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/data/snapshots.tar.gz" -C "$DATA_DIR"
    echo -e "${GREEN}✅ Snapshots restored${NC}"
fi

echo ""

################################################################################
# Restore logs
################################################################################
echo -e "${BLUE}[5/6] Restoring logs...${NC}"
if [ -f "$BACKUP_DIR/logs/ggnet-logs.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/logs/ggnet-logs.tar.gz" -C "$LOG_DIR"
    echo -e "${GREEN}✅ Logs restored${NC}"
fi
echo ""

################################################################################
# Start services
################################################################################
echo -e "${BLUE}[6/6] Starting services...${NC}"
systemctl start ggnet-backend
systemctl start ggnet-frontend
echo -e "${GREEN}✅ Services started${NC}"
echo ""

################################################################################
# Restore Complete
################################################################################
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║              Restore Complete!                              ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Check service status:${NC}"
echo -e "${YELLOW}  sudo systemctl status ggnet-backend${NC}"
echo -e "${YELLOW}  sudo systemctl status ggnet-frontend${NC}"
echo ""
echo -e "${BLUE}View logs:${NC}"
echo -e "${YELLOW}  sudo journalctl -u ggnet-backend -f${NC}"
echo -e "${YELLOW}  sudo journalctl -u ggnet-frontend -f${NC}"
echo ""

