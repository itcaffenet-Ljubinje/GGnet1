# 🐧 REAL HARDWARE TESTING GUIDE

**ggNet Backend - Linux Server Deployment & Testing**

---

## ⚠️ **VAŽNO - PROČITAJ PRE POKRETANJA!**

Ovo je guide za testiranje na **PRAVOM HARDWARE-u** sa **PRAVIM DISKOVIMA**.

**OPASNOST:**
- ❌ **NE POKREĆI NA PRODUCTION SISTEMU**
- ❌ **NE KORISTI DISKOVE SA VAŽNIM PODACIMA**
- ❌ **SVE OPERACIJE SU DESTRUKTIVNE**
- ✅ **KORISTI SAMO TEST SERVER SA TEST DISKOVIMA**

---

## 📋 **PREDUSLOV - HARDVER:**

### **Minimalni zahtevi:**
- 🖥️ **Server:** Debian 11/12 ili Ubuntu 20.04/22.04 LTS
- 💾 **Diskovi:** Minimum 2 nekorišćena diska (za RAID testing)
- 🔌 **RAM:** Minimum 4GB
- 💻 **CPU:** 2+ cores
- 🌐 **Network:** 1Gbps+ Ethernet

### **Preporučeni zahtevi:**
- 🖥️ **Server:** Dedicated bare metal server
- 💾 **Diskovi:** 4-10 identičnih diskova (1.8TB+ SSD)
- 🔌 **RAM:** 8GB+
- 💻 **CPU:** 4+ cores
- 🌐 **Network:** 10Gbps Ethernet

### **Test Environment:**
Idealno za testiranje:
```
Server: Dell PowerEdge R740
CPU: Intel Xeon Silver 4214
RAM: 32GB ECC
Disks: 8x 1.92TB Samsung SSD (sda-sdh)
Network: Dual 10GbE
OS: Ubuntu 22.04 LTS Server
```

---

## 🚀 **STEP-BY-STEP DEPLOYMENT:**

### **KORAK 1: Pripremi Server** 🖥️

```bash
# 1. Fresh install Ubuntu/Debian Server
# 2. SSH na server
ssh root@your-server-ip

# 3. Update sistema
apt-get update && apt-get upgrade -y

# 4. Preuzmi kod
cd /tmp
git clone https://github.com/your-repo/ggnet.git
cd ggnet/backend
```

---

### **KORAK 2: Pokreni Setup Script** 📦

```bash
# Kao root:
sudo bash scripts/setup_linux_server.sh
```

**Šta ovaj script radi:**
- ✅ Instalira sve potrebne pakete (Python, PostgreSQL, ZFS, MD RAID)
- ✅ Kreira ggnet usera
- ✅ Pravi direktorijume (`/srv/ggnet`)
- ✅ Konfiguruje network services (DHCP, TFTP, NFS)
- ✅ Instalira monitoring tools (Prometheus)
- ✅ Kreira systemd service

**Trajanje:** ~5-10 minuta

---

### **KORAK 3: Setup Backend Aplikaciju** 🐍

```bash
# Kopiraj backend kod u /srv/ggnet/backend
sudo cp -r backend/* /srv/ggnet/backend/

# Promeni u ggnet user
sudo su - ggnet

# Pokreni setup
cd /srv/ggnet/backend
bash scripts/setup_backend.sh
```

**Šta ovaj script radi:**
- ✅ Kreira Python virtual environment
- ✅ Instalira dependencies
- ✅ Konfiguriše .env fajl
- ✅ Setup bazu (PostgreSQL)
- ✅ Pokreće migracije
- ✅ Pokreće testove

**Trajanje:** ~3-5 minuta

---

### **KORAK 4: Pripremi Test Diskove** 💾

```bash
# Vrati se na root
exit

# Proveri dostupne diskove
lsblk

# OČEKIVANI OUTPUT:
# NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
# sda      8:0    0   1.8T  0 disk           <- OS disk
# sdb      8:16   0   1.8T  0 disk           <- Test disk 1
# sdc      8:32   0   1.8T  0 disk           <- Test disk 2
# sdd      8:48   0   1.8T  0 disk           <- Test disk 3
# sde      8:64   0   1.8T  0 disk           <- Test disk 4

# ⚠️ PROVERI DA DISKOVI NISU MOUNTOVANI!
mount | grep -E 'sd[b-h]'

# ⚠️ Ako je neki disk mountovan, odmountuj:
# umount /dev/sdb1

# ⚠️ UKLONI SVE PARTICIJE (OPASNO!)
# wipefs -a /dev/sdb
# wipefs -a /dev/sdc
# wipefs -a /dev/sdd
# wipefs -a /dev/sde
```

---

### **KORAK 5: Pokreni Safe Detection Tests** 🔍

```bash
# Kao root ili sa sudo
cd /srv/ggnet/backend

# Activate venv
source venv/bin/activate

# Run safe (read-only) tests
pytest tests/test_real_hardware.py::TestRealHardwareDetection -v
pytest tests/test_real_hardware.py::TestRealHardwareReadOnly -v
```

**Očekivani output:**
```
✓ Array Type Detected: zfs (or mdraid, or unknown)
✓ Array Name: pool0 (or /dev/md0, or None)
✓ ZFS commands available
✓ Available Drives: 4
  sdb: Samsung SSD (1.8T) - Serial: TEST123
  sdc: Samsung SSD (1.8T) - Serial: TEST456
  sdd: Samsung SSD (1.8T) - Serial: TEST789
  sde: Samsung SSD (1.8T) - Serial: TEST012
```

---

### **KORAK 6: Kreiraj Test ZFS Pool** 🛠️

```bash
# ⚠️ DESTRUKTIVNO! Sve podatke na /dev/sdb i /dev/sdc će biti IZBRISANI!

# Kreiraj ZFS mirror pool (RAID1)
zpool create pool0 mirror /dev/sdb /dev/sdc

# Proveri status
zpool status pool0

# Očekivani output:
#   pool: pool0
#  state: ONLINE
# config:
#     NAME        STATE     READ WRITE CKSUM
#     pool0       ONLINE       0     0     0
#       mirror-0  ONLINE       0     0     0
#         sdb     ONLINE       0     0     0
#         sdc     ONLINE       0     0     0

# Proveri kapacitet
zpool list pool0

# Kreiraj direktorijume za ggNet
zfs create pool0/images
zfs create pool0/writebacks
zfs create pool0/snapshots

# Set mountpoints
zfs set mountpoint=/srv/ggnet/array/images pool0/images
zfs set mountpoint=/srv/ggnet/array/writebacks pool0/writebacks
zfs set mountpoint=/srv/ggnet/array/snapshots pool0/snapshots

# Proveri
df -h | grep pool0
```

---

### **KORAK 7: Test Storage Manager sa Real Hardware** ✅

```bash
# Kao ggnet user
sudo su - ggnet
cd /srv/ggnet/backend
source venv/bin/activate

# Pokreni detection tests
pytest tests/test_real_hardware.py::TestRealHardwareDetection -v -s

# Očekivani output:
# ✓ Array Type Detected: zfs
# ✓ Array Name: pool0
# ✓ Array Exists: True
# ✓ Health: online
# ✓ Type: ZFS
# ✓ Devices: 2
# ✓ Total Capacity: 3600 GB
# ✓ Used: 0 GB
# ✓ Available: 3600 GB
#   Device 0: sdb - Samsung SSD (1800GB) - online
#   Device 1: sdc - Samsung SSD (1800GB) - online
```

---

### **KORAK 8: Test API Endpoints** 🌐

