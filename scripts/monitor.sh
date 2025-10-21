#!/bin/bash
################################################################################
# ggNet Monitoring Script
#
# This script monitors ggNet services and sends alerts if issues are detected.
#
# Usage:
#   ./monitor.sh [--email <email>] [--webhook <url>]
#
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ALERT_EMAIL=""
WEBHOOK_URL=""
LOG_FILE="/var/log/ggnet/monitor.log"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --email)
            ALERT_EMAIL="$2"
            shift 2
            ;;
        --webhook)
            WEBHOOK_URL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

################################################################################
# Logging function
################################################################################
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

################################################################################
# Send alert
################################################################################
send_alert() {
    local service=$1
    local status=$2
    local message=$3
    
    log "ALERT: $service - $status - $message"
    
    # Send email
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "ggNet Alert: $service - $status" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    
    # Send webhook
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"service\":\"$service\",\"status\":\"$status\",\"message\":\"$message\"}" \
            2>/dev/null || true
    fi
}

################################################################################
# Check service status
################################################################################
check_service() {
    local service=$1
    local status=$(systemctl is-active "$service")
    
    if [ "$status" != "active" ]; then
        send_alert "$service" "DOWN" "Service is not running"
        return 1
    fi
    
    return 0
}

################################################################################
# Check disk space
################################################################################
check_disk_space() {
    local threshold=80
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt "$threshold" ]; then
        send_alert "DISK" "WARNING" "Disk usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
    
    return 0
}

################################################################################
# Check memory usage
################################################################################
check_memory() {
    local threshold=85
    local usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    
    if [ "$usage" -gt "$threshold" ]; then
        send_alert "MEMORY" "WARNING" "Memory usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
    
    return 0
}

################################################################################
# Check CPU usage
################################################################################
check_cpu() {
    local threshold=80
    local usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    
    if [ "$usage" -gt "$threshold" ]; then
        send_alert "CPU" "WARNING" "CPU usage is ${usage}% (threshold: ${threshold}%)"
        return 1
    fi
    
    return 0
}

################################################################################
# Check API health
################################################################################
check_api_health() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ "$response" != "200" ]; then
        send_alert "API" "DOWN" "API health check failed (HTTP $response)"
        return 1
    fi
    
    return 0
}

################################################################################
# Check database
################################################################################
check_database() {
    if ! sudo -u postgres psql -c "SELECT 1;" ggnet > /dev/null 2>&1; then
        send_alert "DATABASE" "DOWN" "Database connection failed"
        return 1
    fi
    
    return 0
}

################################################################################
# Main monitoring loop
################################################################################
main() {
    log "Starting ggNet monitoring..."
    
    local issues=0
    
    # Check services
    echo -e "${BLUE}Checking services...${NC}"
    check_service "ggnet-backend" || ((issues++))
    check_service "ggnet-frontend" || ((issues++))
    
    # Check resources
    echo -e "${BLUE}Checking resources...${NC}"
    check_disk_space || ((issues++))
    check_memory || ((issues++))
    check_cpu || ((issues++))
    
    # Check API
    echo -e "${BLUE}Checking API...${NC}"
    check_api_health || ((issues++))
    
    # Check database
    echo -e "${BLUE}Checking database...${NC}"
    check_database || ((issues++))
    
    # Summary
    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed${NC}"
        log "All checks passed"
    else
        echo -e "${RED}❌ $issues issue(s) detected${NC}"
        log "$issues issue(s) detected"
    fi
    
    return $issues
}

# Run monitoring
main
exit $?

