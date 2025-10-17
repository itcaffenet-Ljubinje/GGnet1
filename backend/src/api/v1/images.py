"""
Images API Endpoints

Manage system and game images for diskless deployment.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from db.base import get_db
from db.models import Image, ImageType, ImageStatus

router = APIRouter(prefix="/images", tags=["images"])


# Schemas
class ImageCreate(BaseModel):
    name: str
    type: ImageType
    description: str | None = None
    is_default: bool = False


class ImageResponse(BaseModel):
    image_id: str
    name: str
    type: ImageType
    version: int
    size_bytes: int
    status: ImageStatus
    is_default: bool
    creation_date: str
    
    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[ImageResponse])
async def list_images(
    type: ImageType | None = None,
    db: AsyncSession = Depends(get_db)
):
    """List all images, optionally filtered by type"""
    query = select(Image)
    
    if type:
        query = query.where(Image.type == type)
    
    result = await db.execute(query.order_by(Image.creation_date.desc()))
    images = result.scalars().all()
    
    return images


@router.post("/", response_model=ImageResponse)
async def create_image(
    image_data: ImageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new image
    
    TODO: Implement actual image creation:
    - Create ZFS volume
    - Format filesystem
    - Setup iSCSI target
    - Import from VHD/VHDX if provided
    """
    
    # Generate storage path
    storage_path = f"/pool0/ggnet/images/{image_data.type}/{image_data.name}"
    
    image = Image(
        name=image_data.name,
        type=image_data.type,
        description=image_data.description,
        storage_path=storage_path,
        is_default=image_data.is_default,
        status=ImageStatus.ACTIVE
    )
    
    db.add(image)
    await db.commit()
    await db.refresh(image)
    
    return image


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an image"""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # TODO: Check if image is in use by any machines
    # TODO: Delete ZFS volume
    # TODO: Remove iSCSI target
    
    await db.delete(image)
    await db.commit()
    
    return {"success": True, "image_id": image_id}

