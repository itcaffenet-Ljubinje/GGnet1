"""
Storage API Endpoints

Manage RAID arrays, ZFS pools, and storage capacity.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from db.base import get_db
from core.storage_manager import get_storage_manager
from core.safety_validator import get_safety_validator

router = APIRouter(prefix="/storage", tags=["storage"])
logger = logging.getLogger(__name__)


# Schemas
class DriveInfo(BaseModel):
    """Drive information schema"""
    device: str
    serial: str
    model: str
    capacity_gb: int
    status: str  # online, offline, failed
    position: int


class ArrayCapacity(BaseModel):
    """Array capacity schema"""
    total_gb: int
    used_gb: int
    available_gb: int
    reserved_gb: int
    reserved_percent: float


class ArrayBreakdown(BaseModel):
    """Storage breakdown schema"""
    system_images_gb: int
    game_images_gb: int
    writebacks_gb: int
    snapshots_gb: int


class ArrayStatus(BaseModel):
    """Array status schema"""
    exists: bool
    health: str  # online, offline, degraded, rebuilding
    type: str  # RAID0, RAID1, RAID10, ZFS, etc.
    devices: List[DriveInfo]
    capacity: ArrayCapacity
    breakdown: ArrayBreakdown


class DriveOperationResponse(BaseModel):
    """Drive operation response"""
    success: bool
    message: str


class AddDriveRequest(BaseModel):
    """Add drive request"""
    device: str


class ReplaceDriveRequest(BaseModel):
    """Replace drive request"""
    old_device: str
    new_device: str


class AddStripeRequest(BaseModel):
    """Add stripe request"""
    stripe_number: int
    raid_type: str = "raid10"  # raid0, raid1, raid10, mirror, raidz, raidz2
    devices: List[str] = []  # List of devices to use for stripe


class AddDriveToStripeRequest(BaseModel):
    """Add drive to stripe request"""
    device: str


class AvailableDrive(BaseModel):
    """Available drive information"""
    device: str
    size: str
    model: str
    serial: str
    capacity_gb: int


@router.get("/array/status", response_model=ArrayStatus)
async def get_array_status(db: AsyncSession = Depends(get_db)):
    """
    Get array status and health information
    
    Returns:
    - Array health (online/offline/degraded/rebuilding)
    - RAID type
    - Drive information
    - Capacity breakdown
    - Storage usage by type
    """
    try:
        # Get storage manager instance
        storage_manager = get_storage_manager()
        
        # Get array status
        status = storage_manager.get_array_status()
        
        # Convert to API response format
        return ArrayStatus(
            exists=status.exists,
            health=status.health,
            type=status.type,
            devices=[
                DriveInfo(
                    device=d.device,
                    serial=d.serial,
                    model=d.model,
                    capacity_gb=d.capacity_gb,
                    status=d.status.value,
                    position=d.position
                )
                for d in status.devices
            ],
            capacity=ArrayCapacity(
                total_gb=status.capacity.total_gb,
                used_gb=status.capacity.used_gb,
                available_gb=status.capacity.available_gb,
                reserved_gb=status.capacity.reserved_gb,
                reserved_percent=status.capacity.reserved_percent
            ),
            breakdown=ArrayBreakdown(
                system_images_gb=status.breakdown.system_images_gb,
                game_images_gb=status.breakdown.game_images_gb,
                writebacks_gb=status.breakdown.writebacks_gb,
                snapshots_gb=status.breakdown.snapshots_gb
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to get array status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get array status: {str(e)}")


@router.post("/array/drives/add", response_model=DriveOperationResponse)
async def add_drive(
    request: AddDriveRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new drive to the array
    
    Args:
        request: AddDriveRequest containing device name
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        
        success = storage_manager.add_drive(request.device)
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Drive {request.device} added successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to add drive {request.device}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding drive {request.device}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding drive: {str(e)}"
        )


@router.post("/array/drives/remove", response_model=DriveOperationResponse)
async def remove_drive(
    device: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a drive from the array
    
    Args:
        device: Device name (e.g., "sda")
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        
        success = storage_manager.remove_drive(device)
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Drive {device} removed successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to remove drive {device}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing drive {device}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error removing drive: {str(e)}"
        )


@router.post("/array/drives/replace", response_model=DriveOperationResponse)
async def replace_drive(
    request: ReplaceDriveRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Replace a failed drive with a new one
    
    Args:
        request: ReplaceDriveRequest containing old and new device names
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        
        success = storage_manager.replace_drive(
            request.old_device,
            request.new_device
        )
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Drive {request.old_device} replaced with {request.new_device} successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to replace drive {request.old_device} with {request.new_device}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replacing drive: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error replacing drive: {str(e)}"
        )


@router.post("/array/drives/{device}/offline", response_model=DriveOperationResponse)
async def bring_drive_offline(
    device: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Bring a drive offline
    
    Args:
        device: Device name (e.g., "sda")
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        
        success = storage_manager.bring_drive_offline(device)
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Drive {device} brought offline successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to bring drive {device} offline"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bringing drive {device} offline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error bringing drive offline: {str(e)}"
        )


@router.post("/array/drives/{device}/online", response_model=DriveOperationResponse)
async def bring_drive_online(
    device: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Bring a drive online
    
    Args:
        device: Device name (e.g., "sda")
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        
        success = storage_manager.bring_drive_online(device)
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Drive {device} brought online successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to bring drive {device} online"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bringing drive {device} online: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error bringing drive online: {str(e)}"
        )


@router.post("/array/stripes", response_model=DriveOperationResponse)
async def add_stripe(
    request: AddStripeRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new stripe to the array
    
    Args:
        request: AddStripeRequest containing stripe number
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        safety_validator = get_safety_validator()
        
        # Validate stripe number
        is_valid, error_msg = safety_validator.validate_stripe_number(request.stripe_number)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate RAID type
        is_valid, error_msg = safety_validator.validate_raid_type(request.raid_type, len(request.devices))
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate devices
        is_valid, error_msg = safety_validator.validate_devices(request.devices)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Log operation for audit
        logger.warning(f"🔶 Creating stripe {request.stripe_number} with {request.raid_type} on devices: {request.devices}")
        
        # Add stripe using storage manager
        success = storage_manager.add_stripe(request.stripe_number, request.raid_type, request.devices)
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Stripe {request.stripe_number} added successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to add stripe {request.stripe_number}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stripe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding stripe: {str(e)}"
        )


@router.get("/array/available-drives", response_model=List[AvailableDrive])
async def get_available_drives(db: AsyncSession = Depends(get_db)):
    """
    Get list of available drives not currently in the array
    
    Returns:
        List of available drives with device info
    """
    try:
        storage_manager = get_storage_manager()
        
        # Get available drives
        drives = storage_manager.get_available_drives()
        
        # Convert to API response format
        return [
            AvailableDrive(
                device=d['device'],
                size=d['size'],
                model=d['model'],
                serial=d['serial'],
                capacity_gb=d['capacity_gb']
            )
            for d in drives
        ]
        
    except Exception as e:
        logger.error(f"Error getting available drives: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available drives: {str(e)}"
        )


@router.post("/array/stripes/{stripe}/drives", response_model=DriveOperationResponse)
async def add_drive_to_stripe(
    stripe: str,
    request: AddDriveToStripeRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a drive to a specific stripe
    
    Args:
        stripe: Stripe identifier
        request: AddDriveToStripeRequest containing device name
        
    Returns:
        DriveOperationResponse with success status
    """
    try:
        storage_manager = get_storage_manager()
        
        # Validate device name
        if not request.device or not request.device.startswith('sd'):
            raise HTTPException(
                status_code=400,
                detail="Invalid device name. Must start with 'sd' (e.g., sda, sdb)"
            )
        
        # Add drive to stripe using storage manager
        success = storage_manager.add_drive_to_stripe(stripe, request.device)
        
        if success:
            return DriveOperationResponse(
                success=True,
                message=f"Drive {request.device} added to stripe {stripe} successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to add drive {request.device} to stripe {stripe}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding drive to stripe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding drive to stripe: {str(e)}"
        )

