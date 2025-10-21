# 🐧 REAL HARDWARE TESTING - README

**Quick Start Guide za Real Hardware Testing**

---

## ⚠️ **PRE NEGO ŠTO POČNEŠ:**

**OPASNOST:** Ovi testovi mogu da **UNIŠTE SVE PODATKE** na diskovima!

**NIKADA ne pokreći:**
- ❌ Na production serveru
- ❌ Sa diskovima koji sadrže podatke
- ❌ Bez backup-a
- ❌ Ako nisi 100% siguran šta radiš

**UVEK koristi:**
- ✅ Dedicated test server
- ✅ Prazne, nekorišćene diskove
- ✅ Test environment
- ✅ Safety checks enabled

---

## 🚀 **QUICK START:**

### **1. Proveri da li si na Linux:**
```bash
uname -a
# Očekivano: Linux...
```

### **2. Proveri dostupne diskove:**
```bash
lsblk
# Identifikuj NEKORIŠĆENE diskove (npr. sdb, sdc, sdd)
```

### **3. Pokreni SAFE testove (read-only):**
```bash
cd /srv/ggnet/backend
source venv/bin/activate

# Detection tests (100% safe)
pytest tests/test_real_hardware.py::TestRealHardwareDetection -v -s

# Command availability (100% safe)
pytest tests/test_real_hardware.py::TestRealHardwareReadOnly -v -s
```

**Očekivani output:**
```
✓ Array Type Detected: zfs (ili mdraid, ili unknown)
✓ Array Name: pool0
✓ ZFS commands available
✓ Available Drives: 4
  sdb: Samsung SSD (1.8T)
  sdc: Samsung SSD (1.8T)
  sdd: Samsung SSD (1.8T)
  sde: Samsung SSD (1.8T)

5 passed in 2.34s
```

---

## ⚙️ **DESTRUCTIVE TESTS (⚠️ OPASNO!):**

**SAMO za dedicirane test servere!**

### **Setup:**
```bash
# 1. Identifikuj test diskove
export GGNET_TEST_DEVICES=sdb,sdc,sdd,sde

# 2. Proveri da nisu mountovani
mount | grep -E 'sd[b-e]'
# Očekivano: nema output-a

# 3. Enable destructive tests
export GGNET_ALLOW_DESTRUCTIVE_TESTS=yes

# 4. Pokreni (AS ROOT!)
sudo -E pytest tests/test_real_hardware.py::TestRealHardwareOperations -v -s
```

**⚠️ PAŽNJA:** Ovo će **POBRISATI SVE** na navedenim diskovima!

---

## 🧪 **TEST CATEGORIJE:**

### **Safe Tests (Read-Only):**
- ✅ `TestRealHardwareDetection` - Array detection
- ✅ `TestRealHardwareReadOnly` - Command availability

**Može se pokrenuti bilo kad, potpuno safe!**

### **Destructive Tests (⚠️ Dangerous!):**
- ⚠️ `TestRealHardwareOperations` - Actual operations

**SAMO na test serverima sa praznim diskovima!**

---

## 📋 **PRE-FLIGHT CHECKLIST:**

Pre destructive testova:

- [ ] ✅ Na test serveru (NE production!)
- [ ] ✅ Identifikovani test diskovi
- [ ] ✅ Diskovi NISU mountovani
- [ ] ✅ Diskovi su prazni (wipeovani)
- [ ] ✅ Export-ovao si `GGNET_TEST_DEVICES`
- [ ] ✅ Export-ovao si `GGNET_ALLOW_DESTRUCTIVE_TESTS=yes`
- [ ] ✅ Pokrećeš kao root (`sudo -E`)
- [ ] ✅ Imaš backup plan
- [ ] ✅ Razumeš rizike

---

## 📊 **EXPECTED RESULTS:**

### **Safe Tests:**
```
tests/test_real_hardware.py::TestRealHardwareDetection::test_storage_manager_initialization PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_detect_array_type PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_get_array_status PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_get_available_drives PASSED
tests/test_real_hardware.py::TestRealHardwareDetection::test_singleton_pattern PASSED

======================== 5 passed in 2.34s ========================
```

### **Destructive Tests:**
```
tests/test_real_hardware.py::TestRealHardwareOperations::test_zfs_pool_operations PASSED
tests/test_real_hardware.py::TestRealHardwareOperations::test_mdraid_operations PASSED

======================== 2 passed in 45.67s ========================
```

---

## 🔧 **TROUBLESHOOTING:**

### **Testovi se skip-uju:**
```bash
# Razlog: Nisi na Linux-u
uname -a

# Razlog: Nemaš root pristup
sudo -E pytest tests/test_real_hardware.py -v

# Razlog: Nije enabled destructive tests
export GGNET_ALLOW_DESTRUCTIVE_TESTS=yes
```

### **Permission denied:**
```bash
# Dodaj user u disk grupu
sudo usermod -aG disk ggnet

# Ili pokreni kao root
sudo -E pytest tests/test_real_hardware.py -v
```

### **Device busy:**
```bash
# Proveri ko koristi disk
lsof /dev/sdb
fuser -v /dev/sdb

# Force umount
umount -f /dev/sdb

# Wipe
wipefs -a /dev/sdb
```

---

## 📚 **ADDITIONAL RESOURCES:**

- `REAL_HARDWARE_TESTING_GUIDE.md` - Comprehensive guide (500+ lines)
- `DEPLOYMENT_GUIDE.md` - Production deployment (400+ lines)
- `COMPLETE_TEST_SUITE_SUMMARY.md` - Full summary (600+ lines)

---

## ✨ **ZAKLJUČAK:**

**Real hardware testing infrastructure je spremna!**

- ✅ Safe detection tests (5 tests)
- ✅ Read-only command tests (4 tests)
- ✅ Destructive operation templates (2 tests)
- ✅ Safety features enabled
- ✅ Comprehensive documentation

**Status:** ✅ **READY FOR REAL HARDWARE TESTING**

---

**Za detaljne instrukcije, vidi:** `REAL_HARDWARE_TESTING_GUIDE.md`

**SREĆNO! 🚀🐧**

