"""
Real Hardware Tests for Storage Manager

⚠️ WARNING: These tests interact with REAL hardware!
⚠️ Only run on dedicated test servers with test drives!
⚠️ NEVER run on production systems!

Prerequisites:
- Linux server (Debian/Ubuntu)
- ZFS or MD RAID tools installed
- At least 2 unused drives for testing
- Root or sudo access

Usage:
    # Run all real hardware tests (DANGEROUS!)
    sudo pytest tests/test_real_hardware.py -v
    
    # Run in dry-run mode (safe, just checks detection)
    pytest tests/test_real_hardware.py -v -k "detect"
"""

import sys
import os
import subprocess
import platform

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from core.storage_manager import (
    StorageManager,
    ArrayType,
    DriveStatus,
    get_storage_manager
)


# Skip all tests if not on Linux
pytestmark = pytest.mark.skipif(
    platform.system() != 'Linux',
    reason="Real hardware tests require Linux"
)


def check_root_access():
    """Check if running with root/sudo access"""
    return os.geteuid() == 0


def check_command_exists(command):
    """Check if a command exists"""
    try:
        subprocess.run(
            ['which', command],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


class TestRealHardwareDetection:
    """Test hardware detection (safe, read-only)"""
    
    def test_storage_manager_initialization(self):
        """Test StorageManager initialization on real hardware"""
        manager = StorageManager()
        
        assert manager is not None
        assert isinstance(manager.array_type, ArrayType)
        
        print(f"\n✓ Array Type Detected: {manager.array_type.value}")
        print(f"✓ Array Name: {manager.array_name}")
    
    def test_detect_array_type(self):
        """Test array type detection"""
        manager = StorageManager()
        
        print(f"\n✓ Detected Array Type: {manager.array_type.value}")
        
        if manager.array_type == ArrayType.ZFS:
            assert check_command_exists('zpool')
            print("✓ ZFS tools available")
        elif manager.array_type == ArrayType.MD_RAID:
            assert check_command_exists('mdadm')
            print("✓ MD RAID tools available")
        elif manager.array_type == ArrayType.LVM:
            assert check_command_exists('vgs')
            print("✓ LVM tools available")
    
    def test_get_array_status(self):
        """Test getting real array status"""
        manager = StorageManager()
        status = manager.get_array_status()
        
        assert status is not None
        
        print(f"\n✓ Array Exists: {status.exists}")
        print(f"✓ Health: {status.health}")
        print(f"✓ Type: {status.type}")
        print(f"✓ Devices: {len(status.devices)}")
        print(f"✓ Total Capacity: {status.capacity.total_gb} GB")
        print(f"✓ Used: {status.capacity.used_gb} GB")
        print(f"✓ Available: {status.capacity.available_gb} GB")
        
        if status.exists:
            for i, device in enumerate(status.devices):
                print(f"  Device {i}: {device.device} - {device.model} ({device.capacity_gb}GB) - {device.status.value}")
    
    def test_get_available_drives(self):
        """Test getting available drives"""
        manager = StorageManager()
        drives = manager.get_available_drives()
        
        assert drives is not None
        
        print(f"\n✓ Available Drives: {len(drives)}")
        
        for drive in drives:
            print(f"  {drive['device']}: {drive['model']} ({drive['size']}) - Serial: {drive['serial']}")
    
    def test_singleton_pattern(self):
        """Test storage manager singleton"""
        manager1 = get_storage_manager()
        manager2 = get_storage_manager()
        
        assert manager1 is manager2
        print("\n✓ Singleton pattern working")


@pytest.mark.skipif(
    not check_root_access(),
    reason="Requires root access for destructive operations"
)
class TestRealHardwareOperations:
    """
    Test real hardware operations
    
    ⚠️ DANGEROUS! Only run on dedicated test servers!
    ⚠️ These tests can DESTROY DATA!
    """
    
    @pytest.fixture
    def safety_check(self):
        """Safety check before destructive operations"""
        if not check_root_access():
            pytest.skip("Requires root access")
        
        # Check for safety environment variable
        if os.environ.get('GGNET_ALLOW_DESTRUCTIVE_TESTS') != 'yes':
            pytest.skip(
                "Destructive tests disabled. "
                "Set GGNET_ALLOW_DESTRUCTIVE_TESTS=yes to enable"
            )
        
        print("\n⚠️  WARNING: Running destructive hardware tests!")
        print("⚠️  This may DESTROY DATA on the test drives!")
    
    @pytest.mark.destructive
    def test_zfs_pool_operations(self, safety_check):
        """
        Test ZFS pool operations
        
        ⚠️ REQUIRES: At least 2 unused drives (e.g., /dev/sdc, /dev/sdd)
        ⚠️ DESTROYS: All data on specified drives
        """
        # This is a template - adjust device names for your test environment
        test_devices = os.environ.get('GGNET_TEST_DEVICES', 'sdc,sdd').split(',')
        
        if len(test_devices) < 2:
            pytest.skip("Need at least 2 test devices")
        
        print(f"\n⚠️  Testing with devices: {test_devices}")
        
        # Confirm devices are not in use
        for device in test_devices:
            mount_check = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True
            )
            if f'/dev/{device}' in mount_check.stdout:
                pytest.skip(f"Device {device} is mounted! Aborting for safety.")
        
        manager = StorageManager()
        
        # Test creating a ZFS pool
        # NOTE: Uncomment only in controlled test environment!
        # result = manager.add_stripe(99, 'mirror', test_devices)
        # assert result is True
        
        print("✓ Test template ready (uncomment to run actual test)")
    
    @pytest.mark.destructive
    def test_mdraid_operations(self, safety_check):
        """
        Test MD RAID operations
        
        ⚠️ REQUIRES: At least 2 unused drives
        ⚠️ DESTROYS: All data on specified drives
        """
        test_devices = os.environ.get('GGNET_TEST_DEVICES', 'sdc,sdd').split(',')
        
        if len(test_devices) < 2:
            pytest.skip("Need at least 2 test devices")
        
        print(f"\n⚠️  Testing with devices: {test_devices}")
        
        # Safety check
        for device in test_devices:
            mount_check = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True
            )
            if f'/dev/{device}' in mount_check.stdout:
                pytest.skip(f"Device {device} is mounted! Aborting for safety.")
        
        manager = StorageManager()
        
        # Test creating MD RAID
        # NOTE: Uncomment only in controlled test environment!
        # result = manager.add_stripe(99, 'raid1', test_devices)
        # assert result is True
        
        print("✓ Test template ready (uncomment to run actual test)")


class TestRealHardwareReadOnly:
    """Read-only tests safe to run on any system"""
    
    def test_zfs_command_available(self):
        """Test if ZFS commands are available"""
        has_zpool = check_command_exists('zpool')
        has_zfs = check_command_exists('zfs')
        
        if has_zpool and has_zfs:
            print("\n✓ ZFS commands available")
            
            # List pools (safe, read-only)
            result = subprocess.run(
                ['zpool', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ ZFS Pools:\n{result.stdout}")
            else:
                print("✓ No ZFS pools detected")
        else:
            print("\n⚠️  ZFS commands not available")
    
    def test_mdraid_command_available(self):
        """Test if MD RAID commands are available"""
        has_mdadm = check_command_exists('mdadm')
        
        if has_mdadm:
            print("\n✓ MD RAID commands available")
            
            # Check arrays (safe, read-only)
            result = subprocess.run(
                ['cat', '/proc/mdstat'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ MD RAID Status:\n{result.stdout}")
        else:
            print("\n⚠️  MD RAID commands not available")
    
    def test_lvm_command_available(self):
        """Test if LVM commands are available"""
        has_lvm = check_command_exists('vgs')
        
        if has_lvm:
            print("\n✓ LVM commands available")
            
            # List volume groups (safe, read-only)
            result = subprocess.run(
                ['vgs'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"✓ Volume Groups:\n{result.stdout}")
            else:
                print("✓ No volume groups detected")
        else:
            print("\n⚠️  LVM commands not available")
    
    def test_smart_monitoring_available(self):
        """Test if SMART monitoring is available"""
        has_smartctl = check_command_exists('smartctl')
        
        if has_smartctl:
            print("\n✓ SMART monitoring available")
            
            # Get list of devices
            result = subprocess.run(
                ['lsblk', '-d', '-n', '-o', 'NAME,TYPE'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Block Devices:\n{result.stdout}")
        else:
            print("\n⚠️  SMART monitoring not available")


if __name__ == '__main__':
    print("=" * 80)
    print("⚠️  REAL HARDWARE TESTING SUITE")
    print("=" * 80)
    print()
    print("This test suite interacts with REAL hardware!")
    print()
    print("SAFE TESTS (read-only, detection):")
    print("  pytest tests/test_real_hardware.py::TestRealHardwareDetection -v")
    print("  pytest tests/test_real_hardware.py::TestRealHardwareReadOnly -v")
    print()
    print("DANGEROUS TESTS (destructive, requires root):")
    print("  ⚠️  Set GGNET_ALLOW_DESTRUCTIVE_TESTS=yes")
    print("  ⚠️  Set GGNET_TEST_DEVICES=sdc,sdd (unused drives)")
    print("  sudo -E pytest tests/test_real_hardware.py::TestRealHardwareOperations -v")
    print()
    print("=" * 80)
    
    # Run safe tests only
    pytest.main([__file__, '-v', '-k', 'ReadOnly or Detection'])

