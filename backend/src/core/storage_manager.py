"""
Storage Manager Module

Handles RAID array and ZFS pool management operations.
"""

import subprocess
import re
import logging
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Dry-run mode for testing (set GGNET_DRY_RUN=true to enable)
DRY_RUN = os.environ.get('GGNET_DRY_RUN', 'false').lower() == 'true'

if DRY_RUN:
    logger.warning("🔶 DRY RUN MODE ENABLED - No actual commands will be executed!")
else:
    logger.info("✅ Live mode - Commands will be executed")


class ArrayType(Enum):
    """Array type enumeration"""
    MD_RAID = "mdraid"
    ZFS = "zfs"
    LVM = "lvm"
    UNKNOWN = "unknown"


class DriveStatus(Enum):
    """Drive status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    FAILED = "failed"
    SPARE = "spare"
    UNKNOWN = "unknown"


@dataclass
class DriveInfo:
    """Drive information"""
    device: str
    serial: str
    model: str
    capacity_gb: int
    status: DriveStatus
    position: int
    health: Optional[str] = None


@dataclass
class ArrayCapacity:
    """Array capacity information"""
    total_gb: int
    used_gb: int
    available_gb: int
    reserved_gb: int
    reserved_percent: float


@dataclass
class ArrayBreakdown:
    """Storage breakdown by type"""
    system_images_gb: int
    game_images_gb: int
    writebacks_gb: int
    snapshots_gb: int


@dataclass
class ArrayStatus:
    """Complete array status"""
    exists: bool
    health: str  # online, offline, degraded, rebuilding
    type: str
    devices: List[DriveInfo]
    capacity: ArrayCapacity
    breakdown: ArrayBreakdown
    array_type: ArrayType


class StorageManager:
    """Manages storage arrays (RAID/ZFS)"""
    
    def __init__(self):
        self.array_type = self._detect_array_type()
        self.array_name = self._get_array_name()
    
    def _run_command(self, cmd: List[str], dry_run_msg: str = None, check: bool = True, timeout: int = 10) -> subprocess.CompletedProcess:
        """
        Execute a command with dry-run support
        
        Args:
            cmd: Command to execute
            dry_run_msg: Message to log in dry-run mode
            check: Raise exception on failure
            timeout: Command timeout
            
        Returns:
            CompletedProcess result (or mock in dry-run mode)
        """
        if DRY_RUN:
            msg = dry_run_msg or f"Would execute: {' '.join(cmd)}"
            logger.warning(f"[DRY RUN] {msg}")
            # Return mock success
            from unittest.mock import Mock
            return Mock(returncode=0, stdout='', stderr='')
        else:
            return subprocess.run(cmd, capture_output=True, text=True, check=check, timeout=timeout)
    
    def _detect_array_type(self) -> ArrayType:
        """Detect array type (MD RAID, ZFS, LVM)"""
        try:
            # Check for MD RAID
            result = subprocess.run(
                ['mdadm', '--detail', '--scan'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                logger.info("Detected MD RAID array")
                return ArrayType.MD_RAID
            
            # Check for ZFS
            result = subprocess.run(
                ['zpool', 'list', '-H'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                logger.info("Detected ZFS pool")
                return ArrayType.ZFS
            
            # Check for LVM
            result = subprocess.run(
                ['vgs', '--noheadings', '-o', 'vg_name'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                logger.info("Detected LVM volume group")
                return ArrayType.LVM
            
            logger.warning("No storage array detected")
            return ArrayType.UNKNOWN
            
        except FileNotFoundError as e:
            logger.error(f"Storage management tool not found: {e}")
            return ArrayType.UNKNOWN
        except subprocess.TimeoutExpired:
            logger.error("Storage detection timeout")
            return ArrayType.UNKNOWN
        except Exception as e:
            logger.error(f"Error detecting array type: {e}")
            return ArrayType.UNKNOWN
    
    def _get_array_name(self) -> Optional[str]:
        """Get array/pool name"""
        if self.array_type == ArrayType.MD_RAID:
            try:
                result = subprocess.run(
                    ['mdadm', '--detail', '--scan'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Parse: ARRAY /dev/md0 level=raid1 num-devices=2
                    match = re.search(r'ARRAY\s+(\S+)', result.stdout)
                    if match:
                        return match.group(1)
            except Exception as e:
                logger.error(f"Error getting MD RAID name: {e}")
        
        elif self.array_type == ArrayType.ZFS:
            try:
                result = subprocess.run(
                    ['zpool', 'list', '-H', '-o', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    pools = result.stdout.strip().split('\n')
                    if pools:
                        return pools[0]  # Return first pool
            except Exception as e:
                logger.error(f"Error getting ZFS pool name: {e}")
        
        elif self.array_type == ArrayType.LVM:
            try:
                result = subprocess.run(
                    ['vgs', '--noheadings', '-o', 'vg_name'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    vgs = result.stdout.strip().split('\n')
                    if vgs:
                        return vgs[0].strip()  # Return first VG
            except Exception as e:
                logger.error(f"Error getting LVM VG name: {e}")
        
        return None
    
    def get_array_status(self) -> ArrayStatus:
        """Get complete array status"""
        if self.array_type == ArrayType.UNKNOWN or not self.array_name:
            return self._get_empty_status()
        
        try:
            if self.array_type == ArrayType.MD_RAID:
                return self._get_mdraid_status()
            elif self.array_type == ArrayType.ZFS:
                return self._get_zfs_status()
            elif self.array_type == ArrayType.LVM:
                return self._get_lvm_status()
        except Exception as e:
            logger.error(f"Error getting array status: {e}")
            return self._get_empty_status()
    
    def _get_empty_status(self) -> ArrayStatus:
        """Return empty status when no array is detected"""
        return ArrayStatus(
            exists=False,
            health="offline",
            type="N/A",
            devices=[],
            capacity=ArrayCapacity(
                total_gb=0,
                used_gb=0,
                available_gb=0,
                reserved_gb=0,
                reserved_percent=0
            ),
            breakdown=ArrayBreakdown(
                system_images_gb=0,
                game_images_gb=0,
                writebacks_gb=0,
                snapshots_gb=0
            ),
            array_type=ArrayType.UNKNOWN
        )
    
    def _get_mdraid_status(self) -> ArrayStatus:
        """Get MD RAID status"""
        # Get array details
        result = subprocess.run(
            ['mdadm', '--detail', self.array_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to get MD RAID details: {result.stderr}")
            return self._get_empty_status()
        
        # Parse RAID level
        raid_level = "RAID1"  # Default
        match = re.search(r'Raid Level :\s+(\S+)', result.stdout)
        if match:
            raid_level = match.group(1)
        
        # Parse state
        health = "online"
        match = re.search(r'State :\s+(\S+)', result.stdout)
        if match:
            state = match.group(1).lower()
            if 'degraded' in state or 'rebuilding' in state:
                health = "degraded"
            elif 'clean' in state or 'active' in state:
                health = "online"
            else:
                health = "offline"
        
        # Get devices
        devices = self._get_mdraid_devices()
        
        # Get capacity
        capacity = self._get_mdraid_capacity()
        
        # Get breakdown (mock for now)
        breakdown = self._get_storage_breakdown()
        
        return ArrayStatus(
            exists=True,
            health=health,
            type=raid_level,
            devices=devices,
            capacity=capacity,
            breakdown=breakdown,
            array_type=ArrayType.MD_RAID
        )
    
    def _get_mdraid_devices(self) -> List[DriveInfo]:
        """Get MD RAID device information"""
        devices = []
        
        try:
            # Get detailed device information
            result = subprocess.run(
                ['mdadm', '--detail', self.array_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return devices
            
            # Parse device list
            lines = result.stdout.split('\n')
            position = 0
            for line in lines:
                if line.strip().startswith('/dev/'):
                    # Extract device name
                    parts = line.split()
                    device = parts[0].split('/')[-1]
                    
                    # Get device status
                    status = DriveStatus.ONLINE
                    if 'faulty' in line or 'removed' in line:
                        status = DriveStatus.FAILED
                    elif 'spare' in line:
                        status = DriveStatus.SPARE
                    
                    # Get device info
                    device_info = self._get_device_info(device)
                    
                    devices.append(DriveInfo(
                        device=device,
                        serial=device_info['serial'],
                        model=device_info['model'],
                        capacity_gb=device_info['capacity_gb'],
                        status=status,
                        position=position,
                        health=device_info.get('health')
                    ))
                    position += 1
        
        except Exception as e:
            logger.error(f"Error getting MD RAID devices: {e}")
        
        return devices
    
    def _get_zfs_status(self) -> ArrayStatus:
        """Get ZFS pool status"""
        # Get pool status
        result = subprocess.run(
            ['zpool', 'status', self.array_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to get ZFS status: {result.stderr}")
            return self._get_empty_status()
        
        # Parse health
        health = "online"
        match = re.search(r'state:\s+(\S+)', result.stdout)
        if match:
            state = match.group(1).lower()
            if 'degraded' in state or 'resilver' in state:
                health = "degraded"
            elif 'online' in state:
                health = "online"
            else:
                health = "offline"
        
        # Get devices (pass the status output to avoid re-running subprocess)
        devices = self._get_zfs_devices_from_status(result.stdout)
        
        # Get capacity
        capacity = self._get_zfs_capacity()
        
        # Get breakdown
        breakdown = self._get_storage_breakdown()
        
        return ArrayStatus(
            exists=True,
            health=health,
            type="ZFS",
            devices=devices,
            capacity=capacity,
            breakdown=breakdown,
            array_type=ArrayType.ZFS
        )
    
    def _get_zfs_devices(self) -> List[DriveInfo]:
        """Get ZFS device information"""
        devices = []
        
        try:
            # Get pool status
            result = subprocess.run(
                ['zpool', 'status', self.array_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return devices
            
            devices = self._get_zfs_devices_from_status(result.stdout)
        
        except Exception as e:
            logger.error(f"Error getting ZFS devices: {e}")
        
        return devices
    
    def _get_zfs_devices_from_status(self, status_output: str) -> List[DriveInfo]:
        """Parse ZFS devices from status output"""
        devices = []
        
        try:
            # Parse device list
            lines = status_output.split('\n')
            position = 0
            in_config_section = False
            
            for line in lines:
                # Start parsing after "config:" line
                if 'config:' in line.lower():
                    in_config_section = True
                    continue
                
                if not in_config_section:
                    continue
                
                # Skip header line (NAME STATE READ WRITE CKSUM)
                if 'NAME' in line and 'STATE' in line:
                    continue
                
                # Look for device lines (starts with whitespace and device name)
                stripped = line.strip()
                if not stripped or stripped.startswith('pool') or 'mirror' in stripped or 'raidz' in stripped:
                    continue
                
                # Check if line contains a device (sd*, nvme*, etc.)
                parts = stripped.split()
                if len(parts) >= 2:
                    device_name = parts[0]
                    
                    # Check if it's a physical device (not a pool or vdev)
                    if device_name.startswith('sd') or device_name.startswith('nvme') or device_name.startswith('hd'):
                        # Get device status
                        status = DriveStatus.ONLINE
                        device_state = parts[1] if len(parts) > 1 else 'ONLINE'
                        
                        if 'FAULTED' in device_state or 'REMOVED' in device_state:
                            status = DriveStatus.FAILED
                        elif 'OFFLINE' in device_state:
                            status = DriveStatus.OFFLINE
                        elif 'SPARE' in device_state:
                            status = DriveStatus.SPARE
                        
                        # Get device info
                        device_info = self._get_device_info(device_name)
                        
                        devices.append(DriveInfo(
                            device=device_name,
                            serial=device_info['serial'],
                            model=device_info['model'],
                            capacity_gb=device_info['capacity_gb'],
                            status=status,
                            position=position,
                            health=device_info.get('health')
                        ))
                        position += 1
        
        except Exception as e:
            logger.error(f"Error parsing ZFS devices: {e}")
        
        return devices
    
    def _get_lvm_status(self) -> ArrayStatus:
        """Get LVM status"""
        # Mock implementation for LVM
        logger.warning("LVM status not fully implemented")
        return self._get_empty_status()
    
    def _get_device_info(self, device: str) -> Dict:
        """Get device information using lsblk and smartctl"""
        info = {
            'serial': 'Unknown',
            'model': 'Unknown',
            'capacity_gb': 0,
            'health': None
        }
        
        try:
            # Get device info using lsblk
            result = subprocess.run(
                ['lsblk', '-d', '-n', '-o', 'SIZE,MODEL,SERIAL', f'/dev/{device}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                if len(parts) >= 3:
                    # Parse size (e.g., "1.8T" -> 1800 GB)
                    size_str = parts[0]
                    if 'T' in size_str:
                        size_gb = int(float(size_str.replace('T', '')) * 1000)
                    elif 'G' in size_str:
                        size_gb = int(float(size_str.replace('G', '')))
                    else:
                        size_gb = 0
                    
                    info['capacity_gb'] = size_gb
                    info['model'] = ' '.join(parts[1:-1]) if len(parts) > 2 else 'Unknown'
                    info['serial'] = parts[-1] if len(parts) > 1 else 'Unknown'
        
        except Exception as e:
            logger.error(f"Error getting device info for {device}: {e}")
        
        return info
    
    def _get_mdraid_capacity(self) -> ArrayCapacity:
        """Get MD RAID capacity"""
        try:
            # Get array size
            result = subprocess.run(
                ['mdadm', '--detail', self.array_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return ArrayCapacity(0, 0, 0, 0, 0)
            
            # Parse array size
            match = re.search(r'Array Size :\s+(\d+)', result.stdout)
            if match:
                # Array size is in KB, convert to GB
                size_kb = int(match.group(1))
                total_gb = size_kb // (1024 * 1024)
            else:
                total_gb = 0
            
            # Get usage from df
            used_gb = self._get_usage_gb()
            available_gb = total_gb - used_gb
            
            # Reserved space (15% default)
            reserved_percent = 15.0
            reserved_gb = int(total_gb * (reserved_percent / 100))
            
            return ArrayCapacity(
                total_gb=total_gb,
                used_gb=used_gb,
                available_gb=available_gb,
                reserved_gb=reserved_gb,
                reserved_percent=reserved_percent
            )
        
        except Exception as e:
            logger.error(f"Error getting MD RAID capacity: {e}")
            return ArrayCapacity(0, 0, 0, 0, 0)
    
    def _get_zfs_capacity(self) -> ArrayCapacity:
        """Get ZFS capacity"""
        try:
            # Get pool capacity
            result = subprocess.run(
                ['zpool', 'list', '-H', '-o', 'size,allocated,free', self.array_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return ArrayCapacity(0, 0, 0, 0, 0)
            
            parts = result.stdout.strip().split()
            if len(parts) >= 3:
                # Parse sizes (e.g., "1.8T" -> 1800 GB)
                def parse_size(size_str: str) -> int:
                    try:
                        if 'T' in size_str:
                            return int(float(size_str.replace('T', '')) * 1000)
                        elif 'G' in size_str:
                            return int(float(size_str.replace('G', '')))
                        return 0
                    except (ValueError, AttributeError):
                        return 0
                
                total_gb = parse_size(parts[0])
                used_gb = parse_size(parts[1])
                available_gb = parse_size(parts[2])
                
                # Reserved space
                reserved_percent = 15.0
                reserved_gb = int(total_gb * (reserved_percent / 100))
                
                return ArrayCapacity(
                    total_gb=total_gb,
                    used_gb=used_gb,
                    available_gb=available_gb,
                    reserved_gb=reserved_gb,
                    reserved_percent=reserved_percent
                )
        
        except Exception as e:
            logger.error(f"Error getting ZFS capacity: {e}")
        
        return ArrayCapacity(0, 0, 0, 0, 0)
    
    def _get_usage_gb(self) -> int:
        """Get actual disk usage in GB"""
        try:
            # Get usage from df
            result = subprocess.run(
                ['df', '-BG', self.array_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 3:
                        used_str = parts[2].replace('G', '')
                        return int(used_str)
        
        except Exception as e:
            logger.error(f"Error getting usage: {e}")
        
        return 0
    
    def _get_storage_breakdown(self) -> ArrayBreakdown:
        """Get storage breakdown by type (mock implementation)"""
        # TODO: Implement actual breakdown calculation
        return ArrayBreakdown(
            system_images_gb=0,
            game_images_gb=0,
            writebacks_gb=0,
            snapshots_gb=0
        )
    
    def bring_drive_offline(self, device: str) -> bool:
        """Bring a drive offline"""
        try:
            if self.array_type == ArrayType.MD_RAID:
                # Mark drive as faulty
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--fail', f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} marked as faulty in MD RAID")
            
            elif self.array_type == ArrayType.ZFS:
                # Offline drive in ZFS
                subprocess.run(
                    ['zpool', 'offline', self.array_name, f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} taken offline in ZFS pool")
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to bring drive {device} offline: {e}")
            return False
        except Exception as e:
            logger.error(f"Error bringing drive {device} offline: {e}")
            return False
    
    def bring_drive_online(self, device: str) -> bool:
        """Bring a drive online"""
        try:
            if self.array_type == ArrayType.MD_RAID:
                # Remove and re-add drive
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--remove', f'/dev/{device}'],
                    check=False,
                    timeout=10
                )
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--add', f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} brought online in MD RAID")
            
            elif self.array_type == ArrayType.ZFS:
                # Online drive in ZFS
                subprocess.run(
                    ['zpool', 'online', self.array_name, f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} brought online in ZFS pool")
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to bring drive {device} online: {e}")
            return False
        except Exception as e:
            logger.error(f"Error bringing drive {device} online: {e}")
            return False
    
    def add_drive(self, device: str) -> bool:
        """Add a drive to the array"""
        try:
            if self.array_type == ArrayType.MD_RAID:
                # Add drive to MD RAID array
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--add', f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} added to MD RAID")
            
            elif self.array_type == ArrayType.ZFS:
                # Add drive to ZFS pool
                subprocess.run(
                    ['zpool', 'add', self.array_name, f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} added to ZFS pool")
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add drive {device}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error adding drive {device}: {e}")
            return False
    
    def add_stripe(self, stripe_number: int, raid_type: str = "raid10", devices: List[str] = None) -> bool:
        """Add a new stripe to the array"""
        try:
            if self.array_type == ArrayType.ZFS:
                # For ZFS, we create a new vdev (virtual device)
                logger.info(f"Creating ZFS stripe {stripe_number}")
                
                if devices is None or len(devices) == 0:
                    logger.error("No devices provided for ZFS stripe creation")
                    return False
                
                # Create ZFS pool with specified vdev type
                if raid_type == "mirror":
                    # Create mirror vdev
                    cmd = ['zpool', 'create', f'pool{stripe_number}', 'mirror'] + [f'/dev/{d}' for d in devices]
                elif raid_type == "raidz":
                    # Create raidz vdev
                    cmd = ['zpool', 'create', f'pool{stripe_number}', 'raidz'] + [f'/dev/{d}' for d in devices]
                elif raid_type == "raidz2":
                    # Create raidz2 vdev
                    cmd = ['zpool', 'create', f'pool{stripe_number}', 'raidz2'] + [f'/dev/{d}' for d in devices]
                else:
                    # Default to stripe (RAID0)
                    cmd = ['zpool', 'create', f'pool{stripe_number}'] + [f'/dev/{d}' for d in devices]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
                logger.info(f"ZFS stripe {stripe_number} created successfully: {result.stdout}")
                return True
            
            elif self.array_type == ArrayType.MD_RAID:
                # For MD RAID, we create a new RAID array
                logger.info(f"Creating MD RAID stripe {stripe_number}")
                
                if devices is None or len(devices) == 0:
                    logger.error("No devices provided for MD RAID stripe creation")
                    return False
                
                array_name = f'/dev/md{stripe_number}'
                
                # Create MD RAID array
                if raid_type == "raid0":
                    cmd = ['mdadm', '--create', array_name, '--level=0', '--raid-devices=' + str(len(devices))] + [f'/dev/{d}' for d in devices]
                elif raid_type == "raid1":
                    cmd = ['mdadm', '--create', array_name, '--level=1', '--raid-devices=' + str(len(devices))] + [f'/dev/{d}' for d in devices]
                elif raid_type == "raid10":
                    cmd = ['mdadm', '--create', array_name, '--level=10', '--raid-devices=' + str(len(devices))] + [f'/dev/{d}' for d in devices]
                else:
                    logger.error(f"Unsupported RAID type: {raid_type}")
                    return False
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
                logger.info(f"MD RAID stripe {stripe_number} created successfully: {result.stdout}")
                return True
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create stripe {stripe_number}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to add stripe {stripe_number}: {e}")
            return False
    
    def add_drive_to_stripe(self, stripe: str, device: str) -> bool:
        """Add a drive to a specific stripe"""
        try:
            if self.array_type == ArrayType.ZFS:
                # Add drive to ZFS pool as a vdev
                subprocess.run(
                    ['zpool', 'add', self.array_name, f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} added to ZFS pool")
            
            elif self.array_type == ArrayType.MD_RAID:
                # Add drive to MD RAID array
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--add', f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} added to MD RAID")
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add drive {device} to stripe {stripe}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error adding drive {device}: {e}")
            return False
    
    def get_available_drives(self) -> List[Dict[str, any]]:
        """Get list of available drives not in the array"""
        try:
            available_drives = []
            
            # Get all block devices
            result = subprocess.run(
                ['lsblk', '-d', '-n', '-o', 'NAME,SIZE,MODEL,SERIAL,TYPE'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error("Failed to get block devices")
                return available_drives
            
            # Get drives currently in array
            array_drives = set()
            if self.array_type == ArrayType.ZFS and self.array_name:
                # Get ZFS pool devices
                zpool_result = subprocess.run(
                    ['zpool', 'status', self.array_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if zpool_result.returncode == 0:
                    for line in zpool_result.stdout.split('\n'):
                        if '/dev/' in line:
                            device = line.split('/dev/')[-1].split()[0]
                            array_drives.add(device)
            
            elif self.array_type == ArrayType.MD_RAID and self.array_name:
                # Get MD RAID devices
                md_result = subprocess.run(
                    ['mdadm', '--detail', self.array_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if md_result.returncode == 0:
                    for line in md_result.stdout.split('\n'):
                        if '/dev/' in line and 'active' in line:
                            device = line.split('/dev/')[-1].split()[0]
                            array_drives.add(device)
            
            # Parse lsblk output and filter available drives
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    size = parts[1]
                    drive_type = parts[-1]
                    
                    # Only include disks (not partitions or other devices)
                    if drive_type == 'disk' and name not in array_drives:
                        # Get detailed info
                        device_info = self._get_device_info(name)
                        
                        available_drives.append({
                            'device': name,
                            'size': size,
                            'model': device_info.get('model', 'Unknown'),
                            'serial': device_info.get('serial', 'Unknown'),
                            'capacity_gb': device_info.get('capacity_gb', 0)
                        })
            
            return available_drives
        
        except Exception as e:
            logger.error(f"Error getting available drives: {e}")
            return []
    
    def remove_drive(self, device: str) -> bool:
        """Remove a drive from the array"""
        try:
            if self.array_type == ArrayType.MD_RAID:
                # Remove drive from MD RAID
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--remove', f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} removed from MD RAID")
            
            elif self.array_type == ArrayType.ZFS:
                # Remove drive from ZFS pool
                subprocess.run(
                    ['zpool', 'remove', self.array_name, f'/dev/{device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {device} removed from ZFS pool")
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove drive {device}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error removing drive {device}: {e}")
            return False
    
    def replace_drive(self, old_device: str, new_device: str) -> bool:
        """Replace a failed drive with a new one"""
        try:
            if self.array_type == ArrayType.MD_RAID:
                # Remove old drive
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--remove', f'/dev/{old_device}'],
                    check=False,
                    timeout=10
                )
                # Add new drive
                subprocess.run(
                    ['mdadm', '--manage', self.array_name, '--add', f'/dev/{new_device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {old_device} replaced with {new_device} in MD RAID")
            
            elif self.array_type == ArrayType.ZFS:
                # Replace drive in ZFS pool
                subprocess.run(
                    ['zpool', 'replace', self.array_name, f'/dev/{old_device}', f'/dev/{new_device}'],
                    check=True,
                    timeout=10
                )
                logger.info(f"Drive {old_device} replaced with {new_device} in ZFS pool")
            
            else:
                logger.error(f"Unsupported array type: {self.array_type}")
                return False
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to replace drive {old_device} with {new_device}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error replacing drive {old_device} with {new_device}: {e}")
            return False


# Global storage manager instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """Get or create storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager

