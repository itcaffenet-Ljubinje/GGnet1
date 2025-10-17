#!/usr/bin/env python3
"""
Array Manager - RAID10 Array Management

High-level Python interface for managing the SSD/HDD RAID10 array.
Wraps mdadm and ZFS commands with a clean API.

Usage:
    from storage.array_manager import ArrayManager
    
    manager = ArrayManager()
    status = manager.get_status()
    health = manager.check_health()
"""

import subprocess
import json
import os
import re
from typing import Dict, List, Optional
from pathlib import Path


class ArrayManager:
    """Manages RAID10 storage array operations"""
    
    def __init__(self, array_device: str = "/dev/md0", mount_point: str = "/srv/ggnet/array"):
        """
        Initialize array manager
        
        Args:
            array_device: RAID device path (e.g., /dev/md0)
            mount_point: Where the array is mounted
        """
        self.array_device = array_device
        self.mount_point = Path(mount_point)
        self.mdstat_path = Path("/proc/mdstat")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current array status
        
        Returns:
            Dict with array health, capacity, and device info
        """
        status = {
            "exists": self.array_exists(),
            "health": "unknown",
            "type": "RAID10",
            "devices": [],
            "capacity": {},
            "mount_point": str(self.mount_point),
        }
        
        if not status["exists"]:
            return status
        
        # Get RAID health from mdstat
        try:
            with open(self.mdstat_path, 'r') as f:
                mdstat = f.read()
                
                # Parse mdstat for array status
                if "active raid10" in mdstat or "active raid1" in mdstat:
                    status["health"] = "healthy"
                elif "degraded" in mdstat:
                    status["health"] = "degraded"
                elif "recovery" in mdstat or "resync" in mdstat:
                    status["health"] = "rebuilding"
                
                # Extract device list
                devices_match = re.search(r'md0 : (.*)', mdstat)
                if devices_match:
                    devices_line = devices_match.group(1)
                    status["devices"] = re.findall(r'sd[a-z]\d*', devices_line)
        except Exception as e:
            status["error"] = f"Failed to read mdstat: {str(e)}"
        
        # Get capacity info
        status["capacity"] = self.get_capacity()
        
        return status
    
    def array_exists(self) -> bool:
        """Check if RAID array exists"""
        return os.path.exists(self.array_device)
    
    def get_capacity(self) -> Dict[str, int]:
        """
        Get array capacity information
        
        Returns:
            Dict with total, used, available in GB
        """
        capacity = {"total_gb": 0, "used_gb": 0, "available_gb": 0}
        
        if not self.mount_point.exists():
            return capacity
        
        try:
            # Use df to get capacity
            result = subprocess.run(
                ['df', '-BG', str(self.mount_point)],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    capacity["total_gb"] = int(parts[1].replace('G', ''))
                    capacity["used_gb"] = int(parts[2].replace('G', ''))
                    capacity["available_gb"] = int(parts[3].replace('G', ''))
        
        except Exception as e:
            capacity["error"] = f"Failed to get capacity: {str(e)}"
        
        return capacity
    
    def check_health(self) -> Dict[str, any]:
        """
        Comprehensive health check
        
        Returns:
            Dict with detailed health information
        """
        health = {
            "overall": "unknown",
            "checks": []
        }
        
        # Check if array exists
        if not self.array_exists():
            health["overall"] = "error"
            health["checks"].append({
                "name": "Array exists",
                "status": "fail",
                "message": f"Array device {self.array_device} not found"
            })
            return health
        
        health["checks"].append({
            "name": "Array exists",
            "status": "pass",
            "message": f"Array device {self.array_device} found"
        })
        
        # Check mount status
        if self.mount_point.exists():
            health["checks"].append({
                "name": "Mount point",
                "status": "pass",
                "message": f"Mounted at {self.mount_point}"
            })
        else:
            health["checks"].append({
                "name": "Mount point",
                "status": "warn",
                "message": f"Mount point {self.mount_point} not found"
            })
        
        # Check mdstat
        try:
            with open(self.mdstat_path, 'r') as f:
                mdstat = f.read()
                
                if "active raid10" in mdstat and "[UU]" in mdstat:
                    health["checks"].append({
                        "name": "RAID health",
                        "status": "pass",
                        "message": "All devices active and synced"
                    })
                    health["overall"] = "healthy"
                elif "degraded" in mdstat:
                    health["checks"].append({
                        "name": "RAID health",
                        "status": "warn",
                        "message": "Array degraded - drive failure detected"
                    })
                    health["overall"] = "degraded"
                else:
                    health["checks"].append({
                        "name": "RAID health",
                        "status": "unknown",
                        "message": "Cannot determine RAID status"
                    })
        
        except Exception as e:
            health["checks"].append({
                "name": "RAID health",
                "status": "error",
                "message": f"Failed to check: {str(e)}"
            })
        
        # Check disk space
        capacity = self.get_capacity()
        if "available_gb" in capacity and capacity["total_gb"] > 0:
            usage_percent = (capacity["used_gb"] / capacity["total_gb"]) * 100
            
            if usage_percent > 90:
                status = "warn"
                message = f"Disk usage critical: {usage_percent:.1f}%"
                if health["overall"] == "healthy":
                    health["overall"] = "warning"
            elif usage_percent > 80:
                status = "warn"
                message = f"Disk usage high: {usage_percent:.1f}%"
            else:
                status = "pass"
                message = f"Disk usage normal: {usage_percent:.1f}%"
            
            health["checks"].append({
                "name": "Disk space",
                "status": status,
                "message": message
            })
        
        return health
    
    def create_array(self, devices: List[str], raid_level: str = "10") -> Dict[str, any]:
        """
        Create RAID array (wrapper for create_raid10.sh script)
        
        Args:
            devices: List of block devices (e.g., ['/dev/sda', '/dev/sdb'])
            raid_level: RAID level (default: 10)
        
        Returns:
            Dict with creation status
        """
        # TODO: Implement by calling storage/raid/create_raid10.sh script
        # For now, return instruction to use script manually
        return {
            "status": "not_implemented",
            "message": "Use storage/raid/create_raid10.sh script to create array",
            "command": f"sudo bash storage/raid/create_raid10.sh {' '.join(devices)}"
        }
    
    def rebuild_array(self) -> Dict[str, any]:
        """
        Trigger array rebuild
        
        Returns:
            Dict with rebuild status
        """
        # TODO: Implement rebuild logic
        return {
            "status": "not_implemented",
            "message": "Rebuild functionality not yet implemented"
        }
    
    def add_device(self, device: str) -> Dict[str, any]:
        """
        Add device to array
        
        Args:
            device: Block device path (e.g., '/dev/sdc')
        
        Returns:
            Dict with operation status
        """
        try:
            # Use mdadm to add device
            result = subprocess.run(
                ['mdadm', '--manage', self.array_device, '--add', device],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "status": "success",
                "message": f"Device {device} added to array",
                "output": result.stdout
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Failed to add device: {e.stderr}",
                "returncode": e.returncode
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def remove_device(self, device: str) -> Dict[str, any]:
        """
        Remove device from array
        
        Args:
            device: Block device path (e.g., '/dev/sdc')
        
        Returns:
            Dict with operation status
        """
        try:
            # Mark device as failed first
            subprocess.run(
                ['mdadm', '--manage', self.array_device, '--fail', device],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Remove device
            result = subprocess.run(
                ['mdadm', '--manage', self.array_device, '--remove', device],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "status": "success",
                "message": f"Device {device} removed from array",
                "output": result.stdout
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Failed to remove device: {e.stderr}",
                "returncode": e.returncode
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }


# Convenience functions
def get_array_status() -> Dict[str, any]:
    """Get quick array status"""
    manager = ArrayManager()
    return manager.get_status()


def check_array_health() -> Dict[str, any]:
    """Run comprehensive health check"""
    manager = ArrayManager()
    return manager.check_health()


if __name__ == "__main__":
    # CLI usage
    import sys
    
    manager = ArrayManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            status = manager.get_status()
            print(json.dumps(status, indent=2))
        
        elif command == "health":
            health = manager.check_health()
            print(json.dumps(health, indent=2))
        
        elif command == "capacity":
            capacity = manager.get_capacity()
            print(json.dumps(capacity, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python array_manager.py [status|health|capacity]")
            sys.exit(1)
    else:
        # Default: show status
        status = manager.get_status()
        print(json.dumps(status, indent=2))

