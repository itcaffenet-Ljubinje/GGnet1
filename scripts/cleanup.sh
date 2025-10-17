#!/bin/bash
################################################################################
# ggNet Cleanup Script
#
# Cleans temporary files, caches, and old logs from ggNet installation.
# Safe to run periodically (e.g., via cron).
#
# Usage:
#   sudo ./scripts/cleanup.sh
#   sudo ./scripts/cleanup.sh --aggressive  # More thorough cleanup
#   sudo ./scripts/cleanup.sh --dry-run     # Show what would be deleted
################################################################################

set -u  # Exit on undefined variable

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/ggnet"
DATA_DIR="/srv/ggnet"
LOG_DIR="/var/log/ggnet"

# Parse arguments
AGGRESSIVE=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --aggressive) AGGRESSIVE=true ;;
        --dry-run) DRY_RUN=true ;;
        --help)
            echo "ggNet Cleanup Script"
            echo ""
            echo "Usage: sudo $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --aggressive  More thorough cleanup (removes builds, caches)"
            echo "  --dry-run     Show what would be deleted without deleting"
            echo "  --help        Show this help"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ggNet Cleanup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN MODE - No files will be deleted${NC}"
    echo
fi

# Track cleanup stats
FILES_DELETED=0
SPACE_FREED=0

################################################################################
# Function: Delete Files
################################################################################

delete_path() {
    local path=$1
    local description=$2
    
    if [ ! -e "$path" ]; then
        return
    fi
    
    # Get size before deletion
    if [ -f "$path" ]; then
        size=$(du -sb "$path" 2>/dev/null | cut -f1 || echo "0")
    elif [ -d "$path" ]; then
        size=$(du -sb "$path" 2>/dev/null | cut -f1 || echo "0")
    else
        size=0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}Would delete:${NC} $path ($description)"
        if [ -d "$path" ]; then
            count=$(find "$path" -type f 2>/dev/null | wc -l)
            echo "  Contains $count files, $(du -sh "$path" 2>/dev/null | cut -f1 || echo '0')"
        fi
    else
        echo -e "${GREEN}Deleting:${NC} $path ($description)"
        rm -rf "$path"
        FILES_DELETED=$((FILES_DELETED + 1))
        SPACE_FREED=$((SPACE_FREED + size))
    fi
}

################################################################################
# Step 1: Clean Python Cache
################################################################################

echo -e "${BLUE}[1/7] Cleaning Python cache files...${NC}"

# Find and delete __pycache__ directories
if [ -d "$INSTALL_DIR/backend" ]; then
    while IFS= read -r -d '' pycache; do
        delete_path "$pycache" "Python cache"
    done < <(find "$INSTALL_DIR/backend" -type d -name "__pycache__" -print0 2>/dev/null)
    
    # Delete .pyc files
    while IFS= read -r -d '' pyc; do
        delete_path "$pyc" "Python compiled"
    done < <(find "$INSTALL_DIR/backend" -type f -name "*.pyc" -print0 2>/dev/null)
    
    # Delete .pyo files
    while IFS= read -r -d '' pyo; do
        delete_path "$pyo" "Python optimized"
    done < <(find "$INSTALL_DIR/backend" -type f -name "*.pyo" -print0 2>/dev/null)
fi

echo -e "${GREEN}✅ Python cache cleaned${NC}"
echo

################################################################################
# Step 2: Clean Node.js Cache
################################################################################

echo -e "${BLUE}[2/7] Cleaning Node.js cache files...${NC}"

if [ -d "$INSTALL_DIR/frontend" ]; then
    # Clean npm cache (if running as user)
    if [ -d "$HOME/.npm" ] && [ "$DRY_RUN" = false ]; then
        npm cache clean --force 2>/dev/null || true
        echo "  Cleaned npm cache"
    fi
    
    # Delete node_modules/.cache
    if [ -d "$INSTALL_DIR/frontend/node_modules/.cache" ]; then
        delete_path "$INSTALL_DIR/frontend/node_modules/.cache" "Vite build cache"
    fi
fi

echo -e "${GREEN}✅ Node.js cache cleaned${NC}"
echo

################################################################################
# Step 3: Clean Temporary Files
################################################################################

echo -e "${BLUE}[3/7] Cleaning temporary files...${NC}"

# SQLite temporary files
delete_path "$INSTALL_DIR/backend/ggnet.db-journal" "SQLite journal"
delete_path "$INSTALL_DIR/backend/ggnet.db-wal" "SQLite WAL"
delete_path "$INSTALL_DIR/backend/ggnet.db-shm" "SQLite shared memory"