```bash
# Start backend
cd /srv/ggnet/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait for startup
sleep 5

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/storage/array/status | jq

# Očekivani output:
# {
#   "exists": true,
#   "health": "online",
#   "type": "ZFS",
#   "devices": [
#     {
#       "device": "sdb",
#       "serial": "...",
#       "model": "Samsung SSD",
#       "capacity_gb": 1800,
#       "status": "online",
#       "position": 0
#     },
#     ...
#   ],
#   "capacity": {
#     "total_gb": 3600,
#     "used_gb": 0,
#     "available_gb": 3600,
#     ...
#   }
# }

# Test available drives
curl http://localhost:8000/api/v1/storage/array/available-drives | jq

# Očekivani output:
# [
#   {
#     "device": "sdd",
#     "size": "1.8T",
#     "model": "Samsung SSD",
#     "serial": "...",
#     "capacity_gb": 1800
#   },
#   {
#     "device": "sde",
#     "size": "1.8T",
#     "model": "Samsung SSD",
#     "serial": "...",
#     "capacity_gb": 1800
#   }
# ]
```

---

### **KORAK 9: Test Add Stripe Operation** ➕

```bash
# ⚠️ DESTRUKTIVNO! Briše podatke na /dev/sdd i /dev/sde!

# Add new stripe (mirror)
curl -X POST http://localhost:8000/api/v1/storage/array/stripes \
  -H "Content-Type: application/json" \
  -d '{
    "stripe_number": 1,
    "raid_type": "mirror",
    "devices": ["sdd", "sde"]
  }' | jq

# Očekivani output:
# {
#   "success": true,
#   "message": "Stripe 1 added successfully"
# }

# Proveri da li je pool kreiran
zpool list

# Očekivani output:
# NAME    SIZE  ALLOC   FREE
# pool0  3.62T    96K  3.62T
# pool1  3.62T    96K  3.62T  <- Novi pool!

# Proveri status
zpool status pool1
```

---

### **KORAK 10: Test Drive Operations** 🔧

```bash
# Test bring drive offline
curl -X POST http://localhost:8000/api/v1/storage/array/drives/sdb/offline | jq

# Proveri
zpool status pool0
# sdb bi trebalo da bude OFFLINE

# Test bring drive online
curl -X POST http://localhost:8000/api/v1/storage/array/drives/sdb/online | jq

# Proveri
zpool status pool0
# sdb bi trebalo da bude ONLINE

# Test replace drive (simulacija)
# ⚠️ Ovo je primer - prilagodi prema dostupnim diskovima
# curl -X POST http://localhost:8000/api/v1/storage/array/drives/replace \
#   -H "Content-Type: application/json" \
#   -d '{"old_device": "sdb", "new_device": "sdf"}' | jq
```

---

### **KORAK 11: Test MD RAID Operations** 🔄

```bash
# Prvo destroy ZFS pool za test
zpool destroy pool0
zpool destroy pool1

# Kreiraj MD RAID10 array
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{b,c,d,e}

# Proveri status
cat /proc/mdstat

# Test sa ggNet API
curl http://localhost:8000/api/v1/storage/array/status | jq

# Očekivani output:
# {
#   "exists": true,
#   "health": "online",
#   "type": "RAID10",
#   "devices": [...]
# }
```

---

### **KORAK 12: Performance Testing** 📊

```bash
# Test write performance
dd if=/dev/zero of=/srv/ggnet/array/images/test.img bs=1M count=10000 oflag=direct

# Test read performance
dd if=/srv/ggnet/array/images/test.img of=/dev/null bs=1M count=10000 iflag=direct

# ZFS specific tests
zpool iostat pool0 1

# Očekivane performanse:
# Write: 500-1000 MB/s (RAID1/10 sa SSD)
# Read:  1000-2000 MB/s (RAID1/10 sa SSD)
```

---

### **KORAK 13: Cleanup After Testing** 🧹

```bash
# Stop backend
pkill -f uvicorn

# Destroy test pools/arrays
zpool destroy pool0 2>/dev/null || true
zpool destroy pool1 2>/dev/null || true
mdadm --stop /dev/md0 2>/dev/null || true

# Wipe test disks
wipefs -a /dev/sdb
wipefs -a /dev/sdc
wipefs -a /dev/sdd
wipefs -a /dev/sde

# Remove test data
rm -rf /srv/ggnet/array/*
```

---

## 🧪 **PYTEST SA REAL HARDWARE:**

### **Safe Tests (Read-Only):**

