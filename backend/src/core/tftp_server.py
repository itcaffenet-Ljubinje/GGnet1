"""
TFTP Server for ggNet

Provides TFTP service for PXE boot files.
Uses tftpd-hpa or atftpd for actual TFTP functionality.
"""

import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TFTPConfig:
    """TFTP server configuration"""
    root_dir: str = "/var/lib/tftpboot"
    listen_address: str = "0.0.0.0"
    port: int = 69
    enable_write: bool = False
    timeout: int = 300


class TFTPServer:
    """
    TFTP Server Manager
    
    Manages TFTP server configuration and operations.
    Supports tftpd-hpa and atftpd.
    """
    
    def __init__(self, config: TFTPConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.using_tftpd_hpa = self._check_tftpd_hpa()
        
    def _check_tftpd_hpa(self) -> bool:
        """Check if tftpd-hpa is available"""
        try:
            subprocess.run(
                ["in.tftpd", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def start(self):
        """Start TFTP server"""
        if self.using_tftpd_hpa:
            await self._start_tftpd_hpa()
        else:
            raise RuntimeError(
                "tftpd-hpa not found. "
                "Please install: sudo apt-get install tftpd-hpa"
            )
    
    async def _start_tftpd_hpa(self):
        """Start tftpd-hpa TFTP server"""
        logger.info("Starting tftpd-hpa TFTP server...")
        
        # Ensure root directory exists
        root_dir = Path(self.config.root_dir)
        root_dir.mkdir(parents=True, exist_ok=True)
        
        # Start in.tftpd
        cmd = [
            "in.tftpd",
            "-l",  # Log to syslog
            "-v",  # Verbose
            "-a", self.config.listen_address,
            "-s", self.config.root_dir,  # Secure mode
        ]
        
        if not self.config.enable_write:
            cmd.append("-w")  # Enable write
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(
            f"TFTP server started on {self.config.listen_address}:{self.config.port} "
            f"(PID: {self.process.pid})"
        )
    
    async def stop(self):
        """Stop TFTP server"""
        if self.process:
            logger.info(f"Stopping TFTP server (PID: {self.process.pid})...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("TFTP server stopped")
    
    async def restart(self):
        """Restart TFTP server"""
        await self.stop()
        await asyncio.sleep(1)
        await self.start()
    
    def is_running(self) -> bool:
        """Check if TFTP server is running"""
        if self.process:
            return self.process.poll() is None
        return False
    
    async def upload_file(
        self,
        local_path: str,
        remote_path: str
    ):
        """
        Upload file to TFTP server
        
        Args:
            local_path: Local file path
            remote_path: Remote file path on TFTP server
        """
        logger.info(f"Uploading {local_path} to {remote_path}")
        
        # Copy file to TFTP root directory
        local_file = Path(local_path)
        tftp_root = Path(self.config.root_dir)
        remote_file = tftp_root / remote_path
        
        # Create parent directories if needed
        remote_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(local_file, remote_file)
        
        logger.info(f"File uploaded: {remote_file}")
    
    async def download_file(
        self,
        remote_path: str,
        local_path: str
    ):
        """
        Download file from TFTP server
        
        Args:
            remote_path: Remote file path on TFTP server
            local_path: Local file path
        """
        logger.info(f"Downloading {remote_path} to {local_path}")
        
        # Copy file from TFTP root directory
        tftp_root = Path(self.config.root_dir)
        remote_file = tftp_root / remote_path
        local_file = Path(local_path)
        
        if not remote_file.exists():
            raise FileNotFoundError(f"File not found: {remote_path}")
        
        # Copy file
        import shutil
        shutil.copy2(remote_file, local_file)
        
        logger.info(f"File downloaded: {local_file}")
    
    async def delete_file(self, remote_path: str):
        """
        Delete file from TFTP server
        
        Args:
            remote_path: Remote file path on TFTP server
        """
        logger.info(f"Deleting {remote_path}")
        
        tftp_root = Path(self.config.root_dir)
        remote_file = tftp_root / remote_path
        
        if remote_file.exists():
            remote_file.unlink()
            logger.info(f"File deleted: {remote_file}")
        else:
            logger.warning(f"File not found: {remote_path}")
    
    async def list_files(self, remote_dir: str = "") -> list[str]:
        """
        List files in TFTP server directory
        
        Args:
            remote_dir: Remote directory path (empty for root)
        
        Returns:
            List of file paths
        """
        tftp_root = Path(self.config.root_dir)
        remote_path = tftp_root / remote_dir
        
        if not remote_path.exists():
            return []
        
        files = []
        for item in remote_path.rglob("*"):
            if item.is_file():
                files.append(str(item.relative_to(tftp_root)))
        
        return files
    
    async def setup_pxe_boot(self):
        """Setup PXE boot files"""
        logger.info("Setting up PXE boot files...")
        
        tftp_root = Path(self.config.root_dir)
        
        # Create necessary directories
        (tftp_root / "pxelinux.cfg").mkdir(parents=True, exist_ok=True)
        (tftp_root / "menu").mkdir(parents=True, exist_ok=True)
        
        # Create default PXE boot configuration
        default_cfg = tftp_root / "pxelinux.cfg" / "default"
        
        if not default_cfg.exists():
            with open(default_cfg, "w") as f:
                f.write("""# ggNet PXE Boot Configuration
DEFAULT menu.c32
PROMPT 0
TIMEOUT 50
ONTIMEOUT local

LABEL local
    MENU LABEL Boot from local disk
    LOCALBOOT 0

LABEL ggnet
    MENU LABEL Boot from ggNet
    KERNEL menu/ggnet-kernel
    APPEND initrd=menu/ggnet-initrd.img
""")
        
        logger.info("PXE boot files setup complete")


# Singleton instance
_tftp_server: Optional[TFTPServer] = None


def get_tftp_server() -> Optional[TFTPServer]:
    """Get TFTP server instance"""
    return _tftp_server


def init_tftp_server(config: TFTPConfig) -> TFTPServer:
    """Initialize TFTP server"""
    global _tftp_server
    _tftp_server = TFTPServer(config)
    return _tftp_server

