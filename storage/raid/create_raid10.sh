#!/bin/bash
################################################################################
# ggNet RAID10 Array Creation Script
#
# Creates and configures a RAID10 array for ggNet storage.
# Supports environment variables and command-line arguments.
#
# Usage:
#   ./create_raid10.sh                           # Interactive mode
#   ./create_raid10.sh /dev/sda /dev/sdb ...     # With devices
#   DEVICES="/dev/sda /dev/sdb" ./create_raid10.sh  # With env var
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MOUNT_POINT="${GGNET_MOUNT_POINT:-/srv/ggnet/array}"
RAID_DEVICE="${RAID_DEVICE:-/dev/md0}"
RAID_LEVEL=10
MIN_DEVICES=4

echo -e "${BLUE}=================================="
echo "ggNet RAID10 Array Creation"
echo -e "==================================${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ This script must be run as root${NC}"
    echo "   Usage: sudo $0"
    exit 1
fi

# Check if mdadm is installed
if ! command -v mdadm &> /dev/null; then
    echo -e "${RED}❌ mdadm is not installed${NC}"
    echo "   Install with: apt-get install mdadm"
    exit 1
fi

################################################################################
# Function: Get block devices
################################################################################
get_devices() {
    # Priority: Command line args > Environment variable > Interactive
    
    if [ $# -ge $MIN_DEVICES ]; then
        # From command line arguments
        echo "$@"
    elif [ -n "$DEVICES" ]; then
        # From environment variable
        echo $DEVICES
    else
        # Interactive mode
        echo -e "${YELLOW}Available block devices:${NC}"
        lsblk -d -n -p -o NAME,SIZE,TYPE,MODEL | grep -E "disk|nvme"
        echo
        echo -e "${YELLOW}Enter $MIN_DEVICES or more device paths (space-separated):${NC}"
        echo "Example: /dev/sda /dev/sdb /dev/sdc /dev/sdd"
        read -p "> " user_input
        echo $user_input
    fi
}

################################################################################
# Function: Validate devices
################################################################################
validate_devices() {
    local devices=("$@")
    local count=${#devices[@]}
    
    echo -e "${BLUE}📋 Validating $count devices...${NC}"
    
    # Check minimum count
    if [ $count -lt $MIN_DEVICES ]; then
        echo -e "${RED}❌ RAID10 requires at least $MIN_DEVICES devices${NC}"
        echo "   You provided: $count"
        return 1
    fi
    
    # Check if count is even (RAID10 requirement)
    if [ $((count % 2)) -ne 0 ]; then
        echo -e "${RED}❌ RAID10 requires an even number of devices${NC}"
        echo "   You provided: $count (odd number)"
        return 1
    fi
    
    # Validate each device
    for dev in "${devices[@]}"; do
        # Check if device exists
        if [ ! -b "$dev" ]; then
            echo -e "${RED}❌ Device does not exist: $dev${NC}"
            return 1
        fi
        
        # Check if device is in use
        if grep -q "$dev" /proc/mounts; then
            echo -e "${RED}❌ Device is currently mounted: $dev${NC}"
            grep "$dev" /proc/mounts
            return 1
        fi
        
        # Check if device is part of existing RAID
        if mdadm --examine "$dev" &> /dev/null; then
            echo -e "${YELLOW}⚠️  Warning: $dev appears to be part of an existing RAID${NC}"
        fi
        
        echo -e "${GREEN}✅ $dev - $(lsblk -d -n -o SIZE "$dev")${NC}"
    done
    
    return 0
}

################################################################################
# Function: Calculate array size
################################################################################
calculate_array_size() {
    local devices=("$@")
    local count=${#devices[@]}
    
    # Get smallest device size
    local min_size=999999999999
    for dev in "${devices[@]}"; do
        local size=$(blockdev --getsize64 "$dev")
        if [ $size -lt $min_size ]; then
            min_size=$size
        fi
    done
    
    # RAID10 effective size = (total / 2) due to mirroring
    local total_size=$((min_size * count))
    local effective_size=$((total_size / 2))
    
    echo "Array configuration:"
    echo "  Devices: $count"
    echo "  Smallest device: $((min_size / 1024 / 1024 / 1024)) GB"
    echo "  Total raw capacity: $((total_size / 1024 / 1024 / 1024)) GB"
    echo "  Effective capacity: $((effective_size / 1024 / 1024 / 1024)) GB (RAID10 mirroring)"
}

################################################################################
# Function: Create RAID array
################################################################################
create_raid_array() {
    local devices=("$@")
    
    echo
    echo -e "${BLUE}📦 Creating RAID10 array...${NC}"
    
    # Create array
    mdadm --create $RAID_DEVICE \
        --level=$RAID_LEVEL \
        --raid-devices=${#devices[@]} \
        --assume-clean \
        "${devices[@]}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ RAID array created: $RAID_DEVICE${NC}"
    else
        echo -e "${RED}❌ Failed to create RAID array${NC}"
        return 1
    fi
    
    # Wait for array to become active
    echo "⏳ Waiting for array to become active..."
    sleep 3
    
    # Show initial status
    cat /proc/mdstat
}

################################################################################
# Function: Create filesystem
################################################################################
create_filesystem() {
    echo
    echo -e "${BLUE}💾 Creating ext4 filesystem...${NC}"
    
    # Create filesystem with options optimized for large files
    mkfs.ext4 \
        -L ggnet-array \
        -m 1 \
        -E lazy_itable_init=0,lazy_journal_init=0 \
        $RAID_DEVICE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Filesystem created${NC}"
    else
        echo -e "${RED}❌ Failed to create filesystem${NC}"
        return 1
    fi
}

################################################################################
# Function: Mount array
################################################################################
mount_array() {
    echo
    echo -e "${BLUE}📁 Mounting array...${NC}"
    
    # Create mount point
    mkdir -p $MOUNT_POINT
    
    # Mount
    mount $RAID_DEVICE $MOUNT_POINT
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Array mounted at: $MOUNT_POINT${NC}"
    else
        echo -e "${RED}❌ Failed to mount array${NC}"
        return 1
    fi
    
    # Add to fstab if not already present
    if ! grep -q "$RAID_DEVICE" /etc/fstab; then
        echo "$RAID_DEVICE $MOUNT_POINT ext4 defaults,noatime 0 2" >> /etc/fstab
        echo -e "${GREEN}✅ Added to /etc/fstab${NC}"
    fi
}

################################################################################
# Function: Create ggNet directory structure
################################################################################
create_directory_structure() {
    echo
    echo -e "${BLUE}📁 Creating ggNet directory structure...${NC}"
    
    # Create directories
    mkdir -p $MOUNT_POINT/images/os
    mkdir -p $MOUNT_POINT/images/games
    mkdir -p $MOUNT_POINT/writebacks
    mkdir -p $MOUNT_POINT/snapshots
    
    # Set permissions
    if id "ggnet" &>/dev/null; then
        chown -R ggnet:ggnet $MOUNT_POINT
        echo -e "${GREEN}✅ Set ownership to ggnet:ggnet${NC}"
    else
        echo -e "${YELLOW}⚠️  User 'ggnet' not found, using root ownership${NC}"
    fi
    
    # Set permissions
    chmod 755 $MOUNT_POINT
    chmod -R 755 $MOUNT_POINT/images
    chmod -R 755 $MOUNT_POINT/writebacks
    chmod -R 755 $MOUNT_POINT/snapshots
    
    echo -e "${GREEN}✅ Directory structure created:${NC}"
    tree -L 2 $MOUNT_POINT 2>/dev/null || ls -la $MOUNT_POINT
}

################################################################################
# Function: Save RAID configuration
################################################################################
save_raid_config() {
    echo
    echo -e "${BLUE}💾 Saving RAID configuration...${NC}"
    
    # Update mdadm.conf
    mdadm --detail --scan >> /etc/mdadm/mdadm.conf
    
    # Update initramfs
    update-initramfs -u
    
    echo -e "${GREEN}✅ RAID configuration saved${NC}"
}

################################################################################
# Main Script
################################################################################

# Get devices
device_list=($(get_devices "$@"))

# Show warning
echo -e "${RED}⚠️  WARNING: This will ERASE all data on the selected devices!${NC}"
echo

# Show devices
echo "Selected devices:"
for dev in "${device_list[@]}"; do
    echo "  - $dev ($(lsblk -d -n -o SIZE "$dev"))"
done
echo

# Validate devices
if ! validate_devices "${device_list[@]}"; then
    echo -e "${RED}❌ Device validation failed${NC}"
    exit 1
fi

echo
calculate_array_size "${device_list[@]}"
echo

# Confirmation
if [ -z "$GGNET_AUTO_CONFIRM" ]; then
    echo -e "${YELLOW}Are you sure you want to create RAID10 array?${NC}"
    echo "This will DESTROY all data on the devices listed above!"
    read -p "Type 'yes' to continue: " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo "Cancelled by user."
        exit 0
    fi
fi

# Execute steps
create_raid_array "${device_list[@]}" || exit 1
create_filesystem || exit 1
mount_array || exit 1
create_directory_structure || exit 1
save_raid_config || exit 1

# Final status
echo
echo -e "${GREEN}=================================="
echo "✅ RAID10 Array Created Successfully!"
echo -e "==================================${NC}"
echo
echo "Configuration:"
echo "  Device: $RAID_DEVICE"
echo "  Mount point: $MOUNT_POINT"
echo "  RAID level: RAID$RAID_LEVEL"
echo "  Devices: ${#device_list[@]}"
echo
echo "Directory structure:"
echo "  $MOUNT_POINT/images/os/       - OS images"
echo "  $MOUNT_POINT/images/games/    - Game images"
echo "  $MOUNT_POINT/writebacks/      - Client writebacks"
echo "  $MOUNT_POINT/snapshots/       - Snapshots"
echo
echo "Next steps:"
echo "  1. Monitor array rebuild: watch cat /proc/mdstat"
echo "  2. Check array details: mdadm --detail $RAID_DEVICE"
echo "  3. Check mount: df -h $MOUNT_POINT"
echo "  4. Update backend config: GGNET_IMAGE_PATH=$MOUNT_POINT/images"
echo
echo "Management commands:"
echo "  Check status: mdadm --detail $RAID_DEVICE"
echo "  Monitor rebuild: cat /proc/mdstat"
echo "  Array info: mdadm --examine ${device_list[0]}"
echo

exit 0