```bash
cd /srv/ggnet/backend
source venv/bin/activate

# Detection tests (safe)
pytest tests/test_real_hardware.py::TestRealHardwareDetection -v -s

# Command availability tests (safe)
pytest tests/test_real_hardware.py::TestRealHardwareReadOnly -v -s
```

### **Destructive Tests (⚠️ DANGEROUS!):**

```bash
# Set safety environment variables
export GGNET_ALLOW_DESTRUCTIVE_TESTS=yes
export GGNET_TEST_DEVICES=sdb,sdc,sdd,sde

# ⚠️ DOUBLE CHECK DEVICE NAMES!
lsblk

# Run destructive tests (as root)
sudo -E pytest tests/test_real_hardware.py::TestRealHardwareOperations -v -s
```

---

## 📊 **EXPECTED TEST RESULTS:**

### **Detection Tests:**
```
tests/test_real_hardware.py::TestRealHardwareDetection::test_storage_manager_initialization PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_detect_array_type PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_get_array_status PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_get_available_drives PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_singleton_pattern PASSED

======================== 5 passed in 2.34s ========================
```

### **Read-Only Tests:**
```
tests/test_real_hardware.py::TestRealHardwareReadOnly::test_zfs_command_available PASSED
tests/test_real_hardware.py::TestRealHardwareReadOnly::test_mdraid_command_available PASSED
tests/test_real_hardware.py::TestRealHardwareReadOnly::test_lvm_command_available PASSED
tests/test_real_hardware.py::TestRealHardwareReadOnly::test_smart_monitoring_available PASSED

======================== 4 passed in 1.12s ========================
```

---

## 🔐 **SAFETY CHECKLIST:**

Pre nego što pokreneš testove sa pravim hardware-om:

- [ ] ✅ Koristiš dedicated test server (NE production!)
- [ ] ✅ Diskovi su prazni i nekorišćeni
- [ ] ✅ Napravio si backup svih važnih podataka
- [ ] ✅ Proverio si device names (`lsblk`)
- [ ] ✅ Diskovi NISU mountovani (`mount | grep sd`)
- [ ] ✅ Testiraš prvo sa ZFS (non-destructive za ostale diskove)
- [ ] ✅ Imaš pristup serveru (SSH + console access)
- [ ] ✅ Razumeš da sve može da se pobriše
- [ ] ✅ Spreman si da reinstaliraš OS ako nešto krene naopako

---

## 🛡️ **SAFETY FEATURES U KODU:**

Kod ima built-in safety features:

### **1. Validation:**
```python
# Stripe number mora biti 0-10
if stripe_number < 0 or stripe_number > 10:
    raise HTTPException(400, "Invalid stripe number")

# Device names moraju biti validni
if not device.startswith('sd'):
    raise HTTPException(400, "Invalid device name")

# Mora biti bar jedan device
if len(devices) == 0:
    raise HTTPException(400, "At least one device required")
```

### **2. Dry-Run Mode:**
Dodaćemo dry-run mode za testiranje bez izvršavanja:
```python
# In storage_manager.py
DRY_RUN = os.environ.get('GGNET_DRY_RUN', 'false').lower() == 'true'

if DRY_RUN:
    logger.info(f"DRY RUN: Would execute: {cmd}")
    return True
else:
    subprocess.run(cmd, check=True)
```

---

## 📝 **TEST SCENARIOS:**

### **Scenario 1: ZFS Mirror (RAID1)**
```bash
# 2 diska, mirror
zpool create pool0 mirror /dev/sdb /dev/sdc

# Test:
curl http://localhost:8000/api/v1/storage/array/status | jq

# Expected:
# - exists: true
# - type: "ZFS"
# - devices: 2
# - health: "online"
```

### **Scenario 2: ZFS RAIDZ2**
```bash
# 6 diskova, raidz2 (double parity)
zpool create pool0 raidz2 /dev/sd{b,c,d,e,f,g}

# Test:
curl http://localhost:8000/api/v1/storage/array/status | jq

# Expected:
# - devices: 6
# - type: "ZFS"
# - Fault tolerance: 2 disks
```