# Temporary directories
delete_path "/tmp/ggnet-*" "Temporary files"

echo -e "${GREEN}✅ Temporary files cleaned${NC}"
echo

################################################################################
# Step 4: Clean Old Logs
################################################################################

echo -e "${BLUE}[4/7] Cleaning old log files...${NC}"

if [ -d "$LOG_DIR" ]; then
    # Delete logs older than 30 days
    find "$LOG_DIR" -type f -name "*.log" -mtime +30 -print0 2>/dev/null | while IFS= read -r -d '' log; do
        delete_path "$log" "Old log file"
    done
    
    # Compress logs older than 7 days
    if [ "$DRY_RUN" = false ]; then
        find "$LOG_DIR" -type f -name "*.log" -mtime +7 ! -name "*.gz" -print0 2>/dev/null | while IFS= read -r -d '' log; do
            if [ -f "$log" ]; then
                echo "  Compressing: $log"
                gzip "$log" 2>/dev/null || true
            fi
        done
    fi
fi

# Clean systemd journal (keep last 7 days)
if [ "$DRY_RUN" = false ]; then
    journalctl --vacuum-time=7d 2>/dev/null || true
    echo "  Cleaned systemd journal"
fi

echo -e "${GREEN}✅ Old logs cleaned${NC}"
echo

################################################################################
# Step 5: Clean Old Writebacks (if not marked as 'keep')
################################################################################

echo -e "${BLUE}[5/7] Cleaning old writebacks...${NC}"

if [ -d "$DATA_DIR/writebacks" ] && [ -x "$INSTALL_DIR/backend/venv/bin/python" ]; then
    if [ "$DRY_RUN" = false ]; then
        cd "$INSTALL_DIR"
        ./backend/venv/bin/python storage/writeback_manager.py cleanup 30 2>/dev/null || true
        echo "  Cleaned old writebacks (>30 days, not marked as keep)"
    else
        echo -e "${YELLOW}Would clean writebacks older than 30 days${NC}"
    fi
fi

echo -e "${GREEN}✅ Old writebacks processed${NC}"
echo

################################################################################
# Step 6: Aggressive Cleanup (optional)
################################################################################

if [ "$AGGRESSIVE" = true ]; then
    echo -e "${BLUE}[6/7] Aggressive cleanup...${NC}"
    
    # Delete frontend node_modules (can be reinstalled)
    if [ -d "$INSTALL_DIR/frontend/node_modules" ]; then
        delete_path "$INSTALL_DIR/frontend/node_modules" "Node.js modules (will need npm install)"
    fi
    
    # Delete frontend dist (can be rebuilt)
    if [ -d "$INSTALL_DIR/frontend/dist" ]; then
        delete_path "$INSTALL_DIR/frontend/dist" "Frontend build (will need npm run build)"
    fi
    
    # Delete Python venv (can be recreated)
    if [ -d "$INSTALL_DIR/backend/venv" ]; then
        delete_path "$INSTALL_DIR/backend/venv" "Python venv (will need reinstall)"
    fi
    
    echo -e "${GREEN}✅ Aggressive cleanup complete${NC}"
    echo -e "${YELLOW}⚠️  You'll need to run install.sh again to restore dependencies${NC}"
else
    echo -e "${BLUE}[6/7] Skipping aggressive cleanup${NC}"
    echo "  Use --aggressive to also clean node_modules, dist, and venv"
fi
echo

################################################################################
# Step 7: Summary
################################################################################

echo -e "${BLUE}[7/7] Cleanup summary${NC}"
echo

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN COMPLETE${NC}"
    echo "  No files were actually deleted"
    echo "  Run without --dry-run to perform cleanup"
else
    # Convert bytes to human-readable
    if [ $SPACE_FREED -gt 0 ]; then
        if [ $SPACE_FREED -gt 1073741824 ]; then
            freed_gb=$(echo "scale=2; $SPACE_FREED / 1073741824" | bc)
            freed_display="${freed_gb} GB"
        elif [ $SPACE_FREED -gt 1048576 ]; then
            freed_mb=$(echo "scale=2; $SPACE_FREED / 1048576" | bc)
            freed_display="${freed_mb} MB"
        else
            freed_kb=$(echo "scale=2; $SPACE_FREED / 1024" | bc)
            freed_display="${freed_kb} KB"
        fi
    else
        freed_display="0 KB"
    fi
    
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
    echo "  Files deleted: $FILES_DELETED"
    echo "  Space freed: $freed_display"
fi

echo
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Cleanup Finished${NC}"
echo -e "${BLUE}========================================${NC}"

