"""
Storage API Endpoints

Manage RAID arrays, ZFS pools, and storage capacity.
"""

from fastapi import APIRouter, Depends, HTTPException
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
        # TODO: Implement actual array detection and status checking
        # For now, return mock data based on ggNet specifications
        
        # Check if array exists (mock check)
        array_exists = True  # TODO: Check actual array status
        
        if not array_exists:
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
                )
            )
        
        # Mock drive data (Micron 5200 ECO 1.92TB - ggNet recommended)
        devices = [
            DriveInfo(
                device="sda",
                serial="S3Z1NX0K123456",
                model="Micron 5200 ECO 1.92TB",
                capacity_gb=1920,
                status="online",
                position=1
            ),
            DriveInfo(
                device="sdb",
                serial="S3Z1NX0K123457",
                model="Micron 5200 ECO 1.92TB",
                capacity_gb=1920,
                status="online",
                position=2
            ),
            DriveInfo(
                device="sdc",
                serial="S3Z1NX0K123458",
                model="Micron 5200 ECO 1.92TB",
                capacity_gb=1920,
                status="online",
                position=3
            ),
            DriveInfo(
                device="sdd",
                serial="S3Z1NX0K123459",
                model="Micron 5200 ECO 1.92TB",
                capacity_gb=1920,
                status="online",
                position=4
            ),
        ]
        
        # Calculate capacity (RAID10 with 4 drives)
        total_raw_gb = sum(d.capacity_gb for d in devices)
        total_gb = total_raw_gb // 2  # RAID10 = 50% usable capacity
        
        # Mock usage data
        used_gb = 1450
        reserved_percent = 16.25
        reserved_gb = int(total_gb * (reserved_percent / 100))
        available_gb = total_gb - used_gb - reserved_gb
        
        # Mock breakdown
        breakdown = ArrayBreakdown(
            system_images_gb=800,
            game_images_gb=450,
            writebacks_gb=120,
            snapshots_gb=80
        )
        
        return ArrayStatus(
            exists=True,
            health="online",
            type="RAID10",
            devices=devices,
            capacity=ArrayCapacity(
                total_gb=total_gb,
                used_gb=used_gb,
                available_gb=available_gb,
                reserved_gb=reserved_gb,
                reserved_percent=reserved_percent
            ),
            breakdown=breakdown
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get array status: {str(e)}")


@router.post("/array/drives/add")
async def add_drive_to_array(
    device: str,
    stripe_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a drive to the array
    
    Args:
        device: Device name (e.g., "sde")
        stripe_id: Stripe ID to add the drive to
    
    Note: Drive must have capacity larger than largest drive in array
    """
    # TODO: Implement actual drive addition
    return {
        "success": True,
        "message": f"Drive {device} added to stripe {stripe_id}",
        "status": "rebuilding"
    }


@router.post("/array/drives/remove")
async def remove_drive_from_array(
    device: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a drive from the array
    
    Args:
        device: Device name (e.g., "sda")
    
    Note: RAID0 arrays cannot remove single drives
    """
    # TODO: Implement actual drive removal
    return {
        "success": True,
        "message": f"Drive {device} removed from array",
        "status": "rebuilding"
    }


@router.post("/array/drives/replace")
async def replace_drive(
    old_device: str,
    new_device: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Replace a failed drive with a new one
    
    Args:
        old_device: Device name to replace (e.g., "sda")
        new_device: New device name (e.g., "sde")
    """
    # TODO: Implement actual drive replacement
    return {
        "success": True,
        "message": f"Drive {old_device} replaced with {new_device}",
        "status": "rebuilding"
    }


@router.post("/array/drives/{device}/offline")
async def bring_drive_offline(
    device: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Bring a drive offline
    
    Args:
        device: Device name (e.g., "sda")
    """
    # TODO: Implement actual drive offline
    return {
        "success": True,
        "message": f"Drive {device} brought offline"
    }


@router.post("/array/drives/{device}/online")
async def bring_drive_online(
    device: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Bring a drive online
    
    Args:
        device: Device name (e.g., "sda")
    """
    # TODO: Implement actual drive online
    return {
        "success": True,
        "message": f"Drive {device} brought online",
        "status": "rebuilding"
    }

