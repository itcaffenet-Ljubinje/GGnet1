"""
Images API Endpoints

Manage system and game images for diskless deployment.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel, field_serializer
from datetime import datetime
import shutil
from pathlib import Path

from db.base import get_db
from db.models import Image, ImageType, ImageStatus

router = APIRouter(prefix="/images", tags=["images"])


# Schemas
class ImageCreate(BaseModel):
    name: str
    type: str  # "os" or "game"
    description: str | None = None
    storage_path: str | None = None
    size_bytes: int = 0
    is_default: bool = False


class ImageResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    image_id: str
    name: str
    type: str
    version: int
    size_bytes: int
    status: str
    is_default: bool
    creation_date: str | datetime
    storage_path: str | None = None
    description: str | None = None
    
    @field_serializer('creation_date')
    def serialize_datetime(self, dt: datetime | str, _info):
        """Convert datetime to ISO string"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        return dt


# Endpoints
@router.get("/", response_model=List[ImageResponse])
async def list_images(
    type: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """List all images, optionally filtered by type"""
    query = select(Image)

    if type:
        query = query.where(Image.type == type)

    result = await db.execute(query.order_by(Image.creation_date.desc()))
    images = result.scalars().all()

    return images


@router.post("/", response_model=ImageResponse, status_code=201)
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
    if not image_data.storage_path:
        storage_path = f"/var/lib/ggnet/images/{image_data.type}/{image_data.name}"
    else:
        storage_path = image_data.storage_path

    image = Image(
        name=image_data.name,
        type=image_data.type,
        description=image_data.description,
        storage_path=storage_path,
        size_bytes=image_data.size_bytes,
        is_default=image_data.is_default,
        status="active"
    )

    db.add(image)
    try:
        await db.commit()
        await db.refresh(image)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Image with name '{image_data.name}' already exists")

    return image


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get image by ID"""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete image"""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    await db.delete(image)
    await db.commit()
    
    return {"message": "Image deleted successfully"}


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    name: str = Form(...),
    type: str = Form(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload image file (VHD, VHDX, ISO, IMG)
    
    Supported formats:
    - VHD/VHDX (Virtual Hard Disk)
    - ISO (CD/DVD Image)
    - IMG (Disk Image)
    """
    
    # Validate type
    if type not in ["os", "game", "windows", "linux"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    # Validate file extension
    allowed_extensions = [".vhd", ".vhdx", ".iso", ".img", ".raw"]
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate storage path
    storage_dir = Path(f"/var/lib/ggnet/images/{type}")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    storage_path = storage_dir / f"{name}{file_ext}"
    
    # Save uploaded file
    try:
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = storage_path.stat().st_size
        
        # Create database record
        image = Image(
            name=name,
            type=type,
            description=description,
            storage_path=str(storage_path),
            size_bytes=file_size,
            is_default=False,
            status="active"
        )
        
        db.add(image)
        await db.commit()
        await db.refresh(image)
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "image_id": image.image_id,
            "file_size": file_size
        }
    
    except Exception as e:
        # Clean up on error
        if storage_path.exists():
            storage_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


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
