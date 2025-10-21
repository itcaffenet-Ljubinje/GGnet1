"""
ggNet Database Models

Simplified models for diskless boot management system.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
import uuid
import enum


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


def generate_id():
    """Generate short UUID"""
    return str(uuid.uuid4())


# Enums
class ImageType(enum.Enum):
    """Image type enumeration (ggRock compatible)"""
    OS = "os"  # OS Image (C: drive)
    GAME = "game"  # Game Image (G: drive or custom)
    WINDOWS = "windows"  # Windows OS Image
    LINUX = "linux"  # Linux OS Image


class ImageStatus(enum.Enum):
    """Image status enumeration (ggRock compatible)"""
    ACTIVE = "active"  # Active and in use
    DEPRECATED = "deprecated"  # Deprecated but available
    INACTIVE = "inactive"  # Not in use
    TESTING = "testing"  # In testing phase


class WritebackStatus(enum.Enum):
    """Writeback status enumeration (ggRock compatible)"""
    ACTIVE = "active"  # Active writeback
    INACTIVE = "inactive"  # Inactive/wiped
    READY_FOR_SNAPSHOT = "ready_for_snapshot"  # Ready to apply
    APPLIED = "applied"  # Applied to image
    DISCARDED = "discarded"  # Discarded without applying


class SnapshotStatus(enum.Enum):
    """Snapshot status enumeration (ggRock compatible)"""
    ACTIVE = "active"  # Active snapshot (currently in use)
    LATEST = "latest"  # Latest snapshot (most recent)
    ARCHIVED = "archived"  # Archived snapshot
    DELETED = "deleted"  # Deleted snapshot


class Machine(Base):
    """
    Machine Model - Client PC

    Attributes:
        id: Primary key
        name: Display name
        mac_address: Unique MAC address for PXE boot
        ip_address: Current IP (from DHCP)
        status: online/offline/booting
        image_name: Currently assigned image
        writeback_size: Size of writeback in bytes
        keep_writeback: Persist writeback across reboots
        last_boot: Last boot timestamp
    """
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    mac_address = Column(
        String(17),
        unique=True,
        nullable=False)  # XX:XX:XX:XX:XX:XX
    ip_address = Column(String(45), nullable=True)
    # online, offline, booting, error
    status = Column(String(20), default="offline")
    image_name = Column(String(100), nullable=True)
    writeback_size = Column(Integer, default=0)  # bytes
    keep_writeback = Column(Boolean, default=False)
    last_boot = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    # Relationships - removed writebacks relationship due to schema mismatch
    # Writebacks now use attached_client_id instead of machine_id


class Image(Base):
    """
    Image Model - Bootable disk image

    Attributes:
        image_id: Primary key (UUID string)
        name: Unique image name
        type: ImageType enum (OS or GAME)
        version: Image version number
        description: Image description
        storage_path: Storage path (relative to IMAGE_ROOT)
        size_bytes: Total image size
        status: ImageStatus enum
        is_default: Is this the default image for its type
        parent_image_id: Parent image ID (for versioning)
        base_snapshot_id: Base snapshot ID
        applied_to_image_id: Applied to image ID
    """
    __tablename__ = "images"

    image_id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(20), nullable=False)  # Changed from Enum to String for SQLite compatibility
    version = Column(Integer, default=1)
    description = Column(String(500), nullable=True)
    storage_path = Column(String(500), nullable=False)
    size_bytes = Column(Integer, default=0)
    status = Column(String(20), default="active")  # Changed from Enum to String for SQLite compatibility
    is_default = Column(Boolean, default=False)
    parent_image_id = Column(String(36), nullable=True)
    base_snapshot_id = Column(String(36), nullable=True)
    applied_to_image_id = Column(String(36), nullable=True)
    creation_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    snapshots = relationship(
        "Snapshot",
        back_populates="image",
        foreign_keys="Snapshot.base_image_id")
    writebacks = relationship("Writeback", back_populates="image")


class Snapshot(Base):
    """
    Snapshot Model - Point-in-time image capture

    Attributes:
        snapshot_id: Primary key (UUID string)
        name: Snapshot name
        source_writeback_id: Source writeback ID
        source_client_id: Source client ID
        base_image_id: Base image ID
        description: Snapshot description
        size_bytes: Snapshot size
        status: SnapshotStatus enum
        protected: Is this snapshot protected
        date_created: Creation timestamp
        applied_to_image_id: Applied to image ID
    """
    __tablename__ = "snapshots"

    snapshot_id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(100), nullable=False)
    source_writeback_id = Column(String(36), nullable=True)  # Can be None for manual snapshots
    source_client_id = Column(String(36), nullable=True)     # Can be None for manual snapshots
    base_image_id = Column(String(36), ForeignKey("images.image_id"), nullable=False)
    description = Column(String(500), nullable=True)
    size_bytes = Column(Integer, default=0)
    status = Column(Enum(SnapshotStatus), default=SnapshotStatus.ACTIVE)
    protected = Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    applied_to_image_id = Column(String(36), nullable=True)

    # Relationships
    image = relationship(
        "Image",
        back_populates="snapshots",
        foreign_keys=[base_image_id])


class Writeback(Base):
    """
    Writeback Model - Per-machine write layer

    Attributes:
        writeback_id: Primary key (UUID string)
        attached_client_id: Associated client ID
        base_image_id: Base image ID
        size_of_changes: Size of changes in bytes
        status: WritebackStatus enum
        created_at: Creation timestamp
        inactive_hours: Hours since last activity
        ready_for_snapshot: Ready for snapshot flag
    """
    __tablename__ = "writebacks"

    writeback_id = Column(String(36), primary_key=True, default=generate_id)
    attached_client_id = Column(String(36), nullable=False)
    base_image_id = Column(String(36), ForeignKey("images.image_id"), nullable=False)
    size_of_changes = Column(Integer, default=0)
    status = Column(Enum(WritebackStatus), default=WritebackStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    inactive_hours = Column(Integer, default=0)
    ready_for_snapshot = Column(Boolean, default=False)

    # Relationships - removed machine relationship due to schema mismatch
    # Writebacks now use attached_client_id instead of machine_id
    image = relationship("Image", back_populates="writebacks")


class User(Base):
    """
    User Model - Administrator account

    Attributes:
        id: Primary key
        username: Unique username
        password_hash: Hashed password
        role: admin/user
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")

    created_at = Column(DateTime, default=datetime.utcnow)
