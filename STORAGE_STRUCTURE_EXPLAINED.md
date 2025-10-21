# 💾 Storage Structure - Complete Explanation

## 📋 Overview

**DA!** System i games images, snapshots i writebacks se **smestaju u ZFS pool ili RAID array**.

---

## 🎯 **Storage Architecture**

### **1. Storage Location**

Sve se smešta u **jedan centralizovan storage pool**:

```
/srv/ggnet/array/
├── images/          # System i Game Images
│   ├── system/      # Windows, Linux OS images
│   └── games/       # Game images
├── writebacks/      # Client write storage
│   ├── machine-001/ # Per-machine writebacks
│   ├── machine-002/
│   └── ...
└── snapshots/       # Image snapshots
    ├── image-001-v1/
    ├── image-001-v2/
    └── ...
```

---

## 🔧 **Storage Options**

### **Option 1: ZFS Pool (Recommended)**

**Benefits:**
- ✅ **Native Snapshots** - ZFS snapshots su instant i efikasni
- ✅ **Copy-on-Write** - Automatski COW za sve operacije
- ✅ **Compression** - Automatska kompresija
- ✅ **Data Integrity** - Checksums za sve blokove
- ✅ **Deduplication** - Automatska deduplikacija
- ✅ **Easy Management** - Jednostavno upravljanje

**Setup:**
```bash
# Create ZFS pool (RAID10 equivalent)
zpool create pool0 mirror /dev/sda /dev/sdb mirror /dev/sdc /dev/sdd

# Create ggnet dataset
zfs create pool0/ggnet

# Set mountpoint
zfs set mountpoint=/srv/ggnet/array pool0/ggnet

# Enable compression
zfs set compression=lz4 pool0/ggnet

# Enable deduplication (optional, requires RAM)
zfs set dedup=on pool0/ggnet
```

**ZFS Structure:**
```
pool0/
└── ggnet/
    ├── images/          # ZFS dataset
    │   ├── system/      # System images
    │   └── games/       # Game images
    ├── writebacks/      # ZFS dataset
    │   └── machine-*/   # Per-machine writebacks
    └── snapshots/       # ZFS snapshots
        └── image-*/     # Image snapshots
```

---

### **Option 2: MD RAID (RAID10)**

**Benefits:**
- ✅ **Hardware Independent** - Radi na bilo kom hardware-u
- ✅ **Proven Technology** - Stabilna i pouzdana
- ✅ **Good Performance** - Brza čitanja i pisanja
- ✅ **Easy to Understand** - Jednostavna konfiguracija

**Setup:**
```bash
# Create RAID10 array
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sda /dev/sdb /dev/sdc /dev/sdd

# Format with ext4 or XFS
mkfs.ext4 /dev/md0

# Mount
mkdir -p /srv/ggnet/array
mount /dev/md0 /srv/ggnet/array

# Add to fstab
echo '/dev/md0 /srv/ggnet/array ext4 defaults 0 2' >> /etc/fstab

# Create directories
mkdir -p /srv/ggnet/array/{images/{system,games},writebacks,snapshots}
```

**RAID10 Structure:**
```
/dev/md0 (RAID10)
└── /srv/ggnet/array/
    ├── images/
    │   ├── system/
    │   └── games/
    ├── writebacks/
    └── snapshots/
```

---

### **Option 3: LVM (Logical Volume Manager)**

**Benefits:**
- ✅ **Flexibility** - Lako proširivanje
- ✅ **Volume Management** - Jednostavno upravljanje
- ✅ **Snapshots** - LVM snapshots za backup

**Setup:**
```bash
# Create physical volumes
pvcreate /dev/sda /dev/sdb /dev/sdc /dev/sdd

# Create volume group
vgcreate vg0 /dev/sda /dev/sdb /dev/sdc /dev/sdd

# Create logical volume
lvcreate -l 100%FREE -n ggnet vg0

# Format
mkfs.ext4 /dev/vg0/ggnet

# Mount
mkdir -p /srv/ggnet/array
mount /dev/vg0/ggnet /srv/ggnet/array
```

---

## 📊 **Storage Breakdown**

### **What Gets Stored Where:**

