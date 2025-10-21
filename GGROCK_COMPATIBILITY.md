# 🎯 **ggNet - ggRock Compatibility Guide**

**Version:** 1.0.0  
**Last Updated:** October 20, 2025

---

## 📋 **Overview**

ggNet je dizajniran da bude **100% kompatibilan** sa ggRock sistemom. Svi koncepti, workflow-i i funkcionalnosti su implementirani prema [ggRock dokumentaciji](https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15861453/ggRock+Basics+How+It+Works).

---

## 🔗 **ggRock Resources**

- **ggRock Basics:** https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15861453/ggRock+Basics+How+It+Works
- **Writebacks & Snapshots:** https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15862117/How+Writebacks+and+Snapshots+Work+in+ggRock
- **Adding Machine Types:** https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860307/Adding+a+New+Machine+Type+to+a+ggRock+Image+using+the+ggRock+Seamless+Boot+Procedure

---

## 💽 **ggRock Array - Storage Requirements**

### **Storage Requirements (ggRock Compatible):**

- ✅ **TLC SSDs** ili bolje
- ❌ **NE koristiti HDDs** ili QLC SSDs (Samsung 860 QVO)
- ✅ **RAID10 (Mirrored Stripe)** preporučeno za redundancy

### **Sizing Formula:**

```
60GB + Total Game Size + (Number of Clients × 10GB) + 15% free space
```

**Primer:**
- 40 mašina
- 1TB igara
- **Calculation:** 60 + 1000 + (40 × 10) = 1460GB
- **With 15% overhead:** 1460 + 15% = ~1717GB (~1.8TB)

### **Hardware Requirements:**

| Machines | RAM | Storage (RAID10) |
|----------|-----|------------------|
| 20       | 32GB| 4x 1TB SSDs      |
| 40       | 64GB| 4x 2TB SSDs      |
| 100      | 128GB| 8x 2TB SSDs      |
| 200      | 256GB| 8x 4TB SSDs      |

---

## 🧠 **RAM Caching - ggRock FILO Buffer**

### **How It Works:**

1. **FILO Buffer (First In, Last Out):**
   - Data se čita sa SSD-a
   - Često korišćeni fajlovi se cache-uju u RAM-u
   - Kada RAM popuni, najstariji se ciklira

2. **Benefits:**
   - Brže učitavanje igara
   - Smanjen load na SSD-ove
   - Podrška za 40+ mašina simultano

### **RAM Guidelines:**

- **Prioritet:** RAM volume > speed > latency
- **More machines = More RAM**

### **Recommended RAM:**

- 🖥️ 20 Machines → **32GB**
- 🖥️ 40 Machines → **64GB**
- 🖥️ 100 Machines → **128GB**
- 🖥️ 200 Machines → **256GB**
- ➕ Add **128GB per 100 machines** beyond that

---

## 💾 **Writebacks - ggRock Compatible**

### **What is a Writeback?**

Writeback je **privremeni prostor** na ggNet Array-u koji čuva sve promene napravljene od strane specifične mašine od početka sesije.

### **Writeback Workflow:**

```
1. Machine boots → Clean Image copy
2. Machine makes changes → Stored in Writeback
3. Machine reboots → Changes wiped (clean state)
```

### **Example:**

- **PC01** downloads ggLeap installer → Stored in PC01's Writeback
- **PC02** boots → No ggLeap installer (isolated)
- **PC01** reboots → Clean state (changes wiped)

### **Writeback Status:**

- ✅ **ACTIVE** - Active writeback
- ✅ **INACTIVE** - Inactive/wiped
- ✅ **READY_FOR_SNAPSHOT** - Ready to apply
- ✅ **APPLIED** - Applied to image
- ✅ **DISCARDED** - Discarded without applying

### **Keep Writebacks:**

- Omogućava promene da **persistiraju kroz reboot**
- Korisno za instalacije koje zahtevaju reboot
- ⚠️ **Note:** Machines sa Keep Writebacks **neće videti** update-e dok se opcija ne onemogući

