"""
PXE Boot Manager for ggNet

Manages PXE boot configuration and boot files.
"""

import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PXEConfig:
    """PXE boot configuration"""
    tftp_root: str = "/var/lib/tftpboot"
    boot_file: str = "pxelinux.0"
    menu_file: str = "menu.c32"


class PXEManager:
    """
    PXE Boot Manager
    
    Manages PXE boot configuration and files.
    """
    
    def __init__(self, config: PXEConfig):
        self.config = config
        self.tftp_root = Path(config.tftp_root)
        
    async def setup_boot_files(self):
        """Setup PXE boot files"""
        logger.info("Setting up PXE boot files...")
        
        # Create necessary directories
        (self.tftp_root / "pxelinux.cfg").mkdir(parents=True, exist_ok=True)
        (self.tftp_root / "menu").mkdir(parents=True, exist_ok=True)
        
        # Create default PXE boot configuration
        await self.create_default_config()
        
        logger.info("PXE boot files setup complete")
    
    async def create_default_config(self):
        """Create default PXE boot configuration"""
        default_cfg = self.tftp_root / "pxelinux.cfg" / "default"
        
        config_content = """# ggNet PXE Boot Configuration
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
"""
        
        with open(default_cfg, "w") as f:
            f.write(config_content)
        
        logger.info(f"Default PXE config created: {default_cfg}")
    
    async def create_machine_config(
        self,
        mac_address: str,
        image_name: str,
        nfs_server: str,
        nfs_path: str
    ):
        """
        Create PXE boot configuration for machine
        
        Args:
            mac_address: Machine MAC address (XX:XX:XX:XX:XX:XX)
            image_name: Image name to boot
            nfs_server: NFS server IP
            nfs_path: NFS path to image
        """
        # Convert MAC address to PXE format (01-XX-XX-XX-XX-XX-XX)
        mac_clean = mac_address.replace(":", "-").lower()
        pxe_mac = f"01-{mac_clean}"
        
        # Create machine-specific config file
        config_file = self.tftp_root / "pxelinux.cfg" / pxe_mac
        
        config_content = f"""# PXE Boot Configuration for {mac_address}
# Image: {image_name}

DEFAULT menu.c32
PROMPT 0
TIMEOUT 10
ONTIMEOUT boot

LABEL boot
    MENU LABEL Boot {image_name}
    KERNEL menu/{image_name}/kernel
    APPEND initrd=menu/{image_name}/initrd.img nfsroot={nfs_server}:{nfs_path} ip=dhcp
"""
        
        with open(config_file, "w") as f:
            f.write(config_content)
        
        logger.info(
            f"PXE config created for {mac_address}: {config_file}"
        )
    
    async def update_machine_config(
        self,
        mac_address: str,
        image_name: str,
        nfs_server: str,
        nfs_path: str
    ):
        """
        Update PXE boot configuration for machine
        
        Args:
            mac_address: Machine MAC address
            image_name: New image name to boot
            nfs_server: NFS server IP
            nfs_path: NFS path to image
        """
        await self.create_machine_config(
            mac_address,
            image_name,
            nfs_server,
            nfs_path
        )
    
    async def delete_machine_config(self, mac_address: str):
        """
        Delete PXE boot configuration for machine
        
        Args:
            mac_address: Machine MAC address
        """
        # Convert MAC address to PXE format
        mac_clean = mac_address.replace(":", "-").lower()
        pxe_mac = f"01-{mac_clean}"
        
        # Delete machine-specific config file
        config_file = self.tftp_root / "pxelinux.cfg" / pxe_mac
        
        if config_file.exists():
            config_file.unlink()
            logger.info(f"PXE config deleted for {mac_address}: {config_file}")
        else:
            logger.warning(f"PXE config not found: {config_file}")
    
    async def upload_boot_files(
        self,
        image_name: str,
        kernel_path: str,
        initrd_path: str
    ):
        """
        Upload boot files for image
        
        Args:
            image_name: Image name
            kernel_path: Path to kernel file
            initrd_path: Path to initrd file
        """
        # Create image directory
        image_dir = self.tftp_root / "menu" / image_name
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy kernel
        import shutil
        shutil.copy2(kernel_path, image_dir / "kernel")
        
        # Copy initrd
        shutil.copy2(initrd_path, image_dir / "initrd.img")
        
        logger.info(f"Boot files uploaded for {image_name}: {image_dir}")
    
    async def delete_boot_files(self, image_name: str):
        """
        Delete boot files for image
        
        Args:
            image_name: Image name
        """
        image_dir = self.tftp_root / "menu" / image_name
        
        if image_dir.exists():
            import shutil
            shutil.rmtree(image_dir)
            logger.info(f"Boot files deleted for {image_name}: {image_dir}")
        else:
            logger.warning(f"Boot files not found: {image_dir}")
    
    async def list_boot_files(self) -> list[str]:
        """
        List available boot files
        
        Returns:
            List of image names with boot files
        """
        menu_dir = self.tftp_root / "menu"
        
        if not menu_dir.exists():
            return []
        
        images = []
        for item in menu_dir.iterdir():
            if item.is_dir():
                kernel_file = item / "kernel"
                if kernel_file.exists():
                    images.append(item.name)
        
        return images


# Singleton instance
_pxe_manager: Optional[PXEManager] = None


def get_pxe_manager() -> Optional[PXEManager]:
    """Get PXE manager instance"""
    return _pxe_manager


def init_pxe_manager(config: PXEConfig) -> PXEManager:
    """Initialize PXE manager"""
    global _pxe_manager
    _pxe_manager = PXEManager(config)
    return _pxe_manager
