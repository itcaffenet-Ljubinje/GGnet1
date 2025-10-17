#!/usr/bin/env python3
"""
Writeback Manager - Temporary Diff Management

Manages temporary writebacks (diffs) created by client machines.
Each client can have a writeback layer that stores changes made during their session.

Writebacks can be:
- Kept (persistent across reboots)
- Discarded (reset to clean image state)
- Applied (merged back into base image)

Usage:
    from storage.writeback_manager import WritebackManager
    
    manager = WritebackManager()
    wb = manager.create_writeback("machine-01", "ubuntu-22.04")
    manager.apply_writeback(wb_id=1)
    manager.discard_writeback(wb_id=2)
"""

import subprocess
import json
import os
import shutil
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class WritebackManager:
    """Manages client writeback layers"""
    
    def __init__(self, writeback_root: str = "/srv/ggnet/writebacks"):
        """
        Initialize writeback manager
        
        Args:
            writeback_root: Root directory for writeback storage
        """
        self.writeback_root = Path(writeback_root)
        self.writeback_root.mkdir(parents=True, exist_ok=True)
    
    def create_writeback(self, machine_name: str, image_name: str) -> Dict[str, any]:
        """
        Create new writeback layer for a machine
        
        Args:
            machine_name: Name of the client machine
            image_name: Base image name
        
        Returns:
            Dict with writeback info
        """
        writeback_name = f"{machine_name}-{image_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        writeback_path = self.writeback_root / writeback_name
        
        # Create writeback directory
        writeback_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file
        metadata = {
            "writeback_name": writeback_name,
            "machine_name": machine_name,
            "image_name": image_name,
            "created_at": datetime.now().isoformat(),
            "size_bytes": 0,
            "keep": False,
            "status": "active"
        }
        
        metadata_file = writeback_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "status": "success",
            "writeback_name": writeback_name,
            "writeback_path": str(writeback_path),
            "metadata": metadata
        }
    
    def list_writebacks(self, machine_name: Optional[str] = None) -> List[Dict[str, any]]:
        """
        List all writebacks or writebacks for specific machine
        
        Args:
            machine_name: Optional machine name to filter by
        
        Returns:
            List of writeback info dicts
        """
        writebacks = []
        
        try:
            if self.writeback_root.exists():
                for item in self.writeback_root.iterdir():
                    if item.is_dir():
                        # Load metadata if exists
                        metadata_file = item / "metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            # Filter by machine name if provided
                            if machine_name and metadata.get("machine_name") != machine_name:
                                continue
                            
                            # Update size
                            metadata["size_bytes"] = self._get_directory_size(item)
                            writebacks.append(metadata)
                        else:
                            # No metadata, create basic info
                            writebacks.append({
                                "writeback_name": item.name,
                                "path": str(item),
                                "size_bytes": self._get_directory_size(item),
                                "no_metadata": True
                            })
            
            # Sort by creation time (newest first)
            writebacks.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
        
        except Exception as e:
            return [{"error": f"Failed to list writebacks: {str(e)}"}]
        
        return writebacks
    
    def get_writeback_info(self, writeback_name: str) -> Dict[str, any]:
        """
        Get detailed information about a writeback
        
        Args:
            writeback_name: Name of writeback
        
        Returns:
            Dict with writeback details
        """
        writeback_path = self.writeback_root / writeback_name
        
        if not writeback_path.exists():
            return {
                "status": "error",
                "message": f"Writeback {writeback_name} not found"
            }
        
        try:
            # Load metadata
            metadata_file = writeback_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {"writeback_name": writeback_name}
            
            # Update with current info
            metadata["path"] = str(writeback_path)
            metadata["size_bytes"] = self._get_directory_size(writeback_path)
            metadata["exists"] = True
            
            return metadata
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get writeback info: {str(e)}"
            }
    
    def apply_writeback(self, writeback_name: str, image_name: str) -> Dict[str, any]:
        """
        Apply (merge) writeback changes back to base image
        
        Args:
            writeback_name: Name of writeback to apply
            image_name: Target image name
        
        Returns:
            Dict with operation status
        """
        writeback_path = self.writeback_root / writeback_name
        
        if not writeback_path.exists():
            return {
                "status": "error",
                "message": f"Writeback {writeback_name} not found"
            }
        
        # TODO: Implement actual merge operation
        # Process:
        # 1. Create snapshot of base image (for rollback)
        # 2. Merge writeback diff into base image
        # 3. Verify integrity
        # 4. Update database
        # 5. Optionally delete writeback
        #
        # Implementation depends on storage backend:
        # - ZFS: zfs promote/clone operations
        # - COW filesystem: reflink merge
        # - Standard files: rsync overlay
        
        return {
            "status": "stub",
            "writeback_name": writeback_name,
            "image_name": image_name,
            "message": "Writeback apply not yet implemented",
            "implementation_note": "Requires integration with image storage backend"
        }
    
    def discard_writeback(self, writeback_name: str) -> Dict[str, any]:
        """
        Discard (delete) writeback changes
        
        Args:
            writeback_name: Name of writeback to discard
        
        Returns:
            Dict with operation status
        """
        writeback_path = self.writeback_root / writeback_name
        
        if not writeback_path.exists():
            return {
                "status": "error",
                "message": f"Writeback {writeback_name} not found"
            }
        
        try:
            # Delete writeback directory
            shutil.rmtree(writeback_path)
            
            return {
                "status": "success",
                "message": f"Writeback {writeback_name} discarded",
                "path": str(writeback_path)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to discard writeback: {str(e)}"
            }
    
    def set_keep_flag(self, writeback_name: str, keep: bool) -> Dict[str, any]:
        """
        Set keep flag on writeback (persist across reboots)
        
        Args:
            writeback_name: Name of writeback
            keep: Whether to keep writeback across reboots
        
        Returns:
            Dict with operation status
        """
        writeback_path = self.writeback_root / writeback_name
        metadata_file = writeback_path / "metadata.json"
        
        if not metadata_file.exists():
            return {
                "status": "error",
                "message": f"Writeback metadata not found"
            }
        
        try:
            # Load metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Update keep flag
            metadata["keep"] = keep
            metadata["updated_at"] = datetime.now().isoformat()
            
            # Save metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "status": "success",
                "writeback_name": writeback_name,
                "keep": keep,
                "message": f"Keep flag set to {keep}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to set keep flag: {str(e)}"
            }
    
    def get_writeback_size(self, writeback_name: str) -> int:
        """Get writeback size in bytes"""
        writeback_path = self.writeback_root / writeback_name
        
        if not writeback_path.exists():
            return 0
        
        return self._get_directory_size(writeback_path)
    
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
    
    def cleanup_old_writebacks(self, max_age_days: int = 30) -> Dict[str, any]:
        """
        Clean up old writebacks that are not marked as 'keep'
        
        Args:
            max_age_days: Maximum age in days before cleanup
        
        Returns:
            Dict with cleanup results
        """
        cleaned = []
        errors = []
        
        try:
            now = datetime.now()
            
            for item in self.writeback_root.iterdir():
                if item.is_dir():
                    metadata_file = item / "metadata.json"
                    
                    # Check age
                    created_time = datetime.fromtimestamp(item.stat().st_ctime)
                    age_days = (now - created_time).days
                    
                    if age_days > max_age_days:
                        # Check keep flag
                        keep = False
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                keep = metadata.get("keep", False)
                        
                        if not keep:
                            # Delete old writeback
                            try:
                                shutil.rmtree(item)
                                cleaned.append({
                                    "writeback_name": item.name,
                                    "age_days": age_days
                                })
                            except Exception as e:
                                errors.append({
                                    "writeback_name": item.name,
                                    "error": str(e)
                                })
        
        except Exception as e:
            errors.append({"error": f"Cleanup failed: {str(e)}"})
        
        return {
            "status": "success" if not errors else "partial",
            "cleaned_count": len(cleaned),
            "cleaned": cleaned,
            "errors": errors
        }


