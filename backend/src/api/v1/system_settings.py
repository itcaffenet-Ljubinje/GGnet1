"""
Settings API Endpoints

Manage system settings including RAM, Array, and Retention settings.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from db.base import get_db
from core.cleanup import trigger_cleanup

router = APIRouter(prefix="/settings", tags=["settings"])


# Schemas
class RAMSettings(BaseModel):
    """RAM settings schema"""
    maximize_size: bool = True
    ram_cache_size_mb: int = 0  # 0 = auto
    max_ram_for_vms_mb: int = 0  # 0 = auto
    server_reserved_mb: int = 4096


class ArraySettings(BaseModel):
    """Array settings schema (ggNet compatible)"""
    reserved_disk_space_percent: int = 15  # Recommended: 15%
    warning_threshold_percent: int = 85  # Alert threshold


class RetentionSettings(BaseModel):
    """Snapshots and Writebacks retention settings (ggNet compatible)"""
    unutilized_snapshots_days: int = 30
    unprotected_snapshots_count: int = 5
    inactive_writebacks_hours: int = 168  # 7 days


class GeneralSettings(BaseModel):
    """General settings schema"""
    system_name: str = "ggNet Server"
    timezone: str = "UTC"
    auto_updates: bool = False
    dark_mode: bool = False
    release_stream: str = "prod"


class StorageSettings(BaseModel):
    """Storage settings schema"""
    cache_size_mb: int = 51200
    image_compression: bool = True
    auto_cleanup_days: int = 30


class PerformanceSettings(BaseModel):
    """Performance settings schema"""
    max_concurrent_boots: int = 50
    writeback_cache_mb: int = 2048
    snapshot_retention_days: int = 90


class SecuritySettings(BaseModel):
    """Security settings schema"""
    require_auth: bool = False
    api_rate_limit: int = 1000
    enable_https: bool = False


class NotificationSettings(BaseModel):
    """Notification settings schema"""
    email_alerts: bool = False
    slack_webhook: str = ""
    disk_alert_threshold: int = 90


class AllSettings(BaseModel):
    """All settings schema"""
    general: GeneralSettings
    ram: RAMSettings
    array: ArraySettings
    retention: RetentionSettings
    storage: StorageSettings
    performance: PerformanceSettings
    security: SecuritySettings
    notifications: NotificationSettings


# Default settings
DEFAULT_SETTINGS = AllSettings(
    general=GeneralSettings(),
    ram=RAMSettings(),
    array=ArraySettings(),
    retention=RetentionSettings(),
    storage=StorageSettings(),
    performance=PerformanceSettings(),
    security=SecuritySettings(),
    notifications=NotificationSettings()
)


@router.get("/", response_model=AllSettings)
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """
    Get all system settings
    
    Returns:
    - General settings
    - RAM settings
    - Array settings
    - Retention settings
    - Storage settings
    - Performance settings
    - Security settings
    - Notification settings
    """
    try:
        # TODO: Load settings from database or config file
        # For now, return default settings
        return DEFAULT_SETTINGS
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.get("/general", response_model=GeneralSettings)
async def get_general_settings(db: AsyncSession = Depends(get_db)):
    """Get general settings"""
    try:
        # TODO: Load from database
        return DEFAULT_SETTINGS.general
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get general settings: {str(e)}")


@router.get("/ram", response_model=RAMSettings)
async def get_ram_settings(db: AsyncSession = Depends(get_db)):
    """Get RAM settings"""
    try:
        # TODO: Load from database
        return DEFAULT_SETTINGS.ram
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get RAM settings: {str(e)}")


@router.get("/array", response_model=ArraySettings)
async def get_array_settings(db: AsyncSession = Depends(get_db)):
    """Get array settings (ggNet compatible)"""
    try:
        # TODO: Load from database
        return DEFAULT_SETTINGS.array
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get array settings: {str(e)}")


@router.get("/retention", response_model=RetentionSettings)
async def get_retention_settings(db: AsyncSession = Depends(get_db)):
    """Get retention settings (ggNet compatible)"""
    try:
        # TODO: Load from database
        return DEFAULT_SETTINGS.retention
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get retention settings: {str(e)}")


@router.put("/", response_model=AllSettings)
async def update_all_settings(
    settings: AllSettings,
    db: AsyncSession = Depends(get_db)
):
    """
    Update all system settings
    
    Args:
        settings: All settings to update
    
    Returns:
        Updated settings
    """
    try:
        # TODO: Save settings to database or config file
        # For now, just return the updated settings
        return settings
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.put("/general", response_model=GeneralSettings)
async def update_general_settings(
    settings: GeneralSettings,
    db: AsyncSession = Depends(get_db)
):
    """Update general settings"""
    try:
        # TODO: Save to database
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update general settings: {str(e)}")


@router.put("/ram", response_model=RAMSettings)
async def update_ram_settings(
    settings: RAMSettings,
    db: AsyncSession = Depends(get_db)
):
    """Update RAM settings"""
    try:
        # TODO: Save to database
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update RAM settings: {str(e)}")


@router.put("/array", response_model=ArraySettings)
async def update_array_settings(
    settings: ArraySettings,
    db: AsyncSession = Depends(get_db)
):
    """Update array settings (ggNet compatible)"""
    try:
        # TODO: Save to database
        # TODO: Validate settings (e.g., reserved_disk_space_percent >= 15)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update array settings: {str(e)}")


@router.put("/retention", response_model=RetentionSettings)
async def update_retention_settings(
    settings: RetentionSettings,
    db: AsyncSession = Depends(get_db)
):
    """Update retention settings (ggNet compatible)"""
    try:
        # TODO: Save to database
        # Trigger automated cleanup when settings change
        await trigger_cleanup()
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update retention settings: {str(e)}")


@router.post("/cleanup/trigger")
async def trigger_manual_cleanup(db: AsyncSession = Depends(get_db)):
    """
    Manually trigger cleanup process
    
    Useful for:
    - Testing cleanup logic
    - Immediate cleanup after settings change
    - Disk space emergency
    """
    try:
        await trigger_cleanup()
        return {
            "success": True,
            "message": "Cleanup triggered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger cleanup: {str(e)}")