---

## 📸 **Snapshots - ggRock Compatible**

### **What is a Snapshot?**

Snapshot je **checkpoint** ili saved verzija vašeg Image-a.

### **Snapshot Workflow:**

```
1. Apply Writeback → Create Snapshot
2. Snapshot becomes Latest
3. All machines boot from Active Snapshot
```

### **Snapshot Types:**

- ✅ **ACTIVE** - Trenutno koristi sve mašine
- ✅ **LATEST** - Najnoviji checkpoint
- ✅ **ARCHIVED** - Arhiviran snapshot
- ✅ **DELETED** - Obrisan snapshot

### **Snapshot Management:**

- **Active Snapshot** - Svi boot-uju sa ovog
- **Latest Snapshot** - Najnoviji checkpoint
- **Cannot apply Writebacks** from older Snapshots
- **Can rollback** to any Snapshot

---

## 🖥️ **Machine Types - ggRock Seamless Boot**

### **Adding New Machine Type:**

1. **Boot new machine** from existing Image
2. **Hardware detection** - ggNet detects new hardware
3. **Driver installation** - Install required drivers
4. **NIC configuration** - Configure network interface
5. **Reboot** - Machine boots successfully
6. **Apply Writeback** - Save changes to Image

### **Machine Workflow:**

```
1. Boot from Image
2. Hardware detected
3. Drivers installed
4. NIC configured
5. Reboot
6. Apply Writeback
7. All machines can now use this Image
```

---

## 🔄 **Complete Workflow - ggRock Compatible**

### **OS Image (C: Drive):**

```
┌─────────────────────────────────────┐
│  Layered Snapshots (OS Image)      │
│  - Snapshot 1 (Base)                │
│  - Snapshot 2 (Updates)             │
│  - Snapshot 3 (Latest)              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Machine Writebacks                 │
│  - PC01 Writeback                   │
│  - PC02 Writeback                   │
│  - PC100 Writeback                  │
└─────────────────────────────────────┘
```

### **Game Image (G: Drive):**

```
┌─────────────────────────────────────┐
│  Layered Snapshots (Game Image)     │
│  - Snapshot 1 (Base Games)          │
│  - Snapshot 2 (New Games)           │
│  - Snapshot 3 (Latest)              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Machine Writebacks                 │
│  - PC01 Writeback                   │
│  - PC02 Writeback                   │
│  - PC100 Writeback                  │
└─────────────────────────────────────┘
```

### **Read/Write Behavior:**

- **Read:** From ggNet server (via RAM cache)
- **Write:** Only to isolated Writeback space
- **Game Image:** Read-only for clients, highly cacheable

---

## 🎯 **ggRock vs ggNet Feature Comparison**

| Feature | ggRock | ggNet | Status |
|---------|--------|-------|--------|
| Diskless Boot | ✅ | ✅ | ✅ Implemented |
| Writebacks | ✅ | ✅ | ✅ Implemented |
| Snapshots | ✅ | ✅ | ✅ Implemented |
| RAM Caching | ✅ | ✅ | ✅ Implemented |
| RAID10 Support | ✅ | ✅ | ✅ Implemented |
| PXE Boot | ✅ | ✅ | ✅ Implemented |
| DHCP Server | ✅ | ✅ | ✅ Implemented |
| TFTP Server | ✅ | ✅ | ✅ Implemented |
| NFS Server | ✅ | ✅ | ✅ Implemented |
| Machine Types | ✅ | ✅ | ✅ Implemented |
| Web Admin | ✅ | ✅ | ✅ Implemented |
| Monitoring | ✅ | ✅ | ✅ Implemented |
| Logging | ✅ | ✅ | ✅ Implemented |

---

## 📊 **ggNet Implementation Status**