| Type | Location | Description | Size |
|------|----------|-------------|------|
| **System Images** | `/srv/ggnet/array/images/system/` | Windows, Linux OS images | ~60 GB each |
| **Game Images** | `/srv/ggnet/array/images/games/` | Game installations | ~50-200 GB each |
| **Writebacks** | `/srv/ggnet/array/writebacks/machine-*/` | Per-client write storage | ~10 GB per client |
| **Snapshots** | `/srv/ggnet/array/snapshots/` | Image snapshots | Varies |

---

## 🎯 **Storage Formula**

**From ggRock Documentation:**

```
Required Space = 60GB + Total Games Size + (Number of Clients × 10GB) + 15%
```

**Example:**
- 50 clients
- 500 GB games
- Calculation: 60 + 500 + (50 × 10) + 15% = **1.22 TB**

**Breakdown:**
- System Images: 60 GB
- Game Images: 500 GB
- Writebacks: 500 GB (50 clients × 10 GB)
- Reserved Space: 15% (critical for SSD performance)
- **Total Required: 1.22 TB**

---

## 🔄 **How ggNet Uses Storage**

### **1. System Images**

```bash
/srv/ggnet/array/images/system/
├── windows-10-v1.img       # Windows 10 image
├── windows-11-v1.img       # Windows 11 image
├── ubuntu-22.04-v1.img     # Ubuntu 22.04 image
└── debian-12-v1.img        # Debian 12 image
```

**Characteristics:**
- ✅ **Read-only** - Clients mount kao read-only
- ✅ **Shared** - Svi klijenti dele isti image
- ✅ **Immutable** - Ne menja se tokom rada
- ✅ **Cached** - Kešira se u RAM-u za brz pristup

---

### **2. Game Images**

```bash
/srv/ggnet/array/images/games/
├── steam-games-v1.img      # Steam games collection
├── epic-games-v1.img       # Epic Games collection
├── riot-games-v1.img       # Riot Games collection
└── blizzard-games-v1.img   # Blizzard games collection
```

**Characteristics:**
- ✅ **Read-only** - Clients mount kao read-only
- ✅ **Shared** - Svi klijenti dele isti image
- ✅ **Large** - 50-200 GB po image-u
- ✅ **Cached** - Kešira se u RAM-u

---

### **3. Writebacks**

```bash
/srv/ggnet/array/writebacks/
├── machine-001/            # Client 1 writeback
│   ├── user-data/          # User files
│   ├── temp/               # Temporary files
│   └── logs/               # System logs
├── machine-002/            # Client 2 writeback
└── machine-003/            # Client 3 writeback
```

**Characteristics:**
- ✅ **Read-write** - Clients mogu da pišu
- ✅ **Per-client** - Svaki klijent ima svoj writeback
- ✅ **Differential** - Samo promene se čuvaju
- ✅ **Default 10GB** - Konfigurabilno

---

### **4. Snapshots**

#### **A. Image Snapshots (ZFS)**

```bash
# ZFS snapshots
pool0/ggnet/images/system@windows-10-v1
pool0/ggnet/images/system@windows-10-v2
pool0/ggnet/images/games@steam-games-v1
pool0/ggnet/images/games@steam-games-v2
```

**Characteristics:**
- ✅ **Instant** - Kreira se trenutno
- ✅ **Space-efficient** - Koristi COW
- ✅ **Immutable** - Ne može se menjati
- ✅ **Versioning** - Kreira verzije image-a

#### **B. Writeback Snapshots**

```bash
/srv/ggnet/array/snapshots/
├── machine-001-2024-01-15/  # Snapshot of machine 1 writeback
├── machine-002-2024-01-15/  # Snapshot of machine 2 writeback
└── image-001-v2/            # Snapshot of image 1
```

**Characteristics:**
- ✅ **Point-in-time** - Trenutno stanje
- ✅ **Backup** - Backup writeback-a
- ✅ **Recovery** - Mogućnost vraćanja

---

## 🚀 **Storage Operations**

### **1. Image Operations**

```bash
# Upload image
POST /api/v1/images/upload
{
  "name": "windows-10-v1",
  "type": "system",
  "file": "windows-10.img"
}

# Stored at: /srv/ggnet/array/images/system/windows-10-v1.img
```

