"""
Core Services Manager for ggNet

Manages initialization and lifecycle of DHCP, TFTP, NFS, and PXE services.
"""

import asyncio
import logging
from typing import Optional

from .dhcp_server import DHCPServer, DHCPConfig, init_dhcp_server
from .tftp_server import TFTPServer, TFTPConfig, init_tftp_server
from .nfs_server import NFSServer, NFSConfig, init_nfs_server
from .pxe_manager import PXEManager, PXEConfig, init_pxe_manager

logger = logging.getLogger(__name__)


class CoreServicesManager:
    """
    Core Services Manager
    
    Manages all core network services (DHCP, TFTP, NFS, PXE).
    """
    
    def __init__(self):
        self.dhcp_server: Optional[DHCPServer] = None
        self.tftp_server: Optional[TFTPServer] = None
        self.nfs_server: Optional[NFSServer] = None
        self.pxe_manager: Optional[PXEManager] = None
        self._initialized = False
    
    async def initialize(
        self,
        dhcp_config: Optional[DHCPConfig] = None,
        tftp_config: Optional[TFTPConfig] = None,
        nfs_config: Optional[NFSConfig] = None,
        pxe_config: Optional[PXEConfig] = None
    ):
        """
        Initialize all core services
        
        Args:
            dhcp_config: DHCP server configuration
            tftp_config: TFTP server configuration
            nfs_config: NFS server configuration
            pxe_config: PXE manager configuration
        """
        if self._initialized:
            logger.warning("Core services already initialized")
            return
        
        logger.info("Initializing core services...")
        
        # Initialize DHCP server
        if dhcp_config:
            self.dhcp_server = init_dhcp_server(dhcp_config)
            logger.info("DHCP server initialized")
        
        # Initialize TFTP server
        if tftp_config:
            self.tftp_server = init_tftp_server(tftp_config)
            logger.info("TFTP server initialized")
        
        # Initialize NFS server
        if nfs_config:
            self.nfs_server = init_nfs_server(nfs_config)
            logger.info("NFS server initialized")
        
        # Initialize PXE manager
        if pxe_config:
            self.pxe_manager = init_pxe_manager(pxe_config)
            logger.info("PXE manager initialized")
        
        self._initialized = True
        logger.info("Core services initialization complete")
    
    async def start_all(self):
        """Start all initialized services"""
        if not self._initialized:
            raise RuntimeError("Core services not initialized. Call initialize() first.")
        
        logger.info("Starting all core services...")
        
        # Start services in order
        if self.dhcp_server:
            await self.dhcp_server.start()
            logger.info("DHCP server started")
        
        if self.tftp_server:
            await self.tftp_server.start()
            logger.info("TFTP server started")
        
        if self.nfs_server:
            await self.nfs_server.start()
            logger.info("NFS server started")
        
        if self.pxe_manager:
            await self.pxe_manager.setup_boot_files()
            logger.info("PXE manager setup complete")
        
        logger.info("All core services started successfully")
    
    async def stop_all(self):
        """Stop all running services"""
        logger.info("Stopping all core services...")
        
        # Stop services in reverse order
        if self.pxe_manager:
            # PXE manager doesn't need stopping
            pass
        
        if self.nfs_server:
            await self.nfs_server.stop()
            logger.info("NFS server stopped")
        
        if self.tftp_server:
            await self.tftp_server.stop()
            logger.info("TFTP server stopped")
        
        if self.dhcp_server:
            await self.dhcp_server.stop()
            logger.info("DHCP server stopped")
        
        logger.info("All core services stopped")
    
    async def restart_all(self):
        """Restart all services"""
        logger.info("Restarting all core services...")
        await self.stop_all()
        await asyncio.sleep(2)
        await self.start_all()
        logger.info("All core services restarted")
    
    def get_status(self) -> dict:
        """Get status of all services"""
        try:
            return {
                "dhcp": {
                    "initialized": self.dhcp_server is not None,
                    "running": self.dhcp_server.is_running() if self.dhcp_server else False
                },
                "tftp": {
                    "initialized": self.tftp_server is not None,
                    "running": self.tftp_server.is_running() if self.tftp_server else False
                },
                "nfs": {
                    "initialized": self.nfs_server is not None,
                    "running": True if self.nfs_server else False
                },
                "pxe": {
                    "initialized": self.pxe_manager is not None,
                    "running": True if self.pxe_manager else False
                }
            }
        except Exception as e:
            logger.error(f"Error getting services status: {e}")
            return {
                "dhcp": {"initialized": False, "running": False, "error": str(e)},
                "tftp": {"initialized": False, "running": False, "error": str(e)},
                "nfs": {"initialized": False, "running": False, "error": str(e)},
                "pxe": {"initialized": False, "running": False, "error": str(e)}
            }
    
    def is_initialized(self) -> bool:
        """Check if services are initialized"""
        return self._initialized
    
    def get_dhcp_server(self) -> Optional[DHCPServer]:
        """Get DHCP server instance"""
        return self.dhcp_server
    
    def get_tftp_server(self) -> Optional[TFTPServer]:
        """Get TFTP server instance"""
        return self.tftp_server
    
    def get_nfs_server(self) -> Optional[NFSServer]:
        """Get NFS server instance"""
        return self.nfs_server
    
    def get_pxe_manager(self) -> Optional[PXEManager]:
        """Get PXE manager instance"""
        return self.pxe_manager


# Global services manager instance
_services_manager: Optional[CoreServicesManager] = None


def get_services_manager() -> Optional[CoreServicesManager]:
    """Get global services manager instance"""
    return _services_manager


def init_services_manager() -> CoreServicesManager:
    """Initialize global services manager"""
    global _services_manager
    _services_manager = CoreServicesManager()
    return _services_manager


async def initialize_core_services():
    """
    Initialize core services with default configuration
    
    This function should be called during application startup.
    """
    logger.info("Initializing core services with default configuration...")
    
    # Create default configurations
    dhcp_config = DHCPConfig(
        interface="eth0",
        server_ip="192.168.1.1",
        dhcp_start="192.168.1.100",
        dhcp_end="192.168.1.200",
        subnet_mask="255.255.255.0",
        gateway="192.168.1.1",
        dns_servers=["8.8.8.8", "8.8.4.4"],
        tftp_server="192.168.1.1",
        enable_pxe=True
    )
    
    tftp_config = TFTPConfig(
        root_dir="/var/lib/tftpboot",
        listen_address="0.0.0.0",
        port=69
    )
    
    nfs_config = NFSConfig(
        root_dir="/srv/nfs/ggnet",
        network="192.168.1.0/24"
    )
    
    pxe_config = PXEConfig(
        tftp_root="/var/lib/tftpboot"
    )
    
    # Initialize services manager
    services_manager = init_services_manager()
    
    # Initialize all services
    await services_manager.initialize(
        dhcp_config=dhcp_config,
        tftp_config=tftp_config,
        nfs_config=nfs_config,
        pxe_config=pxe_config
    )
    
    logger.info("Core services initialization complete")
    return services_manager


async def start_core_services():
    """Start all core services"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise RuntimeError("Services manager not initialized")
    
    await services_manager.start_all()


async def stop_core_services():
    """Stop all core services"""
    services_manager = get_services_manager()
    
    if services_manager:
        await services_manager.stop_all()
