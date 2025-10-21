"""
Machines API Endpoints

Manage diskless client machines.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from pydantic import BaseModel, Field

from db.base import get_db
from db.models import Machine

router = APIRouter()


# Schemas
class MachineCreate(BaseModel):
    """Schema for creating a new machine"""
    name: str = Field(..., min_length=1, max_length=100,
                      description="Machine display name")
    mac_address: str = Field(...,
                             pattern=r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$",
                             description="MAC address (XX:XX:XX:XX:XX:XX)")
    ip_address: str | None = Field(None, description="IP address (optional)")
    image_id: str | None = Field(None, description="Image ID to assign")
    is_virtual: bool = Field(False, description="Is this a virtual machine?")
    vnc_enabled: bool = Field(False, description="Enable VNC access")
    vnc_port: int | None = Field(None, description="VNC port (default: 5900 + machine_id)")


class MachineResponse(BaseModel):
    """Schema for machine response"""
    id: int
    name: str
    mac_address: str
    ip_address: str | None
    status: str
    image_name: str | None
    image_id: str | None
    writeback_size: int
    keep_writeback: bool
    last_boot: str | None
    is_virtual: bool = False
    vnc_enabled: bool = False
    vnc_port: int | None = None
    vnc_password: str | None = None

    class Config:
        from_attributes = True


class ApplyWritebackRequest(BaseModel):
    """Schema for apply writeback request"""
    comment: str | None = Field(
        None,
        max_length=500,
        description="Description of changes")


# Endpoints
@router.get("/machines", response_model=List[MachineResponse])
async def list_machines(db: AsyncSession = Depends(get_db)):
    """
    List all registered machines

    Returns a list of all machines with their current status.
    """
    result = await db.execute(select(Machine).order_by(Machine.id))
    machines = result.scalars().all()

    # Convert datetime to string for JSON
    machine_list = []
    for m in machines:
        machine_list.append({
            "id": m.id,
            "name": m.name,
            "mac_address": m.mac_address,
            "ip_address": m.ip_address,
            "status": m.status,
            "image_name": m.image_name,
            "image_id": m.image_name,  # For compatibility (image_name stores image_id)
            "writeback_size": m.writeback_size,
            "keep_writeback": m.keep_writeback,
            "last_boot": m.last_boot.isoformat() if m.last_boot else None,
            "is_virtual": False,
            "vnc_enabled": False,
            "vnc_port": None
        })

    return machine_list


@router.post("/machines", response_model=MachineResponse, status_code=201)
async def create_machine(
    machine_data: MachineCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new machine

    Creates a new machine entry with the provided MAC address and name.
    MAC address must be unique.
    """
    # Validate and normalize MAC address
    mac = machine_data.mac_address.upper()

    # Create machine
    machine = Machine(
        name=machine_data.name,
        mac_address=mac,
        ip_address=machine_data.ip_address,
        status="offline",
        image_name=machine_data.image_id  # Store image_id as image_name for now
    )

    db.add(machine)

    try:
        await db.commit()
        await db.refresh(machine)
        
        # If virtual machine, setup VNC
        if machine_data.is_virtual and machine_data.vnc_enabled:
            # TODO: Start VNC server for virtual machine
            pass
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Machine with MAC address {mac} already exists"
        )

    return {
        "id": machine.id,
        "name": machine.name,
        "mac_address": machine.mac_address,
        "ip_address": machine.ip_address,
        "status": machine.status,
        "image_name": machine.image_name,
        "image_id": machine.image_name,  # For now, same as image_name
        "writeback_size": machine.writeback_size,
        "keep_writeback": machine.keep_writeback,
        "last_boot": machine.last_boot.isoformat() if machine.last_boot else None,
        "is_virtual": machine_data.is_virtual,
        "vnc_enabled": machine_data.vnc_enabled,
        "vnc_port": machine_data.vnc_port or (5900 + machine.id) if machine_data.vnc_enabled else None
    }


