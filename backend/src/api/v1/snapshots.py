"""
Snapshots API Endpoints

Create and manage immutable snapshots from writebacks.
Apply snapshots to create new image versions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from db.base import get_db
from db.models import Snapshot, Writeback, Image, SnapshotStatus

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


# Schemas
class SnapshotCreate(BaseModel):
    writeback_id: str
    name: str
    description: str | None = None
    protected: bool = False


class SnapshotResponse(BaseModel):
    snapshot_id: str
    name: str
    source_writeback_id: str
    base_image_id: str
    size_bytes: int
    status: SnapshotStatus
    date_created: str
    protected: bool
    
    class Config:
        from_attributes = True


class ApplySnapshotRequest(BaseModel):
    snapshot_id: str
    new_image_name: str
    make_default: bool = False


# Endpoints
@router.get("/", response_model=List[SnapshotResponse])
async def list_snapshots(db: AsyncSession = Depends(get_db)):
    """List all snapshots"""
    result = await db.execute(
        select(Snapshot).order_by(Snapshot.date_created.desc())
    )
    snapshots = result.scalars().all()
    return snapshots


@router.post("/", response_model=SnapshotResponse)
async def create_snapshot(
    snapshot_data: SnapshotCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create snapshot from writeback
    
    This captures client changes into an immutable snapshot.
    See docs/PIM_TECHNICAL_ARCHITECTURE.md Section 3.2 for full logic.
    """
    # Verify writeback exists
    result = await db.execute(
        select(Writeback).where(Writeback.writeback_id == snapshot_data.writeback_id)
    )
    writeback = result.scalar_one_or_none()
    
    if not writeback:
        raise HTTPException(status_code=404, detail="Writeback not found")
    
    if writeback.status == WritebackStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Cannot snapshot active Writeback. Shutdown client first."
        )
    
    # TODO: Create ZFS snapshot
    # Command: zfs snapshot pool0/ggnet/writebacks/[writeback_id]@[snapshot_id]
    
    snapshot = Snapshot(
        name=snapshot_data.name,
        source_writeback_id=snapshot_data.writeback_id,
        source_client_id=writeback.attached_client_id,
        base_image_id=writeback.base_image_id,
        description=snapshot_data.description,
        size_bytes=writeback.size_of_changes,
        protected=snapshot_data.protected,
        status=SnapshotStatus.ACTIVE
    )
    
    db.add(snapshot)
    
    # Mark writeback as ready for snapshot
    writeback.status = WritebackStatus.READY_FOR_SNAPSHOT
    writeback.ready_for_snapshot = True
    
    await db.commit()
    await db.refresh(snapshot)
    
    return snapshot


@router.post("/apply")
async def apply_snapshot_to_image(
    apply_request: ApplySnapshotRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply snapshot to create new image version
    
    This is the core operation: merges Writeback changes into a new master Image.
    See docs/PIM_TECHNICAL_ARCHITECTURE.md Section 3.3 for complete algorithm.
    
    Steps:
    1. Validate snapshot and parent image
    2. Create new ZFS clone or copy
    3. Merge differential changes from writeback
    4. Finalize new image with updated metadata
    5. Update relationships and cleanup
    """
    # Get snapshot
    result = await db.execute(
        select(Snapshot).where(Snapshot.snapshot_id == apply_request.snapshot_id)
    )
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    if snapshot.status == SnapshotStatus.APPLIED:
        raise HTTPException(
            status_code=400,
            detail=f"Snapshot already applied to image {snapshot.applied_to_image_id}"
        )
    
    # Get parent image
    result = await db.execute(
        select(Image).where(Image.image_id == snapshot.base_image_id)
    )
    parent_image = result.scalar_one_or_none()
    
    if not parent_image:
        raise HTTPException(status_code=404, detail="Base image not found")
    
    # TODO: Implement full merge logic (see PIM_TECHNICAL_ARCHITECTURE.md)
    # 1. Create ZFS clone: zfs clone parent@snapshot new_image
    # 2. Merge changes from writeback
    # 3. Calculate checksum
    # 4. Verify integrity
    
    # Create new image
    new_image = Image(
        name=apply_request.new_image_name,
        type=parent_image.type,
        version=parent_image.version + 1,
        parent_image_id=parent_image.image_id,
        base_snapshot_id=snapshot.snapshot_id,
        storage_path=f"/pool0/ggnet/images/{parent_image.type}/{apply_request.new_image_name}",
        size_bytes=parent_image.size_bytes + snapshot.size_bytes,
        description=f"Applied snapshot: {snapshot.name}",
        is_default=apply_request.make_default,
        status=ImageStatus.ACTIVE
    )
    
    db.add(new_image)
    
    # Update snapshot status
    snapshot.status = SnapshotStatus.APPLIED
    snapshot.applied_to_image_id = new_image.image_id
    
    # Deprecate parent image
    parent_image.status = ImageStatus.DEPRECATED
    
    # If making default, remove default flag from others
    if apply_request.make_default:
        result = await db.execute(
            select(Image).where(
                Image.type == parent_image.type,
                Image.is_default == True
            )
        )
        old_defaults = result.scalars().all()
        for img in old_defaults:
            img.is_default = False
    
    await db.commit()
    await db.refresh(new_image)
    
    return {
        "success": True,
        "new_image_id": new_image.image_id,
        "new_image_name": new_image.name,
        "version": new_image.version,
        "parent_image": parent_image.image_id,
        "applied_snapshot": snapshot.snapshot_id
    }


@router.get("/{image_id}/versions")
async def get_image_versions(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get version history for an image
    
    Traces back through parent_image_id relationships.
    """
    versions = []
    current_id = image_id
    
    while current_id:
        result = await db.execute(
            select(Image).where(Image.image_id == current_id)
        )
        img = result.scalar_one_or_none()
        
        if not img:
            break
        
        versions.append({
            "image_id": img.image_id,
            "name": img.name,
            "version": img.version,
            "status": img.status,
            "creation_date": img.creation_date.isoformat()
        })
        
        current_id = img.parent_image_id
    
    return {"image_id": image_id, "versions": versions}