### **Scenario 3: MD RAID10**
```bash
# 4 diska, RAID10
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd{b,c,d,e}

# Test:
curl http://localhost:8000/api/v1/storage/array/status | jq

# Expected:
# - type: "RAID10"
# - devices: 4
```

### **Scenario 4: Add Stripe via API**
```bash
# Add new stripe
curl -X POST http://localhost:8000/api/v1/storage/array/stripes \
  -H "Content-Type: application/json" \
  -d '{
    "stripe_number": 1,
    "raid_type": "mirror",
    "devices": ["sdd", "sde"]
  }' | jq

# Verify
zpool list
zpool status pool1
```

---

## 🐛 **TROUBLESHOOTING:**

### **Problem 1: ZFS module not loaded**
```bash
# Solution:
modprobe zfs
systemctl restart zfs-import-cache
systemctl restart zfs-mount
```

### **Problem 2: Permission denied**
```bash
# Solution:
sudo usermod -aG disk ggnet
# Logout and login again
```

### **Problem 3: Device busy**
```bash
# Check what's using it:
lsof /dev/sdb
fuser -v /dev/sdb

# Force umount:
umount -f /dev/sdb

# Clear metadata:
wipefs -a /dev/sdb
```

### **Problem 4: Pool import issues**
```bash
# Force import:
zpool import -f pool0

# Import all pools:
zpool import -a
```

---

## 📊 **MONITORING REAL HARDWARE:**

```bash
# ZFS monitoring
watch -n 1 'zpool iostat pool0 1 1'

# MD RAID monitoring
watch -n 1 'cat /proc/mdstat'

# Disk health
smartctl -a /dev/sdb

# Performance
iostat -x 1

# Resource usage
htop
```

---

## ✅ **VERIFICATION CHECKLIST:**

Po završetku testiranja, proveri:

- [ ] ✅ Array je detektovan (`exists: true`)
- [ ] ✅ Health je `online`
- [ ] ✅ Svi diskovi su `ONLINE`
- [ ] ✅ Kapacitet je tačan
- [ ] ✅ API vraća validne podatke
- [ ] ✅ Operacije (add/remove/replace) rade
- [ ] ✅ SMART status je dobar
- [ ] ✅ Performanse su dobre (500+ MB/s write)
- [ ] ✅ Nema error-a u logovima
- [ ] ✅ Frontend može da se konektuje

---

## 📚 **DODATNI RESURSI:**

### **ZFS:**
- https://openzfs.github.io/openzfs-docs/
- `man zpool`
- `man zfs`

### **MD RAID:**
- https://raid.wiki.kernel.org/
- `man mdadm`

### **ggNet:**
- `TESTING_COMPLETE_SUMMARY.md` - Unit tests
- `INTEGRATION_TESTS_COMPLETE.md` - Integration tests
- `backend/tests/test_storage_manager.py` - Test examples

---

## 🚨 **EMERGENCY RECOVERY:**

Ako nešto krene naopako:

```bash
# Stop sve servise
sudo systemctl stop ggnet-backend
sudo pkill -f uvicorn

# Destroy test pools
sudo zpool destroy pool0 -f
sudo zpool destroy pool1 -f

# Stop MD RAID
sudo mdadm --stop /dev/md0

# Wipe sve
sudo wipefs -a /dev/sd{b,c,d,e,f,g,h}

# Reinstall OS (ako je potrebno)
# Imaš USB bootable? 😅
```

---

## 🎯 **ZAKLJUČAK:**

Real hardware testing je **KRITIČAN** korak pre production deployment-a!

**Što testirati:**
- ✅ Array detection
- ✅ Device operations
- ✅ Performance
- ✅ Fault tolerance
- ✅ Recovery scenarios
- ✅ API endpoints
- ✅ Frontend integration

**Očekivano trajanje testiranja:** 2-4 sata

**Suština:** Bolje proveri 10 puta nego se kajaj! 🛡️

---

**SREĆNO SA TESTIRANJEM!** 🚀🐧

