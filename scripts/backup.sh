#!/bin/bash
################################################################################
# ggNet Backup Script
#
# This script creates a backup of ggNet data and configuration.
#
# Usage:
#   sudo ./backup.sh [destination]
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
BACKUP_BASE_DIR="${1:-/var/backups/ggnet}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_BASE_DIR}/${TIMESTAMP}"
GGNET_HOME="/opt/ggnet"
DATA_DIR="/var/lib/ggnet"
LOG_DIR="/var/log/ggnet"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║              ggNet Backup Script                          ║${NC}"
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
# Create backup directory
################################################################################
echo -e "${BLUE}[1/6] Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup directory created: $BACKUP_DIR${NC}"
echo ""

################################################################################
# Backup database
################################################################################
echo -e "${BLUE}[2/6] Backing up database...${NC}"
mkdir -p "$BACKUP_DIR/database"
sudo -u postgres pg_dump ggnet > "$BACKUP_DIR/database/ggnet.sql"
echo -e "${GREEN}✅ Database backed up${NC}"
echo ""

################################################################################
# Backup configuration
################################################################################
echo -e "${BLUE}[3/6] Backing up configuration...${NC}"
mkdir -p "$BACKUP_DIR/config"

# Backend configuration
if [ -f "$GGNET_HOME/backend/.env" ]; then
    cp "$GGNET_HOME/backend/.env" "$BACKUP_DIR/config/backend.env"
fi

# Frontend configuration
if [ -f "$GGNET_HOME/frontend/.env" ]; then
    cp "$GGNET_HOME/frontend/.env" "$BACKUP_DIR/config/frontend.env"
fi

# Nginx configuration
cp /etc/nginx/sites-available/ggnet "$BACKUP_DIR/config/nginx.conf"

# Systemd services
cp /etc/systemd/system/ggnet-backend.service "$BACKUP_DIR/config/"
cp /etc/systemd/system/ggnet-frontend.service "$BACKUP_DIR/config/"

echo -e "${GREEN}✅ Configuration backed up${NC}"
echo ""

################################################################################
# Backup data
################################################################################
echo -e "${BLUE}[4/6] Backing up data...${NC}"
mkdir -p "$BACKUP_DIR/data"

# Backup images
if [ -d "$DATA_DIR/images" ]; then
    tar -czf "$BACKUP_DIR/data/images.tar.gz" -C "$DATA_DIR" images
fi

# Backup writebacks
if [ -d "$DATA_DIR/writebacks" ]; then
    tar -czf "$BACKUP_DIR/data/writebacks.tar.gz" -C "$DATA_DIR" writebacks
fi

# Backup snapshots
if [ -d "$DATA_DIR/snapshots" ]; then
    tar -czf "$BACKUP_DIR/data/snapshots.tar.gz" -C "$DATA_DIR" snapshots
fi

echo -e "${GREEN}✅ Data backed up${NC}"
echo ""

################################################################################
# Backup logs
################################################################################
echo -e "${BLUE}[5/6] Backing up logs...${NC}"
mkdir -p "$BACKUP_DIR/logs"

if [ -d "$LOG_DIR" ]; then
    tar -czf "$BACKUP_DIR/logs/ggnet-logs.tar.gz" -C "$LOG_DIR" .
fi

echo -e "${GREEN}✅ Logs backed up${NC}"
echo ""

################################################################################
# Create backup manifest
################################################################################
echo -e "${BLUE}[6/6] Creating backup manifest...${NC}"
cat > "$BACKUP_DIR/manifest.txt" << EOF
ggNet Backup Manifest
=====================

Timestamp: $TIMESTAMP
Date: $(date)

Contents:
- Database: database/ggnet.sql
- Configuration: config/
- Data: data/
- Logs: logs/

Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)

EOF

echo -e "${GREEN}✅ Backup manifest created${NC}"
echo ""

################################################################################
# Cleanup old backups (keep last 7 days)
################################################################################
echo -e "${BLUE}Cleaning up old backups...${NC}"
find "$BACKUP_BASE_DIR" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Old backups cleaned up${NC}"
echo ""

################################################################################
# Backup Complete
################################################################################
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║              Backup Complete!                               ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Backup location: ${NC}$BACKUP_DIR"
echo -e "${BLUE}Backup size: ${NC}$(du -sh "$BACKUP_DIR" | cut -f1)"
echo ""
echo -e "${YELLOW}To restore this backup, run:${NC}"
echo -e "${YELLOW}  sudo ./restore.sh $BACKUP_DIR${NC}"
echo ""

