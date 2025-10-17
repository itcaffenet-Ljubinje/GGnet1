"""
ggNet Database Models

Simplified models for diskless boot management system.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


def generate_id():
    """Generate short UUID"""
    return str(uuid.uuid4())


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
    mac_address = Column(String(17), unique=True, nullable=False)  # XX:XX:XX:XX:XX:XX
    ip_address = Column(String(45), nullable=True)
    status = Column(String(20), default="offline")  # online, offline, booting, error
    image_name = Column(String(100), nullable=True)
    writeback_size = Column(Integer, default=0)  # bytes
    keep_writeback = Column(Boolean, default=False)
    last_boot = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    writebacks = relationship("Writeback", back_populates="machine", cascade="all, delete-orphan")


class Image(Base):
    """
    Image Model - Bootable disk image
    
    Attributes:
        id: Primary key
        name: Unique image name
        path: Storage path (relative to IMAGE_ROOT)
        type: 'os' or 'game'
        size_bytes: Total image size
        active_snapshot_id: Currently active snapshot
    """
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    path = Column(String(500), nullable=False)
    type = Column(String(10), nullable=False)  # 'os' or 'game'
    size_bytes = Column(Integer, default=0)
    active_snapshot_id = Column(Integer, ForeignKey("snapshots.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    snapshots = relationship("Snapshot", back_populates="image", foreign_keys="Snapshot.image_id")
    writebacks = relationship("Writeback", back_populates="image")


class Snapshot(Base):
    """
    Snapshot Model - Point-in-time image capture
    
    Attributes:
        id: Primary key
        image_id: Parent image
        created_by: Username who created snapshot
        created_at: Creation timestamp
        comment: Description of changes
        path: Storage path for snapshot data
    """
    __tablename__ = "snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(String(500), nullable=True)
    path = Column(String(500), nullable=False)
    
    # Relationships
    image = relationship("Image", back_populates="snapshots", foreign_keys=[image_id])


class Writeback(Base):
    """
    Writeback Model - Per-machine write layer
    
    Attributes:
        id: Primary key
        machine_id: Associated machine
        image_id: Base image
        path: Storage path for writeback data
        size_bytes: Current size in bytes
        created_at: Creation timestamp
    """
    __tablename__ = "writebacks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    path = Column(String(500), nullable=False)
    size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    machine = relationship("Machine", back_populates="writebacks")
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

