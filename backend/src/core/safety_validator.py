"""
Safety Validator Module

Provides safety checks for destructive storage operations.
Prevents accidental data loss and validates operations before execution.
"""

import os
import subprocess
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class SafetyValidator:
    """Validates storage operations for safety"""
    
    # Protected devices (never allow operations on these)
    PROTECTED_DEVICES = ['sda', 'sda1', 'sda2', 'nvme0n1', 'nvme0n1p1']
    
    # Minimum disk size for array (in GB) - prevents using USB drives accidentally
    MIN_DISK_SIZE_GB = 100
    
    # Maximum devices in a single operation (sanity check)
    MAX_DEVICES_PER_OPERATION = 20
    
    def __init__(self):
        self.strict_mode = os.environ.get('GGNET_STRICT_SAFETY', 'true').lower() == 'true'
        
        if self.strict_mode:
            logger.info("🛡️  Strict safety mode ENABLED")
        else:
            logger.warning("⚠️  Strict safety mode DISABLED - Use with caution!")
    
    def validate_device(self, device: str) -> Tuple[bool, str]:
        """
        Validate a device name for safety
        
        Args:
            device: Device name (e.g., 'sdb', 'sdc')
            
        Returns:
            (is_valid, error_message)
        """
        # Check if device is protected
        if device in self.PROTECTED_DEVICES:
            return False, f"Device {device} is protected (likely OS disk)"
        
        # Check device name format
        if not (device.startswith('sd') or device.startswith('nvme') or device.startswith('hd')):
            return False, f"Invalid device name: {device}"
        
        # Check if device exists
        device_path = f'/dev/{device}'
        if not os.path.exists(device_path):
            return False, f"Device {device_path} does not exist"
        
        # Check if device is mounted
        is_mounted, mount_point = self._is_device_mounted(device)
        if is_mounted:
            return False, f"Device {device} is mounted at {mount_point} - unmount first!"
        
        # Check disk size
        size_gb = self._get_disk_size_gb(device)
        if size_gb > 0 and size_gb < self.MIN_DISK_SIZE_GB:
            return False, f"Device {device} is too small ({size_gb}GB < {self.MIN_DISK_SIZE_GB}GB minimum)"
        
        return True, "OK"
    
    def validate_devices(self, devices: List[str]) -> Tuple[bool, str]:
        """
        Validate multiple devices
        
        Args:
            devices: List of device names
            
        Returns:
            (are_valid, error_message)
        """
        if not devices:
            return False, "No devices provided"
        
        if len(devices) > self.MAX_DEVICES_PER_OPERATION:
            return False, f"Too many devices ({len(devices)} > {self.MAX_DEVICES_PER_OPERATION})"
        
        # Check for duplicates first (before expensive validation)
        if len(devices) != len(set(devices)):
            return False, "Duplicate devices in list"
        
        # Check each device
        for device in devices:
            is_valid, error_msg = self.validate_device(device)
            if not is_valid:
                return False, f"Device {device}: {error_msg}"
        
        return True, "OK"
    
    def validate_stripe_number(self, stripe_number: int) -> Tuple[bool, str]:
        """
        Validate stripe number
        
        Args:
            stripe_number: Stripe number (0-10)
            
        Returns:
            (is_valid, error_message)
        """
        if stripe_number < 0 or stripe_number > 10:
            return False, f"Stripe number must be between 0 and 10 (got {stripe_number})"
        
        return True, "OK"
    
    def validate_raid_type(self, raid_type: str, num_devices: int) -> Tuple[bool, str]:
        """
        Validate RAID type and device count
        
        Args:
            raid_type: RAID type (raid0, raid1, raid10, mirror, raidz, raidz2)
            num_devices: Number of devices
            
        Returns:
            (is_valid, error_message)
        """
        valid_types = {
            'raid0': 2,      # Minimum 2 devices
            'raid1': 2,      # Minimum 2 devices
            'raid10': 4,     # Minimum 4 devices
            'mirror': 2,     # Minimum 2 devices (ZFS)
            'raidz': 3,      # Minimum 3 devices (ZFS)
            'raidz2': 4,     # Minimum 4 devices (ZFS)
            'stripe': 1,     # Minimum 1 device (ZFS)
        }
        
        if raid_type not in valid_types:
            return False, f"Invalid RAID type: {raid_type}"
        
        min_devices = valid_types[raid_type]
        if num_devices < min_devices:
            return False, f"{raid_type} requires minimum {min_devices} devices (got {num_devices})"
        
        # RAID10 requires even number of devices
        if raid_type == 'raid10' and num_devices % 2 != 0:
            return False, f"RAID10 requires even number of devices (got {num_devices})"
        
        return True, "OK"
    
    def confirm_destructive_operation(self, operation: str, devices: List[str]) -> bool:
        """
        Request confirmation for destructive operations
        
        Args:
            operation: Operation name (e.g., "create stripe", "wipe device")
            devices: Affected devices
            
        Returns:
            True if confirmed (or auto-confirmed in non-strict mode)
        """
        if not self.strict_mode:
            return True
        
        # In production, this would integrate with frontend for user confirmation
        # For now, just log the warning
        logger.warning(f"⚠️  DESTRUCTIVE OPERATION: {operation}")
        logger.warning(f"⚠️  Affected devices: {', '.join(devices)}")
        logger.warning(f"⚠️  ALL DATA ON THESE DEVICES WILL BE DESTROYED!")
        
        # Check for auto-confirm environment variable
        auto_confirm = os.environ.get('GGNET_AUTO_CONFIRM', 'false').lower() == 'true'
        
        if auto_confirm:
            logger.warning("⚠️  AUTO-CONFIRM enabled - proceeding without confirmation")
            return True
        
        # In strict mode without auto-confirm, require manual override
        return False
    
    def _is_device_mounted(self, device: str) -> Tuple[bool, str]:
        """
        Check if device is mounted
        
        Args:
            device: Device name
            
        Returns:
            (is_mounted, mount_point)
        """
        try:
            result = subprocess.run(
                ['mount'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            device_path = f'/dev/{device}'
            for line in result.stdout.split('\n'):
                if device_path in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mount_point = parts[2]
                        return True, mount_point
            
            return False, ""
        
        except Exception as e:
            logger.error(f"Error checking if device is mounted: {e}")
            # Assume mounted for safety
            return True, "unknown"
    
    def _get_disk_size_gb(self, device: str) -> int:
        """
        Get disk size in GB
        
        Args:
            device: Device name
            
        Returns:
            Size in GB (0 if error)
        """
        try:
            result = subprocess.run(
                ['lsblk', '-b', '-d', '-n', '-o', 'SIZE', f'/dev/{device}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                size_bytes = int(result.stdout.strip())
                size_gb = size_bytes // (1024 ** 3)
                return size_gb
            
            return 0
        
        except Exception as e:
            logger.error(f"Error getting disk size: {e}")
            return 0
    
    def validate_array_name(self, array_name: str) -> Tuple[bool, str]:
        """
        Validate array name
        
        Args:
            array_name: Array name (e.g., 'pool0', '/dev/md0')
            
        Returns:
            (is_valid, error_message)
        """
        if not array_name:
            return False, "Array name cannot be empty"
        
        # Check format
        if array_name.startswith('pool'):
            # ZFS pool name
            if not array_name[4:].isdigit():
                return False, f"Invalid ZFS pool name: {array_name}"
        elif array_name.startswith('/dev/md'):
            # MD RAID array name
            if not array_name.split('md')[-1].isdigit():
                return False, f"Invalid MD RAID array name: {array_name}"
        else:
            return False, f"Invalid array name format: {array_name}"
        
        return True, "OK"


# Singleton instance
_safety_validator = None


def get_safety_validator() -> SafetyValidator:
    """Get safety validator singleton"""
    global _safety_validator
    
    if _safety_validator is None:
        _safety_validator = SafetyValidator()
    
    return _safety_validator

