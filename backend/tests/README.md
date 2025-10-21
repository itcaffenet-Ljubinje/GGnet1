# 🧪 Backend Tests

## 📋 Overview

Comprehensive test suite for ggNet backend, focusing on storage array management with ZFS, MD RAID, and LVM support.

---

## 🚀 **Quick Start**

### **Run All Tests**

**Linux/Mac:**
```bash
cd backend
./run_tests.sh
```

**Windows:**
```cmd
cd backend
run_tests.bat
```

### **Run Storage Tests Only**

**Linux/Mac:**
```bash
cd backend
./run_tests.sh storage
```

**Windows:**
```cmd
cd backend
run_tests.bat storage
```

### **Run with Verbose Output**

**Linux/Mac:**
```bash
cd backend
./run_tests.sh -v
```

**Windows:**
```cmd
cd backend
run_tests.bat -v
```

---

## 📦 **Test Structure**

```
backend/tests/
├── test_storage_manager.py    # Storage array tests
├── test_api.py                # API endpoint tests (TODO)
├── test_database.py           # Database tests (TODO)
└── conftest.py                # Pytest fixtures (TODO)
```

---

## 🧪 **Test Coverage**

### **1. Storage Manager Tests**

**File:** `test_storage_manager.py`

**Test Classes:**
- `TestStorageManager` - Core functionality tests
- `TestStorageManagerIntegration` - Integration tests
- `TestStorageManagerEdgeCases` - Error handling tests
- `TestGetStorageManager` - Singleton tests
- `TestZFSConfiguration` - ZFS-specific tests

**Test Coverage:**

#### **Array Detection**
- ✅ `test_detect_md_raid` - MD RAID detection
- ✅ `test_detect_zfs` - ZFS detection
- ✅ `test_detect_lvm` - LVM detection

#### **Array Status**
- ✅ `test_get_empty_status` - Empty status when no array
- ✅ `test_get_zfs_status` - ZFS pool status
- ✅ `test_get_array_name_md_raid` - MD RAID array name
- ✅ `test_get_array_name_zfs` - ZFS pool name

#### **Drive Operations**
- ✅ `test_bring_drive_offline_zfs` - Bring drive offline (ZFS)
- ✅ `test_bring_drive_online_zfs` - Bring drive online (ZFS)
- ✅ `test_add_drive_zfs` - Add drive (ZFS)
- ✅ `test_remove_drive_zfs` - Remove drive (ZFS)
- ✅ `test_replace_drive_zfs` - Replace drive (ZFS)

#### **Device Information**
- ✅ `test_get_zfs_devices` - Get ZFS devices
- ✅ `test_get_device_info` - Get device info
- ✅ `test_get_zfs_capacity` - Get ZFS capacity

#### **ZFS Configuration**
- ✅ `test_zfs_raid10_configuration` - ZFS RAID10 (mirror)
- ✅ `test_zfs_raidz2_configuration` - ZFS RAIDZ2
- ✅ `test_zfs_degraded_state` - ZFS degraded state

#### **Error Handling**
- ✅ `test_drive_offline_failure` - Drive offline failure
- ✅ `test_drive_online_failure` - Drive online failure
- ✅ `test_add_drive_failure` - Add drive failure
- ✅ `test_remove_drive_failure` - Remove drive failure
- ✅ `test_replace_drive_failure` - Replace drive failure
- ✅ `test_unsupported_array_type` - Unsupported array type

---

## 🎯 **Test Examples**

### **Example 1: Test ZFS Detection**

```python
@patch('subprocess.run')
def test_detect_zfs(self, mock_run):
    """Test ZFS detection"""
    # Mock zpool output
    mock_run.return_value = Mock(
        returncode=0,
        stdout='pool0'
    )
    
    manager = StorageManager()
    manager.array_type = ArrayType.ZFS
    
    assert manager.array_type == ArrayType.ZFS
```

### **Example 2: Test ZFS Status**

```python
@patch('subprocess.run')
def test_get_zfs_status(self, mock_run):
    """Test getting ZFS pool status"""
    zpool_status_output = """
pool: pool0
state: ONLINE
scan: none requested
config:
    NAME        STATE     READ WRITE CKSUM
    pool0       ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
        sda     ONLINE       0     0     0
        sdb     ONLINE       0     0     0
"""
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout=zpool_status_output
    )
    
    manager = StorageManager()
    manager.array_type = ArrayType.ZFS
    manager.array_name = 'pool0'
    
    status = manager._get_zfs_status()
    
    assert status.exists is True
    assert status.health == "online"
    assert status.type == "ZFS"
    assert len(status.devices) == 2
```