### **2. Writeback Operations**

```bash
# Create writeback for machine
POST /api/v1/machines/{machine_id}/writeback
{
  "size_gb": 10
}

# Stored at: /srv/ggnet/array/writebacks/machine-001/
```

### **3. Snapshot Operations**

```bash
# Create snapshot
POST /api/v1/images/{image_id}/snapshot
{
  "name": "windows-10-v2",
  "comment": "Updated drivers"
}

# ZFS snapshot: pool0/ggnet/images/system@windows-10-v2
# Or file copy: /srv/ggnet/array/snapshots/windows-10-v2/
```

---

## 🎨 **ggNet Storage Manager**

**File:** `backend/src/core/storage_manager.py`

**Features:**
- ✅ **Automatic Detection** - Detektuje ZFS, MD RAID, LVM
- ✅ **Capacity Calculation** - Računa total, used, available
- ✅ **Storage Breakdown** - System images, games, writebacks, snapshots
- ✅ **Drive Operations** - Add, remove, replace drives

**How It Works:**
```python
# Get storage manager
storage_manager = get_storage_manager()

# Get array status
status = storage_manager.get_array_status()

# Status includes:
# - Array health (online/offline/degraded/rebuilding)
# - Array type (RAID10, ZFS, LVM)
# - Drive information
# - Capacity breakdown
# - Storage breakdown (system images, games, writebacks, snapshots)
```

---

## 🔐 **Storage Security**

### **1. Permissions**

```bash
# Set ownership
chown -R ggnet:ggnet /srv/ggnet/array

# Set permissions
chmod 755 /srv/ggnet/array
chmod 644 /srv/ggnet/array/images/*/.*
chmod 755 /srv/ggnet/array/writebacks/*
chmod 755 /srv/ggnet/array/snapshots/*
```

### **2. Quotas**

**ZFS Quotas:**
```bash
# Set quota for writebacks
zfs set quota=10G pool0/ggnet/writebacks/machine-001

# Set quota for images
zfs set quota=100G pool0/ggnet/images/system
```

**LVM Quotas:**
```bash
# Enable quotas
mount -o remount,usrquota /srv/ggnet/array
quotacheck -avug
quotaon -avug

# Set quota for user
setquota -u ggnet 10000 20000 0 0 /srv/ggnet/array
```

---

## 📊 **Storage Monitoring**

### **1. Capacity Monitoring**

```bash
# ZFS
zpool list
zfs list -r pool0/ggnet

# MD RAID
mdadm --detail /dev/md0
df -h /srv/ggnet/array

# LVM
vgs
lvs
df -h /srv/ggnet/array
```

### **2. Usage Breakdown**

**Web UI Shows:**
- System Images: 800 GB
- Game Images: 450 GB
- Writebacks: 120 GB
- Snapshots: 80 GB
- **Total Used: 1450 GB**
- Reserved: 624 GB (15%)
- **Available: 1766 GB**

---

## ✅ **Summary**

**DA! Sve se smešta u ZFS pool ili RAID array:**

1. ✅ **System Images** → `/srv/ggnet/array/images/system/`
2. ✅ **Game Images** → `/srv/ggnet/array/images/games/`
3. ✅ **Writebacks** → `/srv/ggnet/array/writebacks/machine-*/`
4. ✅ **Snapshots** → `/srv/ggnet/array/snapshots/` (ili ZFS snapshots)

**Storage Options:**
- ✅ **ZFS Pool** (Recommended) - Native snapshots, COW, compression
- ✅ **MD RAID** (RAID10) - Hardware independent, proven
- ✅ **LVM** - Flexible, easy to extend

**Benefits:**
- ✅ **Centralized Storage** - Sve na jednom mestu
- ✅ **Shared Images** - Svi klijenti dele isti image
- ✅ **Per-Client Writebacks** - Svaki klijent ima svoj writeback
- ✅ **Snapshot Support** - Point-in-time backups
- ✅ **High Performance** - RAM caching + SSD storage

---

**Storage Structure je potpuno objašnjena! 💾✨**

---

**Last Updated:** October 20, 2025  
**Version:** 2.0.0  
**Status:** ✅ Complete Explanation