# Convenience functions
def get_writeback_size(machine_name: str) -> int:
    """Quick writeback size check"""
    manager = WritebackManager()
    writebacks = manager.list_writebacks(machine_name)
    total = sum(wb.get("size_bytes", 0) for wb in writebacks if not wb.get("error"))
    return total


if __name__ == "__main__":
    # CLI usage
    import sys
    
    manager = WritebackManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            machine_name = sys.argv[2] if len(sys.argv) > 2 else None
            writebacks = manager.list_writebacks(machine_name)
            print(json.dumps(writebacks, indent=2))
        
        elif command == "create" and len(sys.argv) > 3:
            machine_name = sys.argv[2]
            image_name = sys.argv[3]
            result = manager.create_writeback(machine_name, image_name)
            print(json.dumps(result, indent=2))
        
        elif command == "discard" and len(sys.argv) > 2:
            writeback_name = sys.argv[2]
            result = manager.discard_writeback(writeback_name)
            print(json.dumps(result, indent=2))
        
        elif command == "keep" and len(sys.argv) > 3:
            writeback_name = sys.argv[2]
            keep = sys.argv[3].lower() in ['true', '1', 'yes']
            result = manager.set_keep_flag(writeback_name, keep)
            print(json.dumps(result, indent=2))
        
        elif command == "cleanup":
            max_age = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            result = manager.cleanup_old_writebacks(max_age)
            print(json.dumps(result, indent=2))
        
        else:
            print("Usage:")
            print("  python writeback_manager.py list [machine_name]")
            print("  python writeback_manager.py create <machine_name> <image_name>")
            print("  python writeback_manager.py discard <writeback_name>")
            print("  python writeback_manager.py keep <writeback_name> <true|false>")
            print("  python writeback_manager.py cleanup [max_age_days]")
            sys.exit(1)
    else:
        # Default: list all writebacks
        writebacks = manager.list_writebacks()
        print(json.dumps(writebacks, indent=2))