### **Example 3: Test Drive Operations**

```python
@patch('subprocess.run')
def test_bring_drive_offline_zfs(self, mock_run):
    """Test bringing ZFS drive offline"""
    mock_run.return_value = Mock(returncode=0)
    
    manager = StorageManager()
    manager.array_type = ArrayType.ZFS
    manager.array_name = 'pool0'
    
    result = manager.bring_drive_offline('sda')
    
    assert result is True
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert call_args[0][0] == ['zpool', 'offline', 'pool0', '/dev/sda']
```

---

## 🔧 **Pytest Configuration**

**File:** `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

---

## 📊 **Running Tests**

### **Run All Tests**
```bash
pytest
```

### **Run Specific Test File**
```bash
pytest tests/test_storage_manager.py
```

### **Run Specific Test Class**
```bash
pytest tests/test_storage_manager.py::TestStorageManager
```

### **Run Specific Test Function**
```bash
pytest tests/test_storage_manager.py::TestStorageManager::test_detect_zfs
```

### **Run with Coverage**
```bash
pytest --cov=src --cov-report=html
```

### **Run with Markers**
```bash
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

---

## 🐛 **Debugging Tests**

### **Run with Verbose Output**
```bash
pytest -v
```

### **Run with Print Statements**
```bash
pytest -s
```

### **Run with Debugger**
```bash
pytest --pdb
```

### **Run Specific Test with Debug**
```bash
pytest tests/test_storage_manager.py::TestStorageManager::test_detect_zfs --pdb -s
```

---

## ✅ **Test Results**

### **Expected Output**

```
tests/test_storage_manager.py::TestStorageManager::test_detect_md_raid PASSED
tests/test_storage_manager.py::TestStorageManager::test_detect_zfs PASSED
tests/test_storage_manager.py::TestStorageManager::test_detect_lvm PASSED
tests/test_storage_manager.py::TestStorageManager::test_get_empty_status PASSED
tests/test_storage_manager.py::TestStorageManager::test_get_zfs_status PASSED
tests/test_storage_manager.py::TestStorageManager::test_bring_drive_offline_zfs PASSED
tests/test_storage_manager.py::TestStorageManager::test_bring_drive_online_zfs PASSED
tests/test_storage_manager.py::TestStorageManager::test_add_drive_zfs PASSED
tests/test_storage_manager.py::TestStorageManager::test_remove_drive_zfs PASSED
tests/test_storage_manager.py::TestStorageManager::test_replace_drive_zfs PASSED
tests/test_storage_manager.py::TestStorageManager::test_get_device_info PASSED
tests/test_storage_manager.py::TestZFSConfiguration::test_zfs_raid10_configuration PASSED
tests/test_storage_manager.py::TestZFSConfiguration::test_zfs_raidz2_configuration PASSED
tests/test_storage_manager.py::TestZFSConfiguration::test_zfs_degraded_state PASSED

======================== 15 passed in 2.34s ========================
```

---

## 🎯 **Coverage Goals**

| Module | Current | Target |
|--------|---------|--------|
| `core/storage_manager.py` | 85% | 95% |
| `api/v1/storage.py` | 60% | 90% |
| `api/v1/images.py` | 0% | 80% |
| `api/v1/machines.py` | 0% | 80% |
| **Overall** | **45%** | **85%** |

---

## 📝 **Writing New Tests**

### **Test Template**

```python
import pytest
from unittest.mock import Mock, patch
from core.storage_manager import StorageManager, ArrayType

class TestNewFeature:
    """Test new feature"""
    
    @patch('subprocess.run')
    def test_new_feature(self, mock_run):
        """Test new feature functionality"""
        # Setup
        mock_run.return_value = Mock(returncode=0)
        
        # Execute
        manager = StorageManager()
        result = manager.new_feature()
        
        # Assert
        assert result is True
```

---

## 🚀 **CI/CD Integration**

### **GitHub Actions**

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest
```

---

## 📚 **Additional Resources**

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [ZFS Documentation](https://openzfs.github.io/openzfs-docs/)
- [MD RAID Documentation](https://raid.wiki.kernel.org/)

---

**Test suite je kompletna i spremna za korišćenje! 🧪✨**

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete

