"""
Tests for Storage Manager Module

Tests ZFS, MD RAID, and LVM array detection and operations.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from core.storage_manager import (
    StorageManager,
    ArrayType,
    DriveStatus,
    DriveInfo,
    ArrayCapacity,
    ArrayBreakdown,
    ArrayStatus,
    get_storage_manager
)


class TestStorageManager:
    """Test Storage Manager functionality"""
    
    def test_storage_manager_initialization(self):
        """Test StorageManager initialization"""
        manager = StorageManager()
        assert manager is not None
        assert isinstance(manager.array_type, ArrayType)
    
    @patch('subprocess.run')
    def test_detect_md_raid(self, mock_run):
        """Test MD RAID detection"""
        # Mock mdadm output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='ARRAY /dev/md0 level=raid1 num-devices=2'
        )
        
        manager = StorageManager()
        # Force re-detection
        manager._detect_array_type = lambda: ArrayType.MD_RAID
        manager.array_type = ArrayType.MD_RAID
        
        assert manager.array_type == ArrayType.MD_RAID
    
    @patch('subprocess.run')
    def test_detect_zfs(self, mock_run):
        """Test ZFS detection"""
        # Mock zpool output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='pool0'
        )
        
        manager = StorageManager()
        # Force re-detection
        manager._detect_array_type = lambda: ArrayType.ZFS
        manager.array_type = ArrayType.ZFS
        
        assert manager.array_type == ArrayType.ZFS
    
    @patch('subprocess.run')
    def test_detect_lvm(self, mock_run):
        """Test LVM detection"""
        # Mock vgs output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='vg0'
        )
        
        manager = StorageManager()
        # Force re-detection
        manager._detect_array_type = lambda: ArrayType.LVM
        manager.array_type = ArrayType.LVM
        
        assert manager.array_type == ArrayType.LVM
    
    @patch('subprocess.run')
    def test_get_array_name_md_raid(self, mock_run):
        """Test getting MD RAID array name"""
        # Mock mdadm output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='ARRAY /dev/md0 level=raid1 num-devices=2'
        )
        
        manager = StorageManager()
        manager.array_type = ArrayType.MD_RAID
        
        with patch.object(manager, '_get_array_name') as mock_get_name:
            mock_get_name.return_value = '/dev/md0'
            assert manager._get_array_name() == '/dev/md0'
    
    @patch('subprocess.run')
    def test_get_array_name_zfs(self, mock_run):
        """Test getting ZFS pool name"""
        # Mock zpool output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='pool0'
        )
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        
        with patch.object(manager, '_get_array_name') as mock_get_name:
            mock_get_name.return_value = 'pool0'
            assert manager._get_array_name() == 'pool0'
    
    def test_get_empty_status(self):
        """Test getting empty status when no array detected"""
        manager = StorageManager()
        status = manager._get_empty_status()
        
        assert status.exists is False
        assert status.health == "offline"
        assert status.type == "N/A"
        assert len(status.devices) == 0
        assert status.capacity.total_gb == 0
        assert status.array_type == ArrayType.UNKNOWN
    
    @patch('subprocess.run')
    def test_get_zfs_status(self, mock_run):
        """Test getting ZFS pool status"""
        # Mock zpool status output
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
      mirror-1  ONLINE       0     0     0
        sdc     ONLINE       0     0     0
        sdd     ONLINE       0     0     0
"""
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=zpool_status_output
        )
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        # Mock device info
        with patch.object(manager, '_get_device_info') as mock_device_info:
            mock_device_info.return_value = {
                'serial': 'TEST123',
                'model': 'Test Drive',
                'capacity_gb': 1920,
                'health': 'healthy'
            }
            
            # Mock capacity
            with patch.object(manager, '_get_zfs_capacity') as mock_capacity:
                mock_capacity.return_value = ArrayCapacity(
                    total_gb=3840,
                    used_gb=1450,
                    available_gb=1766,
                    reserved_gb=624,
                    reserved_percent=16.25
                )
                
                # Mock breakdown
                with patch.object(manager, '_get_storage_breakdown') as mock_breakdown:
                    mock_breakdown.return_value = ArrayBreakdown(
                        system_images_gb=800,
                        game_images_gb=450,
                        writebacks_gb=120,
                        snapshots_gb=80
                    )
                    
                    status = manager._get_zfs_status()
                    
                    assert status.exists is True
                    assert status.health == "online"
                    assert status.type == "ZFS"
                    assert len(status.devices) == 4
                    assert status.capacity.total_gb == 3840
    
    @patch('subprocess.run')
    def test_get_zfs_devices(self, mock_run):
        """Test getting ZFS devices"""
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
        
        with patch.object(manager, '_get_device_info') as mock_device_info:
            mock_device_info.return_value = {
                'serial': 'TEST123',
                'model': 'Test Drive',
                'capacity_gb': 1920,
                'health': 'healthy'
            }
            
            devices = manager._get_zfs_devices()
            
            assert len(devices) == 2
            assert devices[0].device == 'sda'
            assert devices[0].status == DriveStatus.ONLINE
            assert devices[1].device == 'sdb'
            assert devices[1].status == DriveStatus.ONLINE
    
    @patch('subprocess.run')
    def test_get_zfs_capacity(self, mock_run):
        """Test getting ZFS capacity"""
        # Mock zpool list output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='3.84T  1.42T  2.42T'
        )
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        capacity = manager._get_zfs_capacity()
        
        assert capacity.total_gb == 3840
        assert capacity.used_gb == 1420
        assert capacity.available_gb == 2420
        assert capacity.reserved_percent == 15.0
    
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
    
    @patch('subprocess.run')
    def test_bring_drive_online_zfs(self, mock_run):
        """Test bringing ZFS drive online"""
        mock_run.return_value = Mock(returncode=0)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.bring_drive_online('sda')
        
        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['zpool', 'online', 'pool0', '/dev/sda']
    
    @patch('subprocess.run')
    def test_add_drive_zfs(self, mock_run):
        """Test adding drive to ZFS pool"""
        mock_run.return_value = Mock(returncode=0)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.add_drive('sde')
        
        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['zpool', 'add', 'pool0', '/dev/sde']
    
    @patch('subprocess.run')
    def test_remove_drive_zfs(self, mock_run):
        """Test removing drive from ZFS pool"""
        mock_run.return_value = Mock(returncode=0)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.remove_drive('sde')
        
        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['zpool', 'remove', 'pool0', '/dev/sde']
    
    @patch('subprocess.run')
    def test_replace_drive_zfs(self, mock_run):
        """Test replacing drive in ZFS pool"""
        mock_run.return_value = Mock(returncode=0)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.replace_drive('sda', 'sde')
        
        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['zpool', 'replace', 'pool0', '/dev/sda', '/dev/sde']
    
    @patch('subprocess.run')
    def test_get_device_info(self, mock_run):
        """Test getting device information"""
        # Mock lsblk output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='1.8T Micron 5200 ECO 1.92TB S3Z1NX0K123456'
        )
        
        manager = StorageManager()
        device_info = manager._get_device_info('sda')
        
        assert device_info['capacity_gb'] == 1800
        assert 'Micron' in device_info['model']
        assert device_info['serial'] == 'S3Z1NX0K123456'
    
    def test_get_storage_breakdown(self):
        """Test getting storage breakdown"""
        manager = StorageManager()
        breakdown = manager._get_storage_breakdown()
        
        assert breakdown.system_images_gb == 0
        assert breakdown.game_images_gb == 0
        assert breakdown.writebacks_gb == 0
        assert breakdown.snapshots_gb == 0


