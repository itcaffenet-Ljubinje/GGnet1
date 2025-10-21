# 🔧 ZFS Installation Guide for ggNet

## PROBLEM

```
sudo: zpool: command not found
```

This means **ZFS is not installed** on your server.

---

## ✅ SOLUTION - Install ZFS

### **Quick Install (Ubuntu/Debian):**

```bash
# SSH into server
ssh root@192.168.0.137

# Run install script
cd /opt/ggnet/backend
bash scripts/install_zfs.sh
```

---

### **Manual Installation:**

#### **Ubuntu 20.04/22.04/24.04:**

```bash
sudo apt-get update
sudo apt-get install -y zfsutils-linux

# Load kernel module
sudo modprobe zfs

# Verify
zpool --version
zfs --version
```

#### **Debian 11/12:**

```bash
# Enable contrib repository
echo "deb http://deb.debian.org/debian $(lsb_release -sc) contrib" | sudo tee /etc/apt/sources.list.d/contrib.list

# Update and install
sudo apt-get update
sudo apt-get install -y linux-headers-$(uname -r)
sudo apt-get install -y zfs-dkms zfsutils-linux

# Load kernel module
sudo modprobe zfs

# Verify
zpool --version
zfs --version
```

---

## 🗄️ CREATE ZFS POOL FOR GGNET

After installing ZFS, create the storage pool:

### **Example: RAID 10 (2x Mirror)**

```bash
# List available drives
lsblk

# Create pool with 2 mirror vdevs
sudo zpool create pool0 \
  mirror /dev/sdb /dev/sdc \
  mirror /dev/sdd /dev/sde

# Verify
sudo zpool status
```

### **Example: RAID Z2 (6 drives)**

```bash
sudo zpool create pool0 raidz2 /dev/sdb /dev/sdc /dev/sdd /dev/sde /dev/sdf /dev/sdg

sudo zpool status
```

### **Example: Simple Mirror (2 drives)**

```bash
sudo zpool create pool0 mirror /dev/sdb /dev/sdc

sudo zpool status
```

---

## 📁 CREATE GGNET FILESYSTEM STRUCTURE

```bash
# Create main dataset
sudo zfs create pool0/ggnet

# Create sub-datasets
sudo zfs create pool0/ggnet/images      # System and game images
sudo zfs create pool0/ggnet/snapshots   # Snapshots
sudo zfs create pool0/ggnet/writebacks  # Writeback layers

# Set ownership
sudo chown -R ggnet:ggnet /pool0/ggnet

# Set permissions
sudo chmod -R 755 /pool0/ggnet

# Verify
zfs list
```

**Expected output:**
```
NAME                      USED  AVAIL     REFER  MOUNTPOINT
pool0                     xxx   xxxTB     xxx    /pool0
pool0/ggnet               xxx   xxxTB     xxx    /pool0/ggnet
pool0/ggnet/images        xxx   xxxTB     xxx    /pool0/ggnet/images
pool0/ggnet/snapshots     xxx   xxxTB     xxx    /pool0/ggnet/snapshots
pool0/ggnet/writebacks    xxx   xxxTB     xxx    /pool0/ggnet/writebacks
```

---

## 🔧 CONFIGURE GGNET TO USE ZFS

Update backend configuration:

```bash
# Edit settings
sudo nano /opt/ggnet/backend/src/config/settings.py

# Ensure IMAGE_ROOT points to ZFS:
IMAGE_ROOT = "/pool0/ggnet/images"
SNAPSHOT_ROOT = "/pool0/ggnet/snapshots"
WRITEBACK_ROOT = "/pool0/ggnet/writebacks"
```

Restart backend:
```bash
sudo systemctl restart ggnet-backend
```

---

## 🎯 VERIFY ZFS INTEGRATION

### **1. Check Storage in UI:**

Visit: `http://192.168.0.137/storage`

You should see:
- Array Type: ZFS
- Array Name: pool0
- Status: ONLINE
- Devices listed

### **2. Test via API:**

```bash
curl http://192.168.0.137/api/v1/storage/array
```

Expected response:
```json
{
  "exists": true,
  "type": "zfs",
  "name": "pool0",
  "status": "ONLINE",
  "capacity_bytes": 8000000000000,
  "used_bytes": 500000000,
  "devices": [
    {"name": "sdb", "status": "ONLINE"},
    {"name": "sdc", "status": "ONLINE"}
  ]
}
```

---

## 🚀 ALTERNATIVE: Use MD RAID Instead

If you prefer **MD RAID** over ZFS:

```bash
# Create RAID 10
sudo mdadm --create /dev/md0 \
  --level=10 \
  --raid-devices=4 \
  /dev/sdb /dev/sdc /dev/sdd /dev/sde

# Format
sudo mkfs.ext4 /dev/md0

# Mount
sudo mkdir -p /mnt/ggnet
sudo mount /dev/md0 /mnt/ggnet

# Create directories
sudo mkdir -p /mnt/ggnet/{images,snapshots,writebacks}
sudo chown -R ggnet:ggnet /mnt/ggnet

# Add to fstab
echo "/dev/md0 /mnt/ggnet ext4 defaults 0 2" | sudo tee -a /etc/fstab

# Update ggNet config
IMAGE_ROOT = "/mnt/ggnet/images"
```

---

## ⚠️ IMPORTANT NOTES

1. **ZFS requires 64-bit system** and at least **2GB RAM** (8GB+ recommended)
2. **Drives will be WIPED** when creating pool - backup data first!
3. **Never mix ZFS and MD RAID** - choose one
4. **Pool name "pool0"** is recommended but can be changed
5. **Mirror requires even number of drives** (2, 4, 6, etc.)

---

## 📞 TROUBLESHOOTING

### **"Cannot find /dev/sdb"**
→ Use `lsblk` to find correct device names

### **"Permission denied"**
→ Run all `zpool` and `zfs` commands with `sudo`

### **"Module zfs not found"**
→ Reboot server after installing ZFS: `sudo reboot`

### **"Pool already exists"**
→ Destroy old pool first: `sudo zpool destroy pool0`

---

**Last Updated:** 2025-10-21  
**Issue:** ZFS not installed on production server  
**Status:** Installation script created ✅

