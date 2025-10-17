"""
Writebacks API Endpoints

Manage per-client write storage and differential changes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from db.base import get_db
from db.models import Writeback, WritebackStatus

router = APIRouter(prefix="/writebacks", tags=["writebacks"])


# Schemas
class WritebackResponse(BaseModel):
    writeback_id: str
    attached_client_id: str
    base_image_id: str
    size_of_changes: int
    status: WritebackStatus
    created_at: str
    inactive_hours: int

    class Config:
        from_attributes = True


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
    for wb in writebacks:
        wb.inactive_hours = 0  # Placeholder

    return writebacks


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
