"""
Tests for Safety Validator Module

Tests validation logic for storage operations to prevent data loss.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import patch, Mock
from core.safety_validator import SafetyValidator, get_safety_validator


class TestSafetyValidator:
    """Test Safety Validator functionality"""
    
    def test_validator_initialization(self):
        """Test SafetyValidator initialization"""
        validator = SafetyValidator()
        
        assert validator is not None
        assert validator.strict_mode is True  # Default
    
    def test_validate_device_protected(self):
        """Test validation rejects protected devices"""
        validator = SafetyValidator()
        
        # Test protected devices
        is_valid, error = validator.validate_device('sda')
        assert is_valid is False
        assert "protected" in error.lower()
        
        is_valid, error = validator.validate_device('nvme0n1')
        assert is_valid is False
        assert "protected" in error.lower()
    
    def test_validate_device_invalid_name(self):
        """Test validation rejects invalid device names"""
        validator = SafetyValidator()
        
        is_valid, error = validator.validate_device('invalid')
        assert is_valid is False
        assert "invalid" in error.lower()
        
        is_valid, error = validator.validate_device('xvda')
        assert is_valid is False
    
    @patch('os.path.exists')
    @patch('core.safety_validator.SafetyValidator._is_device_mounted')
    @patch('core.safety_validator.SafetyValidator._get_disk_size_gb')
    def test_validate_device_success(self, mock_size, mock_mounted, mock_exists):
        """Test validation accepts valid devices"""
        validator = SafetyValidator()
        
        # Mock device exists, not mounted, good size
        mock_exists.return_value = True
        mock_mounted.return_value = (False, "")
        mock_size.return_value = 1800  # 1.8TB
        
        is_valid, error = validator.validate_device('sdb')
        assert is_valid is True
        assert error == "OK"
    
    @patch('os.path.exists')
    @patch('core.safety_validator.SafetyValidator._is_device_mounted')
    def test_validate_device_mounted(self, mock_mounted, mock_exists):
        """Test validation rejects mounted devices"""
        validator = SafetyValidator()
        
        mock_exists.return_value = True
        mock_mounted.return_value = (True, "/mnt/data")
        
        is_valid, error = validator.validate_device('sdb')
        assert is_valid is False
        assert "mounted" in error.lower()
    
    @patch('os.path.exists')
    @patch('core.safety_validator.SafetyValidator._is_device_mounted')
    @patch('core.safety_validator.SafetyValidator._get_disk_size_gb')
    def test_validate_device_too_small(self, mock_size, mock_mounted, mock_exists):
        """Test validation rejects too small devices"""
        validator = SafetyValidator()
        
        mock_exists.return_value = True
        mock_mounted.return_value = (False, "")
        mock_size.return_value = 50  # 50GB (< 100GB minimum)
        
        is_valid, error = validator.validate_device('sdb')
        assert is_valid is False
        assert "too small" in error.lower()
    
    @patch('os.path.exists')
    @patch('core.safety_validator.SafetyValidator._is_device_mounted')
    @patch('core.safety_validator.SafetyValidator._get_disk_size_gb')
    def test_validate_devices_list(self, mock_size, mock_mounted, mock_exists):
        """Test validation of device list"""
        validator = SafetyValidator()
        
        mock_exists.return_value = True
        mock_mounted.return_value = (False, "")
        mock_size.return_value = 1800
        
        is_valid, error = validator.validate_devices(['sdb', 'sdc', 'sdd'])
        assert is_valid is True
        assert error == "OK"
    
    def test_validate_devices_empty(self):
        """Test validation rejects empty device list"""
        validator = SafetyValidator()
        
        is_valid, error = validator.validate_devices([])
        assert is_valid is False
        assert "no devices" in error.lower()
    
    def test_validate_devices_duplicates(self):
        """Test validation rejects duplicate devices"""
        validator = SafetyValidator()
        
        is_valid, error = validator.validate_devices(['sdb', 'sdc', 'sdb'])
        assert is_valid is False
        assert "duplicate" in error.lower()
    
    def test_validate_devices_too_many(self):
        """Test validation rejects too many devices"""
        validator = SafetyValidator()
        
        # Create list of 25 devices (> MAX_DEVICES_PER_OPERATION)
        devices = [f'sd{chr(98+i)}' for i in range(25)]  # sdb-sdz
        
        is_valid, error = validator.validate_devices(devices)
        assert is_valid is False
        assert "too many" in error.lower()
    
    def test_validate_stripe_number(self):
        """Test stripe number validation"""
        validator = SafetyValidator()
        
        # Valid stripe numbers
        assert validator.validate_stripe_number(0)[0] is True
        assert validator.validate_stripe_number(5)[0] is True
        assert validator.validate_stripe_number(10)[0] is True
        
        # Invalid stripe numbers
        assert validator.validate_stripe_number(-1)[0] is False
        assert validator.validate_stripe_number(11)[0] is False
        assert validator.validate_stripe_number(100)[0] is False
    
    def test_validate_raid_type(self):
        """Test RAID type validation"""
        validator = SafetyValidator()
        
        # Valid RAID types with correct device counts
        assert validator.validate_raid_type('raid0', 2)[0] is True
        assert validator.validate_raid_type('raid1', 2)[0] is True
        assert validator.validate_raid_type('raid10', 4)[0] is True
        assert validator.validate_raid_type('mirror', 2)[0] is True
        assert validator.validate_raid_type('raidz', 3)[0] is True
        assert validator.validate_raid_type('raidz2', 4)[0] is True
        
        # Invalid RAID type
        assert validator.validate_raid_type('invalid', 2)[0] is False
        
        # Insufficient devices
        assert validator.validate_raid_type('raid10', 2)[0] is False  # Needs 4
        assert validator.validate_raid_type('raidz', 2)[0] is False   # Needs 3
        
        # RAID10 requires even number
        assert validator.validate_raid_type('raid10', 5)[0] is False
    
    def test_validate_array_name(self):
        """Test array name validation"""
        validator = SafetyValidator()
        
        # Valid ZFS pool names
        assert validator.validate_array_name('pool0')[0] is True
        assert validator.validate_array_name('pool1')[0] is True
        assert validator.validate_array_name('pool10')[0] is True
        
        # Valid MD RAID array names
        assert validator.validate_array_name('/dev/md0')[0] is True
        assert validator.validate_array_name('/dev/md1')[0] is True
        
        # Invalid names
        assert validator.validate_array_name('')[0] is False
        assert validator.validate_array_name('invalid')[0] is False
        assert validator.validate_array_name('poolX')[0] is False
    
    def test_get_safety_validator_singleton(self):
        """Test safety validator singleton"""
        validator1 = get_safety_validator()
        validator2 = get_safety_validator()
        
        assert validator1 is validator2


class TestSafetyValidatorStrictMode:
    """Test strict mode functionality"""
    
    @patch.dict(os.environ, {'GGNET_STRICT_SAFETY': 'true'})
    def test_strict_mode_enabled(self):
        """Test strict safety mode enabled"""
        validator = SafetyValidator()
        
        assert validator.strict_mode is True
    
    @patch.dict(os.environ, {'GGNET_STRICT_SAFETY': 'false'})
    def test_strict_mode_disabled(self):
        """Test strict safety mode disabled"""
        validator = SafetyValidator()
        
        assert validator.strict_mode is False
    
    @patch.dict(os.environ, {'GGNET_AUTO_CONFIRM': 'false'})
    def test_confirm_destructive_operation_strict(self):
        """Test confirmation required in strict mode"""
        validator = SafetyValidator()
        validator.strict_mode = True
        
        confirmed = validator.confirm_destructive_operation(
            "create stripe",
            ['sdb', 'sdc']
        )
        
        assert confirmed is False  # Requires manual confirmation
    
    @patch.dict(os.environ, {'GGNET_AUTO_CONFIRM': 'true'})
    def test_confirm_destructive_operation_auto(self):
        """Test auto-confirmation"""
        validator = SafetyValidator()
        validator.strict_mode = True
        
        confirmed = validator.confirm_destructive_operation(
            "create stripe",
            ['sdb', 'sdc']
        )
        
        assert confirmed is True  # Auto-confirmed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

