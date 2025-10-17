#!/bin/bash

# RAID Array Status Check Script

echo "=================================="
echo "RAID Array Status"
echo "=================================="
echo

# Check mdstat
echo "📊 Array Status:"
cat /proc/mdstat
echo

# Check array details
if [ -e /dev/md0 ]; then
    echo "📋 Array Details:"
    mdadm --detail /dev/md0
    echo
    
    echo "💾 Filesystem:"
    df -h /dev/md0
    echo
else
    echo "⚠️  No RAID array found at /dev/md0"
fi

# Check disk health
echo "🔍 Disk Health (SMART):"
for disk in /dev/sd[a-z]; do
    if [ -e "$disk" ]; then
        echo "  $disk:"
        smartctl -H "$disk" 2>/dev/null | grep "SMART overall-health" || echo "    SMART not available"
    fi
done
echo

echo "=================================="

