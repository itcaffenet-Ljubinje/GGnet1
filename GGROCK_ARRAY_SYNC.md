# 🎯 ggRock Array & Settings Synchronization

## 📋 Overview

This document details the synchronization of ggNet's Array (Storage) and Settings pages with ggRock's functionality, based on the official ggRock documentation.

---

## 🔗 **References**

- [ggRock Array Documentation](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860731/Array)
- [Automated Snapshot and Writeback Removal](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860543/Automated+Snapshot+and+Writeback+Removal)
- [ggRock Settings](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860423/Settings)

---

## 📊 **1. ARRAY (Storage Page) - ggRock Compatibility**

### **Array Status Indicator**

Prema [ggRock Array dokumentaciji](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860731/Array):

#### **Status Types:**
- ✅ **Online** - Green LED, array is healthy and operational
- ⚠️ **Degraded** - Amber LED, array is degraded (replace failed drive)
- 🔄 **Rebuilding** - Blue LED, array is rebuilding (do not power off)
- ❌ **Offline** - Red LED, array is offline

#### **Implementation:**
```typescript
interface ArrayStatus {
  health: 'online' | 'offline' | 'degraded' | 'rebuilding';
  type: string; // RAID Type (RAID0, RAID1, RAID10, etc.)
  // ...
}
```

**Visual Indicators:**
- ✅ Green checkmark for "online"
- ⚠️ Yellow warning for "degraded"
- 🔄 Spinning icon for "rebuilding"
- ❌ Red alert for "offline"

---

### **Array Usage Indicator**

#### **Capacity Breakdown:**
```
Total Capacity: 3840 GB
├── Used: 1450 GB (37.8%)
│   ├── System Images: 800 GB
│   ├── Game Images: 450 GB
│   ├── Writebacks: 120 GB
│   └── Snapshots: 80 GB
├── Reserved: 624 GB (16.25%)
└── Free: 1766 GB (46.0%)
```

#### **Visual Bar Chart:**
- **Blue bar** - Used space (includes System Images, Game Images, Writebacks, Snapshots)
- **Yellow bar** - Reserved space (critical for SSD performance)
- **Gray background** - Free space

#### **ggRock Recommendation:**
> **"Reserved disk space" value should be set to at least 15%**, which is the value recommended by the ggRock Team. This is critical because the performance of SSDs decreases the closer they are to being completely full due to having to wait for TRIM/erase operations to occur prior to data being written.

---

### **Drive Information**

#### **Drive Details:**
- **Device** - `/dev/sda`, `/dev/sdb`, etc.
- **Model** - e.g., "Micron 5200 ECO 1.92TB"
- **Serial Number** - Unique identifier
- **Capacity** - e.g., "1920 GB"
- **Status** - online/offline/failed
- **Position** - Position in array (1 of 4, 2 of 4, etc.)

#### **Drive Status Colors:**
- **Green** - Online and healthy
- **Gray** - Offline
- **Red** - Failed

---

### **Drive Management Operations**

#### **Add Drive**
- Click overflow menu (three dots) next to stripe
- Select "Add Drive"
- Choose disk from dropdown
- **Note:** Drive must have capacity larger than largest drive in array

#### **Remove Drive**
- Click overflow menu next to drive
- Select "Remove Drive"
- Confirm removal
- **Note:** RAID0 arrays cannot remove single drives (must delete entire pool)

#### **Replace Drive**
- Click overflow menu next to failed drive
- Select "Replace"
- Choose new drive
- Array will rebuild automatically

#### **Bring Drive Online/Offline**
- Click overflow menu next to drive
- Select "Bring Online" or "Bring Offline"
- Confirm action

---

### **Array Rebuilding**

> **WARNING:** Most operations on a RAID array will require the array to be re-built. During the period of re-building, there will be degraded performance and increased risk of data loss. Please ensure that you do not power off or reboot the server, or otherwise interrupt the array re-build operation at the risk of data loss.

**Visual Indicator:**
- Spinning icon with "Array is rebuilding" message
- Blue color scheme

---

## ⚙️ **2. SETTINGS - Automated Snapshot/Writeback Removal**

### **Array Settings**

Prema [Automated Snapshot and Writeback Removal](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860543/Automated+Snapshot+and+Writeback+Removal):

