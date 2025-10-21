"""
Writebacks API Endpoints

Manage per-client write storage and differential changes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from pydantic import BaseModel, field_serializer
from datetime import datetime

from db.base import get_db
from db.models import Writeback, WritebackStatus

router = APIRouter(prefix="/writebacks", tags=["writebacks"])


# Schemas
class WritebackCreate(BaseModel):
    attached_client_id: str
    base_image_id: str
    size_of_changes: int = 0


class WritebackResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    writeback_id: str
    attached_client_id: str
    base_image_id: str
    size_of_changes: int
    status: WritebackStatus
    created_at: str | datetime
    inactive_hours: int = 0
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime | str, _info):
        """Convert datetime to ISO string"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        return dt


# Endpoints
@router.get("/", response_model=List[WritebackResponse])
async def list_writebacks(
    client_id: str | None = None,
    status: WritebackStatus | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all writebacks with optional filters
    """
    query = select(Writeback)

    if client_id:
        query = query.where(Writeback.attached_client_id == client_id)

    if status:
        query = query.where(Writeback.status == status)

    result = await db.execute(query.order_by(Writeback.created_at.desc()))
    writebacks = result.scalars().all()

    # TODO: Calculate inactive_hours from last_activity
    result_list = []
    for wb in writebacks:
        wb.inactive_hours = 0  # Placeholder
        result_list.append(WritebackResponse.from_orm(wb))

    return result_list


@router.post("/", response_model=WritebackResponse, status_code=201)
async def create_writeback(
    writeback_data: WritebackCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new writeback for a client"""
    writeback = Writeback(
        attached_client_id=writeback_data.attached_client_id,
        base_image_id=writeback_data.base_image_id,
        size_of_changes=writeback_data.size_of_changes,
        status=WritebackStatus.ACTIVE,
        ready_for_snapshot=False
    )
    
    db.add(writeback)
    try:
        await db.commit()
        await db.refresh(writeback)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Writeback already exists for this client")
    
    writeback.inactive_hours = 0  # Placeholder
    return WritebackResponse.from_orm(writeback)


@router.get("/{writeback_id}", response_model=WritebackResponse)
async def get_writeback(
    writeback_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get writeback by ID"""
    result = await db.execute(
        select(Writeback).where(Writeback.writeback_id == writeback_id)
    )
    writeback = result.scalar_one_or_none()
    
    if not writeback:
        raise HTTPException(status_code=404, detail="Writeback not found")
    
    writeback.inactive_hours = 0  # Placeholder
    return WritebackResponse.from_orm(writeback)


@router.delete("/{writeback_id}")
async def delete_writeback(
    writeback_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a writeback

    WARNING: This permanently removes client changes!
    Ensure Snapshot exists if changes need to be preserved.
    """
    result = await db.execute(
        select(Writeback).where(Writeback.writeback_id == writeback_id)
    )
    writeback = result.scalar_one_or_none()

    if not writeback:
        raise HTTPException(status_code=404, detail="Writeback not found")

    if writeback.status == WritebackStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete active Writeback. Shutdown client first."
        )

    # TODO: Delete ZFS volume
    # TODO: Remove iSCSI target
    # Command: zfs destroy pool0/ggnet/writebacks/[writeback_id]

    await db.delete(writeback)
    await db.commit()

    return {"success": True, "writeback_id": writeback_id}


@router.post("/{writeback_id}/apply")
async def apply_writeback(
    writeback_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply writeback changes to base image
    
    This commits all changes in the writeback layer back to the base image.
    After applying, the writeback is marked as applied and can be deleted.
    """
    result = await db.execute(
        select(Writeback).where(Writeback.writeback_id == writeback_id)
    )
    writeback = result.scalar_one_or_none()

    if not writeback:
        raise HTTPException(status_code=404, detail="Writeback not found")

    # TODO: Implement actual ZFS merge
    # Command: zfs send pool0/ggnet/writebacks/[writeback_id]@snapshot | zfs receive pool0/ggnet/images/[image_id]
    
    writeback.status = WritebackStatus.APPLIED
    await db.commit()
    await db.refresh(writeback)
    
    writeback.inactive_hours = 0  # Placeholder
    return WritebackResponse.from_orm(writeback)


@router.post("/{writeback_id}/discard")
async def discard_writeback(
    writeback_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Discard writeback changes
    
    This deletes all changes in the writeback without applying them.
    Client will revert to clean state on next boot.
    """
    result = await db.execute(
        select(Writeback).where(Writeback.writeback_id == writeback_id)
    )
    writeback = result.scalar_one_or_none()

    if not writeback:
        raise HTTPException(status_code=404, detail="Writeback not found")

    # TODO: Delete ZFS volume
    # Command: zfs destroy pool0/ggnet/writebacks/[writeback_id]
    
    writeback.status = WritebackStatus.DISCARDED
    await db.commit()
    await db.refresh(writeback)
    
    writeback.inactive_hours = 0  # Placeholder
    return WritebackResponse.from_orm(writeback)


@router.post("/cleanup")
async def cleanup_writebacks(db: AsyncSession = Depends(get_db)):
    """
    Run writeback cleanup based on retention policies

    Deletes inactive writebacks older than configured threshold.
    """
    # TODO: Implement retention policy logic
    # 1. Find writebacks with status=INACTIVE
    # 2. Check inactive_hours > threshold
    # 3. Delete ZFS volumes
    # 4. Remove database records

    return {
        "success": True,
        "deleted_count": 0,  # TODO: Return actual count
        "space_freed_bytes": 0
    }