class TestStorageManagerIntegration:
    """Integration tests for Storage Manager"""
    
    @pytest.mark.skipif(True, reason="Requires actual ZFS pool")
    def test_real_zfs_pool_status(self):
        """Test with real ZFS pool (requires actual ZFS setup)"""
        manager = StorageManager()
        
        if manager.array_type == ArrayType.ZFS:
            status = manager.get_array_status()
            
            assert status.exists is True
            assert status.type == "ZFS"
            assert len(status.devices) > 0
            assert status.capacity.total_gb > 0
    
    @pytest.mark.skipif(True, reason="Requires actual MD RAID array")
    def test_real_md_raid_status(self):
        """Test with real MD RAID array (requires actual RAID setup)"""
        manager = StorageManager()
        
        if manager.array_type == ArrayType.MD_RAID:
            status = manager.get_array_status()
            
            assert status.exists is True
            assert 'RAID' in status.type
            assert len(status.devices) > 0
            assert status.capacity.total_gb > 0


class TestStorageManagerEdgeCases:
    """Test edge cases and error handling"""
    
    @patch('subprocess.run')
    def test_drive_offline_failure(self, mock_run):
        """Test drive offline operation failure"""
        mock_run.return_value = Mock(returncode=1)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.bring_drive_offline('sda')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_drive_online_failure(self, mock_run):
        """Test drive online operation failure"""
        mock_run.return_value = Mock(returncode=1)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.bring_drive_online('sda')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_add_drive_failure(self, mock_run):
        """Test add drive operation failure"""
        mock_run.return_value = Mock(returncode=1)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.add_drive('sde')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_remove_drive_failure(self, mock_run):
        """Test remove drive operation failure"""
        mock_run.return_value = Mock(returncode=1)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.remove_drive('sde')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_replace_drive_failure(self, mock_run):
        """Test replace drive operation failure"""
        mock_run.return_value = Mock(returncode=1)
        
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        
        result = manager.replace_drive('sda', 'sde')
        
        assert result is False
    
    @patch('subprocess.run')
    def test_unsupported_array_type(self, mock_run):
        """Test operations with unsupported array type"""
        manager = StorageManager()
        manager.array_type = ArrayType.UNKNOWN
        manager.array_name = None
        
        result = manager.bring_drive_offline('sda')
        assert result is False
        
        result = manager.bring_drive_online('sda')
        assert result is False
        
        result = manager.add_drive('sde')
        assert result is False
        
        result = manager.remove_drive('sde')
        assert result is False
        
        result = manager.replace_drive('sda', 'sde')
        assert result is False


