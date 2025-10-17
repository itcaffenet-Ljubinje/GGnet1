#!/bin/bash

# ggNet System Check Script
# Verifies all components are running correctly

echo "=================================="
echo "ggNet System Check"
echo "=================================="
echo

# Check backend service
echo "🔍 Checking backend service..."
if systemctl is-active --quiet ggnet-backend; then
    echo "✅ ggNet backend is running"
    systemctl status ggnet-backend --no-pager | head -n 3
else
    echo "❌ ggNet backend is NOT running"
    echo "   Start with: sudo systemctl start ggnet-backend"
fi
echo

# Check Nginx
echo "🔍 Checking Nginx..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx is NOT running"
fi
echo

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL is running"
    sudo -u postgres psql -d ggnet -c "SELECT 1;" &>/dev/null && echo "✅ Database 'ggnet' is accessible" || echo "❌ Database 'ggnet' not accessible"
else
    echo "❌ PostgreSQL is NOT running"
fi
echo

# Check API health
echo "🔍 Checking API health..."
if curl -s -f http://localhost:5000/health &>/dev/null; then
    echo "✅ API is responding"
    curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || echo "   Response received"
else
    echo "❌ API is NOT responding"
fi
echo

# Check disk space
echo "🔍 Checking disk space..."
df -h / | tail -n 1 | awk '{print "   Root: " $5 " used (" $4 " available)"}'
if [ -d "/pool0" ]; then
    df -h /pool0 | tail -n 1 | awk '{print "   Pool0: " $5 " used (" $4 " available)"}'
fi
echo

# Check memory
echo "🔍 Checking memory..."
free -h | grep Mem | awk '{print "   Total: " $2 ", Used: " $3 ", Available: " $7}'
echo

# Check network
echo "🔍 Checking network..."
hostname -I | awk '{print "   Server IP: " $1}'
echo

# Summary
echo "=================================="
echo "System Check Complete"
echo "=================================="