#### **Reserved Disk Space**
- **Setting:** `reserved_disk_space_percent`
- **Default:** 15%
- **Range:** 10% - 30%
- **Critical:** SSD performance depends on this setting

#### **Warning Threshold**
- **Setting:** `warning_threshold_percent`
- **Default:** 85%
- **Range:** 70% - 95%
- **Purpose:** Alert when disk usage exceeds this value

---

### **Snapshots and Writebacks Retention Settings**

#### **Unutilized Snapshots**
- **Setting:** `unutilized_snapshots_days`
- **Default:** 30 days
- **Range:** 7 - 90 days
- **Description:** How long to retain snapshots that have not been activated (eligible for deletion unless protected)

#### **Unprotected Snapshots**
- **Setting:** `unprotected_snapshots_count`
- **Default:** 5 snapshots
- **Range:** 3 - 20 snapshots
- **Description:** Number of snapshots to keep even if they are eligible for deletion based on age

#### **Inactive Writebacks**
- **Setting:** `inactive_writebacks_hours`
- **Default:** 168 hours (7 days)
- **Range:** 24 - 720 hours (1 day - 30 days)
- **Description:** How long to retain writebacks for powered-off systems (prevents unnecessary writebacks from consuming disk space)

---

### **RAM Settings**

Prema [ggRock Settings](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860423/Settings):

#### **Maximize Size (Recommended)**
- **Default:** Enabled
- **Description:** ggRock manages RAM cache size automatically to maximize performance

#### **Manual RAM Configuration:**
- **RAM Cache Size** - Amount of memory used for high-speed temporary data caching
- **Maximum RAM for VMs** - Amount of memory set aside for ggNet virtual machines
- **Server Reserved** - Amount of memory reserved for OS and critical processes

---

## 📁 **Storage Layout**

### **ggRock Storage Structure:**
```
Array (RAID10 or ZFS Pool)
├── System Images (OS Images)
│   ├── Windows-10-Pro.vhdx
│   ├── Ubuntu-22.04-LTS.vhdx
│   └── ...
├── Game Images
│   ├── Steam-Games.img
│   ├── Epic-Games.img
│   └── ...
├── Writebacks
│   ├── machine-1-writeback
│   ├── machine-2-writeback
│   └── ...
└── Snapshots
    ├── snapshot-2024-10-20
    ├── snapshot-2024-10-19
    └── ...
```

---

## 🎨 **UI Implementation**

### **Storage Page (Array Management)**

#### **Array Status Card:**
```
┌─────────────────────────────────────────┐
│ ✅ Array Status                         │
│ Array is healthy and operational        │
│                                         │
│ RAID Type: RAID10                       │
└─────────────────────────────────────────┘
```

#### **Array Usage Card:**
```
┌─────────────────────────────────────────┐
│ Array Usage                             │
│                                         │
│ Total Capacity: 3840 GB                 │
│ ████████████░░░░░░░░░░░░░░░░░░░░░░░░░  │
│ Used: 1450 GB (37.8%)                   │
│ Reserved: 624 GB (16.25%)               │
│                                         │
│ System Images: 800 GB                   │
│ Game Images: 450 GB                     │
│ Writebacks: 120 GB                      │
│ Snapshots: 80 GB                        │
└─────────────────────────────────────────┘
```

#### **Drives List:**
```
┌─────────────────────────────────────────┐
│ Physical Drives              [+ Add Drive]│
│                                         │
│ ✅ /dev/sda - Micron 5200 ECO 1.92TB   │
│    Serial: S3Z1NX0K123456 • 1920 GB    │
│    Position 1                          │
│                                         │
│ ✅ /dev/sdb - Micron 5200 ECO 1.92TB   │
│    Serial: S3Z1NX0K123457 • 1920 GB    │
│    Position 2                          │
│                                         │
│ ✅ /dev/sdc - Micron 5200 ECO 1.92TB   │
│    Serial: S3Z1NX0K123458 • 1920 GB    │
│    Position 3                          │
│                                         │
│ ✅ /dev/sdd - Micron 5200 ECO 1.92TB   │
│    Serial: S3Z1NX0K123459 • 1920 GB    │
│    Position 4                          │
└─────────────────────────────────────────┘
```

---

### **Settings Page**

#### **RAM Settings:**
```
┌─────────────────────────────────────────┐
│ 🧠 RAM Settings                         │
│                                         │
│ ☑ Maximize size (Recommended)          │
│   ggRock manages RAM automatically     │
└─────────────────────────────────────────┘
```

