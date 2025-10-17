#!/usr/bin/env python3
"""
Snapshot Manager - Image Snapshot Management

Manages creation, restoration, and deletion of disk image snapshots.
Supports both ZFS snapshots and file-based snapshots.

Usage:
    from storage.snapshot_manager import SnapshotManager
    
    manager = SnapshotManager()
    snapshot = manager.create_snapshot("ubuntu-22.04", "Pre-update snapshot")
    manager.restore_snapshot(snapshot_id=1)
"""

import subprocess
import json
import os
import shutil
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class SnapshotManager:
    """Manages disk image snapshots"""
    
    def __init__(self, snapshot_root: str = "/srv/ggnet/snapshots"):
        """
        Initialize snapshot manager
        
        Args:
            snapshot_root: Root directory for snapshot storage
        """
        self.snapshot_root = Path(snapshot_root)
        self.snapshot_root.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(self, image_name: str, description: str = "") -> Dict[str, any]:
        """
        Create snapshot of an image
        
        Args:
            image_name: Name of the image to snapshot
            description: Optional description
        
        Returns:
            Dict with snapshot info
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_name = f"{image_name}-{timestamp}"
        snapshot_path = self.snapshot_root / snapshot_name
        
        # TODO: Implement actual snapshot creation
        # Options:
        # 1. ZFS snapshot: zfs snapshot pool/image@snapshot_name
        # 2. File copy: cp -a image snapshot (slow but simple)
        # 3. COW filesystem features (btrfs reflink, xfs reflink)
        # 4. LVM snapshot
        
        return {
            "status": "stub",
            "snapshot_name": snapshot_name,
            "snapshot_path": str(snapshot_path),
            "image_name": image_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "message": "Snapshot creation not yet implemented",
            "implementation_note": "Use ZFS snapshots for production: zfs snapshot pool/images/{}@{}".format(image_name, timestamp)
        }
    
    def list_snapshots(self, image_name: Optional[str] = None) -> List[Dict[str, any]]:
        """
        List all snapshots or snapshots for specific image
        
        Args:
            image_name: Optional image name to filter by
        
        Returns:
            List of snapshot info dicts
        """
        snapshots = []
        
        try:
            # List directories in snapshot root
            if self.snapshot_root.exists():
                for item in self.snapshot_root.iterdir():
                    if item.is_dir():
                        # Parse snapshot name
                        parts = item.name.split('-')
                        if len(parts) >= 2:
                            snap_image_name = '-'.join(parts[:-2]) if len(parts) > 2 else parts[0]
                            
                            # Filter by image name if provided
                            if image_name and snap_image_name != image_name:
                                continue
                            
                            # Get snapshot size
                            size = self._get_directory_size(item)
                            
                            snapshots.append({
                                "snapshot_name": item.name,
                                "image_name": snap_image_name,
                                "path": str(item),
                                "size_bytes": size,
                                "created_at": datetime.fromtimestamp(item.stat().st_ctime).isoformat()
                            })
            
            # Sort by creation time (newest first)
            snapshots.sort(key=lambda x: x["created_at"], reverse=True)
        
        except Exception as e:
            return [{"error": f"Failed to list snapshots: {str(e)}"}]
        
        return snapshots
    
    def restore_snapshot(self, snapshot_id: int, image_name: str) -> Dict[str, any]:
        """
        Restore image from snapshot
        
        Args:
            snapshot_id: Snapshot ID
            image_name: Target image name
        
        Returns:
            Dict with restoration status
        """
        # TODO: Implement actual snapshot restoration
        # Process:
        # 1. Stop any VMs using the image
        # 2. Backup current image state
        # 3. Restore snapshot data
        # 4. Update database to point to restored snapshot
        # 5. Notify connected clients
        
        return {
            "status": "stub",
            "snapshot_id": snapshot_id,
            "image_name": image_name,
            "message": "Snapshot restoration not yet implemented",
            "implementation_note": "For ZFS: zfs rollback pool/images/{}@snapshot_name".format(image_name)
        }
    
    def delete_snapshot(self, snapshot_name: str) -> Dict[str, any]:
        """
        Delete a snapshot
        
        Args:
            snapshot_name: Name of snapshot to delete
        
        Returns:
            Dict with deletion status
        """
        snapshot_path = self.snapshot_root / snapshot_name
        
        if not snapshot_path.exists():
            return {
                "status": "error",
                "message": f"Snapshot {snapshot_name} not found"
            }
        
        try:
            # Delete snapshot directory
            shutil.rmtree(snapshot_path)
            
            return {
                "status": "success",
                "message": f"Snapshot {snapshot_name} deleted",
                "path": str(snapshot_path)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete snapshot: {str(e)}"
            }
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total
    
    def get_snapshot_info(self, snapshot_name: str) -> Dict[str, any]:
        """
        Get detailed information about a snapshot
        
        Args:
            snapshot_name: Name of snapshot
        
        Returns:
            Dict with snapshot details
        """
        snapshot_path = self.snapshot_root / snapshot_name
        
        if not snapshot_path.exists():
            return {
                "status": "error",
                "message": f"Snapshot {snapshot_name} not found"
            }
        
        try:
            stat = snapshot_path.stat()
            size = self._get_directory_size(snapshot_path)
            
            return {
                "snapshot_name": snapshot_name,
                "path": str(snapshot_path),
                "size_bytes": size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get snapshot info: {str(e)}"
            }


# Convenience functions
def create_snapshot(image_name: str, description: str = "") -> Dict[str, any]:
    """Quick snapshot creation"""
    manager = SnapshotManager()
    return manager.create_snapshot(image_name, description)


def list_snapshots(image_name: Optional[str] = None) -> List[Dict[str, any]]:
    """Quick snapshot listing"""
    manager = SnapshotManager()
    return manager.list_snapshots(image_name)


if __name__ == "__main__":
    # CLI usage
    import sys
    
    manager = SnapshotManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            image_name = sys.argv[2] if len(sys.argv) > 2 else None
            snapshots = manager.list_snapshots(image_name)
            print(json.dumps(snapshots, indent=2))
        
        elif command == "create" and len(sys.argv) > 2:
            image_name = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            result = manager.create_snapshot(image_name, description)
            print(json.dumps(result, indent=2))
        
        elif command == "delete" and len(sys.argv) > 2:
            snapshot_name = sys.argv[2]
            result = manager.delete_snapshot(snapshot_name)
            print(json.dumps(result, indent=2))
        
        elif command == "info" and len(sys.argv) > 2:
            snapshot_name = sys.argv[2]
            info = manager.get_snapshot_info(snapshot_name)
            print(json.dumps(info, indent=2))
        
        else:
            print("Usage:")
            print("  python snapshot_manager.py list [image_name]")
            print("  python snapshot_manager.py create <image_name> [description]")
            print("  python snapshot_manager.py delete <snapshot_name>")
            print("  python snapshot_manager.py info <snapshot_name>")
            sys.exit(1)
    else:
        # Default: list all snapshots
        snapshots = manager.list_snapshots()
        print(json.dumps(snapshots, indent=2))