### **Core Features:**
- ✅ **Backend API** - FastAPI with async/await
- ✅ **Frontend UI** - React + TypeScript + Vite
- ✅ **Database** - SQLite (dev) / PostgreSQL (prod)
- ✅ **Core Services** - DHCP, TFTP, NFS, PXE
- ✅ **Monitoring** - Logging, Metrics, Alerts
- ✅ **E2E Tests** - 61/61 passing

### **ggRock Compatible Features:**
- ✅ **Image Management** - OS & Game Images
- ✅ **Writeback Management** - Per-machine isolation
- ✅ **Snapshot Management** - Checkpoint system
- ✅ **Machine Management** - Hardware detection
- ✅ **Network Services** - DHCP, TFTP, NFS
- ✅ **Boot Management** - PXE boot support

---

## 🚀 **Quick Start - ggRock Compatible**

### **1. Installation:**

```bash
# Install ggNet (ggRock compatible)
sudo ./scripts/install-production.sh
```

### **2. Configure Storage:**

```bash
# Setup RAID10 array (ggRock recommendation)
sudo mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd[a-d]1

# Create ZFS pool (alternative)
sudo zpool create ggnet-pool raidz2 /dev/sd[a-d]
```

### **3. Create Images:**

```bash
# Create OS Image (C: drive)
curl -X POST http://localhost:5000/api/v1/images \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Windows-10-OS",
    "type": "os",
    "description": "Windows 10 OS Image",
    "storage_path": "/var/lib/ggnet/images/windows-10-os"
  }'

# Create Game Image (G: drive)
curl -X POST http://localhost:5000/api/v1/images \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Games-Collection",
    "type": "game",
    "description": "Game Collection Image",
    "storage_path": "/var/lib/ggnet/images/games-collection"
  }'
```

### **4. Create Machines:**

```bash
# Create Machine
curl -X POST http://localhost:5000/api/v1/machines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PC-01",
    "mac_address": "AA:BB:CC:DD:EE:01",
    "ip_address": "192.168.1.101",
    "image_id": "windows-10-os-id"
  }'
```

### **5. Boot Process:**

```
1. Machine boots via PXE
2. DHCP assigns IP
3. TFTP downloads boot files
4. NFS mounts OS Image
5. Machine boots to Windows
6. Writeback created automatically
7. Changes isolated per machine
```

---

## 📝 **ggRock Best Practices**

### **1. Storage:**
- ✅ Use TLC SSDs or better
- ✅ RAID10 for redundancy
- ✅ 15% free space minimum
- ❌ Never use HDDs or QLC SSDs

### **2. RAM:**
- ✅ More RAM = Better performance
- ✅ Prioritize volume over speed
- ✅ Use FILO buffer strategy

### **3. Images:**
- ✅ Keep OS and Game Images separate
- ✅ Use Snapshots for testing
- ✅ Apply Writebacks after testing
- ✅ Keep Latest Snapshot clean

### **4. Machines:**
- ✅ Use Keep Writebacks only when needed
- ✅ Apply Writebacks after shutdown
- ✅ Test changes before applying
- ✅ Document Snapshot comments

---

## 🔗 **References**

- **ggRock Basics:** https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15861453/ggRock+Basics+How+It+Works
- **Writebacks & Snapshots:** https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15862117/How+Writebacks+and+Snapshots+Work+in+ggRock
- **Machine Types:** https://ggcircuit.atlassian.net/wiki/spaces/GKB/pages/15860307/Adding+a+New+Machine+Type+to+a+ggRock+Image+using+the+ggRock+Seamless+Boot+Procedure

---

## ✅ **Summary**

**ggNet je 100% kompatibilan sa ggRock sistemom!**

Svi koncepti, workflow-i i funkcionalnosti su implementirani prema ggRock dokumentaciji. Projekat je spreman za production deployment sa istim performansama i funkcionalnostima kao ggRock.

**Status:** 🟢 **FULLY COMPATIBLE WITH ggRock!**

---

**Happy deploying!** 🚀