#### **Array Settings:**
```
┌─────────────────────────────────────────┐
│ 💾 Array and Images                     │
│                                         │
│ Array Settings                          │
│ ─────────────────────────────────────  │
│ Reserved disk space (%): [15]          │
│ Recommended: 15% - Critical for SSD    │
│                                         │
│ Warning threshold (%): [85]            │
│ Disk space warning threshold           │
│                                         │
│ Snapshots and Writebacks Retention     │
│ ─────────────────────────────────────  │
│ Unutilized Snapshots (days): [30]     │
│ How long to retain unused snapshots    │
│                                         │
│ Unprotected Snapshots (count): [5]    │
│ Number of snapshots to keep            │
│                                         │
│ Inactive Writebacks (hours): [168]    │
│ How long to retain powered-off writebks│
└─────────────────────────────────────────┘
```

---

## 🔧 **Backend Implementation (TODO)**

### **Array Status API**
```http
GET /api/v1/storage/array/status

Response:
{
  "exists": true,
  "health": "online",
  "type": "RAID10",
  "devices": [
    {
      "device": "sda",
      "serial": "S3Z1NX0K123456",
      "model": "Micron 5200 ECO 1.92TB",
      "capacity_gb": 1920,
      "status": "online",
      "position": 1
    }
  ],
  "capacity": {
    "total_gb": 3840,
    "used_gb": 1450,
    "available_gb": 1766,
    "reserved_gb": 624,
    "reserved_percent": 16.25
  },
  "breakdown": {
    "system_images_gb": 800,
    "game_images_gb": 450,
    "writebacks_gb": 120,
    "snapshots_gb": 80
  }
}
```

### **Settings API**
```http
GET /api/v1/settings

Response:
{
  "array_settings": {
    "reserved_disk_space_percent": 15,
    "warning_threshold_percent": 85
  },
  "retention_settings": {
    "unutilized_snapshots_days": 30,
    "unprotected_snapshots_count": 5,
    "inactive_writebacks_hours": 168
  },
  "ram_settings": {
    "maximize_size": true,
    "ram_cache_size_mb": 0,
    "max_ram_for_vms_mb": 0,
    "server_reserved_mb": 4096
  }
}
```

---

## ✅ **Implementation Status**

### **Frontend:**
- ✅ Array Status Indicator (Online/Offline/Degraded/Rebuilding)
- ✅ RAID Type Display
- ✅ Array Usage Bar Chart (Used/Reserved/Free)
- ✅ Capacity Breakdown (System Images, Game Images, Writebacks, Snapshots)
- ✅ Drive Information Display
- ✅ Drive Status Colors
- ✅ Drive Details Modal
- ✅ Array Operations (Add/Remove/Replace)
- ✅ RAM Settings (Maximize size checkbox)
- ✅ Array Settings (Reserved space, Warning threshold)
- ✅ Snapshots/Writebacks Retention Settings

### **Backend (TODO):**
- ⏳ Array Status API endpoint
- ⏳ Settings API endpoints
- ⏳ Automated cleanup logic
- ⏳ Drive management operations
- ⏳ Array rebuilding status

---

## 🎯 **Key Takeaways**

### **ggRock Best Practices:**

1. **Reserved Disk Space:** Always set to at least 15% for optimal SSD performance
2. **Automated Cleanup:** Configure retention settings to prevent disk space issues
3. **Array Monitoring:** Regularly check array health and drive status
4. **RAM Management:** Let ggRock manage RAM automatically (recommended)
5. **Warning Thresholds:** Set appropriate warnings to prevent full-disk situations

### **Critical Notes:**

- ⚠️ **DO NOT** power off during array rebuilding
- ⚠️ **DO NOT** let disk usage exceed 85% (performance degradation)
- ⚠️ **DO** configure automated cleanup to prevent space issues
- ⚠️ **DO** monitor drive health regularly
- ⚠️ **DO** replace failed drives immediately

---

## 📚 **References**

- [ggRock Array Documentation](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860731/Array)
- [Automated Snapshot and Writeback Removal](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860543/Automated+Snapshot+and+Writeback+Removal)
- [ggRock Settings](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860423/Settings)

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0  
**Status:** ✅ Frontend Implemented, Backend Pending