@router.post("/machines/{machine_id}/vnc/connect")
async def connect_vnc(
    machine_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get VNC connection info for virtual machine
    
    Returns VNC URL and credentials for connecting to the machine.
    """
    result = await db.execute(
        select(Machine).where(Machine.id == machine_id)
    )
    machine = result.scalar_one_or_none()
    
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # TODO: Implement VNC server management
    # For now, return placeholder info
    vnc_port = 5900 + machine_id
    
    return {
        "machine_id": machine_id,
        "machine_name": machine.name,
        "vnc_host": "localhost",
        "vnc_port": vnc_port,
        "vnc_url": f"vnc://localhost:{vnc_port}",
        "web_url": f"http://localhost:6080/vnc.html?host=localhost&port={vnc_port}",
        "password": "ggnet123",  # TODO: Generate secure password
        "status": "connected"
    }


@router.delete("/machines/{machine_id}", status_code=204)
async def delete_machine(
    machine_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a machine

    Permanently removes a machine from the system.
    Associated writebacks will also be deleted.
    """
    result = await db.execute(
        select(Machine).where(Machine.id == machine_id)
    )
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    await db.delete(machine)
    await db.commit()

    return None


@router.get("/machines/{machine_id}")
async def get_machine(
    machine_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get machine details"""
    result = await db.execute(
        select(Machine).where(Machine.id == machine_id)
    )
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    return {
        "id": machine.id,
        "name": machine.name,
        "mac_address": machine.mac_address,
        "ip_address": machine.ip_address,
        "status": machine.status,
        "image_name": machine.image_name,
        "writeback_size": machine.writeback_size,
        "keep_writeback": machine.keep_writeback,
        "last_boot": machine.last_boot.isoformat() if machine.last_boot else None}


@router.post("/machines/{machine_id}/power")
async def power_operation(
    machine_id: int,
    action: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Power operation on machine

    Actions: start, stop, reboot

    TODO: Implement actual Wake-on-LAN for start
    TODO: Implement SSH/agent for stop/reboot
    """
    result = await db.execute(
        select(Machine).where(Machine.id == machine_id)
    )
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if action == "start":
        machine.status = "booting"
        # TODO: Send Wake-on-LAN magic packet to machine.mac_address
    elif action == "stop":
        machine.status = "offline"
        # TODO: Send shutdown signal via SSH or agent
    elif action == "reboot":
        machine.status = "booting"
        # TODO: Send reboot signal
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {action}")

    await db.commit()

    return {
        "success": True,
        "machine_id": machine_id,
        "action": action,
        "new_status": machine.status
    }


@router.post("/machines/{machine_id}/apply_writeback")
async def apply_writeback(
    machine_id: int,
    request: ApplyWritebackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply machine writeback (create snapshot)

    This endpoint schedules the writeback to be merged into the base image.
    Currently marks the operation in the database.

    TODO: Integrate with snapshot_service for actual merge operation.
    """
    result = await db.execute(
        select(Machine).where(Machine.id == machine_id)
    )
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if machine.writeback_size == 0:
        raise HTTPException(
            status_code=400,
            detail="No writeback to apply - writeback size is 0"
        )

    # TODO: Call snapshot_service.create_snapshot()
    # For now, just return success

    return {
        "success": True,
        "message": "Writeback apply scheduled",
        "machine_id": machine_id,
        "writeback_size": machine.writeback_size,
        "comment": request.comment
    }


@router.post("/machines/{machine_id}/keep_writeback")
async def set_keep_writeback(
    machine_id: int,
    keep: bool,
    db: AsyncSession = Depends(get_db)
):
    """
    Enable/disable keep writeback for machine

    When enabled, writeback is preserved across reboots.
    When disabled, writeback is discarded on shutdown.
    """
    result = await db.execute(
        select(Machine).where(Machine.id == machine_id)
    )
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    machine.keep_writeback = keep
    await db.commit()

    return {
        "success": True,
        "machine_id": machine_id,
        "keep_writeback": keep,
        "message": f"Keep writeback {'enabled' if keep else 'disabled'}"
    }
