"""
NFS Server for ggNet

Provides NFS service for diskless client boot images.
Manages NFS exports and shares.
"""

import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NFSConfig:
    """NFS server configuration"""
    exports_file: str = "/etc/exports"
    root_dir: str = "/srv/nfs/ggnet"
    network: str = "192.168.1.0/24"
    options: str = "rw,sync,no_subtree_check,no_root_squash"


class NFSServer:
    """
    NFS Server Manager
    
    Manages NFS server configuration and operations.
    """
    
    def __init__(self, config: NFSConfig):
        self.config = config
        self.using_nfs_kernel_server = self._check_nfs_kernel_server()
        
    def _check_nfs_kernel_server(self) -> bool:
        """Check if nfs-kernel-server is available"""
        try:
            subprocess.run(
                ["exportfs", "-v"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def start(self):
        """Start NFS server"""
        if not self.using_nfs_kernel_server:
            raise RuntimeError(
                "nfs-kernel-server not found. "
                "Please install: sudo apt-get install nfs-kernel-server"
            )
        
        logger.info("Starting NFS server...")
        
        # Ensure root directory exists
        root_dir = Path(self.config.root_dir)
        root_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup exports
        await self._setup_exports()
        
        # Export filesystems
        await self._exportfs("-ra")
        
        logger.info("NFS server started")
    
    async def stop(self):
        """Stop NFS server"""
        logger.info("Stopping NFS server...")
        
        # Unexport all filesystems
        await self._exportfs("-ua")
        
        logger.info("NFS server stopped")
    
    async def restart(self):
        """Restart NFS server"""
        await self.stop()
        await asyncio.sleep(1)
        await self.start()
    
    async def _exportfs(self, flags: str):
        """Run exportfs command"""
        cmd = ["exportfs", flags]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"exportfs failed: {result.stderr}")
            raise RuntimeError(f"exportfs failed: {result.stderr}")
    
    async def _setup_exports(self):
        """Setup NFS exports configuration"""
        logger.info("Setting up NFS exports...")
        
        # Read current exports
        exports_path = Path(self.config.exports_file)
        
        if exports_path.exists():
            with open(exports_path, "r") as f:
                exports_content = f.read()
        else:
            exports_content = ""
        
        # Add ggNet export if not present
        export_line = f"{self.config.root_dir} {self.config.network}({self.config.options})"
        
        if export_line not in exports_content:
            with open(exports_path, "a") as f:
                f.write(f"\n# ggNet NFS Export\n{export_line}\n")
        
        logger.info(f"NFS export configured: {export_line}")
    
    async def add_export(
        self,
        path: str,
        network: Optional[str] = None,
        options: Optional[str] = None
    ):
        """
        Add NFS export
        
        Args:
            path: Export path
            network: Network or host (default: from config)
            options: Export options (default: from config)
        """
        network = network or self.config.network
        options = options or self.config.options
        
        export_line = f"{path} {network}({options})"
        
        # Add to exports file
        exports_path = Path(self.config.exports_file)
        
        with open(exports_path, "a") as f:
            f.write(f"\n# ggNet Export\n{export_line}\n")
        
        # Export immediately
        await self._exportfs("-ra")
        
        logger.info(f"NFS export added: {export_line}")
    
    async def remove_export(self, path: str):
        """
        Remove NFS export
        
        Args:
            path: Export path
        """
        exports_path = Path(self.config.exports_file)
        
        if not exports_path.exists():
            return
        
        # Remove export from file
        with open(exports_path, "r") as f:
            lines = f.readlines()
        
        with open(exports_path, "w") as f:
            skip_next = False
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue
                
                if line.strip().startswith(f"{path} "):
                    # Skip this line and next comment if present
                    skip_next = True
                    continue
                
                f.write(line)
        
        # Unexport
        await self._exportfs("-ua")
        await self._exportfs("-ra")
        
        logger.info(f"NFS export removed: {path}")
    
    async def list_exports(self) -> list[dict]:
        """
        List active NFS exports
        
        Returns:
            List of export dictionaries
        """
        result = subprocess.run(
            ["exportfs", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"exportfs failed: {result.stderr}")
            return []
        
        exports = []
        for line in result.stdout.split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    exports.append({
                        "path": parts[0],
                        "network": parts[1],
                        "options": parts[2] if len(parts) > 2 else ""
                    })
        
        return exports
    
    async def create_image_share(self, image_name: str) -> str:
        """
        Create NFS share for image
        
        Args:
            image_name: Image name
        
        Returns:
            NFS share path
        """
        image_path = Path(self.config.root_dir) / "images" / image_name
        image_path.mkdir(parents=True, exist_ok=True)
        
        # Add export
        await self.add_export(
            str(image_path),
            self.config.network,
            self.config.options
        )
        
        logger.info(f"Image share created: {image_path}")
        
        return str(image_path)
    
    async def create_writeback_share(self, machine_id: str) -> str:
        """
        Create NFS share for machine writeback
        
        Args:
            machine_id: Machine ID
        
        Returns:
            NFS share path
        """
        writeback_path = Path(self.config.root_dir) / "writebacks" / machine_id
        writeback_path.mkdir(parents=True, exist_ok=True)
        
        # Add export
        await self.add_export(
            str(writeback_path),
            self.config.network,
            self.config.options
        )
        
        logger.info(f"Writeback share created: {writeback_path}")
        
        return str(writeback_path)
    
    async def remove_share(self, path: str):
        """
        Remove NFS share
        
        Args:
            path: Share path
        """
        await self.remove_export(path)
        
        # Remove directory if empty
        share_path = Path(path)
        if share_path.exists():
            try:
                share_path.rmdir()
                logger.info(f"Share directory removed: {path}")
            except OSError:
                logger.warning(f"Share directory not empty: {path}")


# Singleton instance
_nfs_server: Optional[NFSServer] = None


def get_nfs_server() -> Optional[NFSServer]:
    """Get NFS server instance"""
    return _nfs_server


def init_nfs_server(config: NFSConfig) -> NFSServer:
    """Initialize NFS server"""
    global _nfs_server
    _nfs_server = NFSServer(config)
    return _nfs_server

