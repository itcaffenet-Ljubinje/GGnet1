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