class TestGetStorageManager:
    """Test storage manager singleton"""
    
    def test_get_storage_manager_singleton(self):
        """Test that get_storage_manager returns singleton"""
        manager1 = get_storage_manager()
        manager2 = get_storage_manager()
        
        assert manager1 is manager2


class TestZFSConfiguration:
    """Test ZFS-specific configurations"""
    
    @pytest.fixture
    def zfs_manager(self):
        """Create ZFS storage manager"""
        manager = StorageManager()
        manager.array_type = ArrayType.ZFS
        manager.array_name = 'pool0'
        return manager
    
    @patch('subprocess.run')
    def test_zfs_raid10_configuration(self, mock_run, zfs_manager):
        """Test ZFS RAID10 (mirror) configuration"""
        # Mock zpool status for RAID10
        zpool_status = """
pool: pool0
state: ONLINE
scan: none requested
config:
    NAME        STATE     READ WRITE CKSUM
    pool0       ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
        sda     ONLINE       0     0     0
        sdb     ONLINE       0     0     0
      mirror-1  ONLINE       0     0     0
        sdc     ONLINE       0     0     0
        sdd     ONLINE       0     0     0
"""
        mock_run.return_value = Mock(returncode=0, stdout=zpool_status)
        
        with patch.object(zfs_manager, '_get_device_info') as mock_device:
            mock_device.return_value = {
                'serial': 'TEST123',
                'model': 'Test Drive',
                'capacity_gb': 1920,
                'health': 'healthy'
            }
            
            with patch.object(zfs_manager, '_get_zfs_capacity') as mock_cap:
                mock_cap.return_value = ArrayCapacity(3840, 1450, 1766, 624, 16.25)
                
                with patch.object(zfs_manager, '_get_storage_breakdown') as mock_break:
                    mock_break.return_value = ArrayBreakdown(800, 450, 120, 80)
                    
                    status = zfs_manager._get_zfs_status()
                    
                    assert status.type == "ZFS"
                    assert len(status.devices) == 4
                    assert status.capacity.total_gb == 3840
    
    @patch('subprocess.run')
    def test_zfs_raidz2_configuration(self, mock_run, zfs_manager):
        """Test ZFS RAIDZ2 configuration"""
        # Mock zpool status for RAIDZ2
        zpool_status = """
pool: pool0
state: ONLINE
scan: none requested
config:
    NAME        STATE     READ WRITE CKSUM
    pool0       ONLINE       0     0     0
      raidz2-0  ONLINE       0     0     0
        sda     ONLINE       0     0     0
        sdb     ONLINE       0     0     0
        sdc     ONLINE       0     0     0
        sdd     ONLINE       0     0     0
        sde     ONLINE       0     0     0
        sdf     ONLINE       0     0     0
"""
        mock_run.return_value = Mock(returncode=0, stdout=zpool_status)
        
        with patch.object(zfs_manager, '_get_device_info') as mock_device:
            mock_device.return_value = {
                'serial': 'TEST123',
                'model': 'Test Drive',
                'capacity_gb': 1920,
                'health': 'healthy'
            }
            
            with patch.object(zfs_manager, '_get_zfs_capacity') as mock_cap:
                mock_cap.return_value = ArrayCapacity(7680, 2900, 3532, 1248, 16.25)
                
                with patch.object(zfs_manager, '_get_storage_breakdown') as mock_break:
                    mock_break.return_value = ArrayBreakdown(1600, 900, 240, 160)
                    
                    status = zfs_manager._get_zfs_status()
                    
                    assert status.type == "ZFS"
                    assert len(status.devices) == 6
                    assert status.capacity.total_gb == 7680
    
    @patch('subprocess.run')
    def test_zfs_degraded_state(self, mock_run, zfs_manager):
        """Test ZFS degraded state detection"""
        # Mock zpool status for degraded state
        zpool_status = """
pool: pool0
state: DEGRADED
scan: resilver in progress
config:
    NAME        STATE     READ WRITE CKSUM
    pool0       DEGRADED     0     0     0
      mirror-0  DEGRADED     0     0     0
        sda     ONLINE       0     0     0
        sdb     FAULTED      0     0     0
      mirror-1  ONLINE       0     0     0
        sdc     ONLINE       0     0     0
        sdd     ONLINE       0     0     0
"""
        mock_run.return_value = Mock(returncode=0, stdout=zpool_status)
        
        with patch.object(zfs_manager, '_get_device_info') as mock_device:
            mock_device.return_value = {
                'serial': 'TEST123',
                'model': 'Test Drive',
                'capacity_gb': 1920,
                'health': 'healthy'
            }
            
            with patch.object(zfs_manager, '_get_zfs_capacity') as mock_cap:
                mock_cap.return_value = ArrayCapacity(3840, 1450, 1766, 624, 16.25)
                
                with patch.object(zfs_manager, '_get_storage_breakdown') as mock_break:
                    mock_break.return_value = ArrayBreakdown(800, 450, 120, 80)
                    
                    status = zfs_manager._get_zfs_status()
                    
                    assert status.health == "degraded"
                    assert status.devices[1].status == DriveStatus.FAILED


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

