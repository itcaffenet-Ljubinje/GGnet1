"""
Tests for Core Services Integration

Test DHCP, TFTP, NFS, and PXE services integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.core.services import CoreServicesManager, initialize_core_services
from src.core.dhcp_server import DHCPConfig
from src.core.tftp_server import TFTPConfig
from src.core.nfs_server import NFSConfig
from src.core.pxe_manager import PXEConfig


class TestCoreServicesManager:
    """Test CoreServicesManager functionality"""
    
    def test_initialization(self):
        """Test services manager initialization"""
        manager = CoreServicesManager()
        
        assert not manager.is_initialized()
        assert manager.get_dhcp_server() is None
        assert manager.get_tftp_server() is None
        assert manager.get_nfs_server() is None
        assert manager.get_pxe_manager() is None
    
    @pytest.mark.asyncio
    async def test_initialize_services(self):
        """Test services initialization"""
        manager = CoreServicesManager()
        
        dhcp_config = DHCPConfig(
            interface="eth0",
            server_ip="192.168.1.1",
            dhcp_start="192.168.1.100",
            dhcp_end="192.168.1.200",
            subnet_mask="255.255.255.0",
            gateway="192.168.1.1",
            dns_servers=["8.8.8.8"],
            tftp_server="192.168.1.1"
        )
        
        tftp_config = TFTPConfig(
            root_dir="/tmp/tftpboot",
            listen_address="127.0.0.1"
        )
        
        nfs_config = NFSConfig(
            root_dir="/tmp/nfs",
            network="127.0.0.0/8"
        )
        
        pxe_config = PXEConfig(
            tftp_root="/tmp/tftpboot"
        )
        
        await manager.initialize(
            dhcp_config=dhcp_config,
            tftp_config=tftp_config,
            nfs_config=nfs_config,
            pxe_config=pxe_config
        )
        
        assert manager.is_initialized()
        assert manager.get_dhcp_server() is not None
        assert manager.get_tftp_server() is not None
        assert manager.get_nfs_server() is not None
        assert manager.get_pxe_manager() is not None
    
    def test_get_status(self):
        """Test status reporting"""
        manager = CoreServicesManager()
        
        status = manager.get_status()
        
        assert "dhcp" in status
        assert "tftp" in status
        assert "nfs" in status
        assert "pxe" in status
        
        assert status["dhcp"]["initialized"] is False
        assert status["dhcp"]["running"] is False
        assert status["tftp"]["initialized"] is False
        assert status["tftp"]["running"] is False
        assert status["nfs"]["initialized"] is False
        assert status["nfs"]["running"] is False
        assert status["pxe"]["initialized"] is False
        assert status["pxe"]["running"] is False


class TestCoreServicesIntegration:
    """Test core services integration with FastAPI"""
    
    @pytest.mark.asyncio
    async def test_initialize_core_services(self):
        """Test core services initialization function"""
        with patch('src.core.services.init_services_manager') as mock_init:
            mock_manager = AsyncMock()
            mock_init.return_value = mock_manager
            
            manager = await initialize_core_services()
            
            assert manager == mock_manager
            mock_manager.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_services_manager_singleton(self):
        """Test services manager singleton pattern"""
        from src.core.services import get_services_manager, init_services_manager
        
        # Initially no manager
        assert get_services_manager() is None
        
        # Initialize manager
        manager = init_services_manager()
        assert manager is not None
        
        # Should return same instance
        assert get_services_manager() == manager


class TestServiceConfigurations:
    """Test service configuration classes"""
    
    def test_dhcp_config(self):
        """Test DHCP configuration"""
        config = DHCPConfig(
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
        
        assert config.interface == "eth0"
        assert config.server_ip == "192.168.1.1"
        assert config.dhcp_start == "192.168.1.100"
        assert config.dhcp_end == "192.168.1.200"
        assert config.subnet_mask == "255.255.255.0"
        assert config.gateway == "192.168.1.1"
        assert config.dns_servers == ["8.8.8.8", "8.8.4.4"]
        assert config.tftp_server == "192.168.1.1"
        assert config.enable_pxe is True
        assert config.boot_file == "pxelinux.0"  # Default value
    
    def test_tftp_config(self):
        """Test TFTP configuration"""
        config = TFTPConfig(
            root_dir="/var/lib/tftpboot",
            listen_address="0.0.0.0",
            port=69,
            enable_write=False,
            timeout=300
        )
        
        assert config.root_dir == "/var/lib/tftpboot"
        assert config.listen_address == "0.0.0.0"
        assert config.port == 69
        assert config.enable_write is False
        assert config.timeout == 300
    
    def test_nfs_config(self):
        """Test NFS configuration"""
        config = NFSConfig(
            exports_file="/etc/exports",
            root_dir="/srv/nfs/ggnet",
            network="192.168.1.0/24",
            options="rw,sync,no_subtree_check,no_root_squash"
        )
        
        assert config.exports_file == "/etc/exports"
        assert config.root_dir == "/srv/nfs/ggnet"
        assert config.network == "192.168.1.0/24"
        assert config.options == "rw,sync,no_subtree_check,no_root_squash"
    
    def test_pxe_config(self):
        """Test PXE configuration"""
        config = PXEConfig(
            tftp_root="/var/lib/tftpboot",
            boot_file="pxelinux.0",
            menu_file="menu.c32"
        )
        
        assert config.tftp_root == "/var/lib/tftpboot"
        assert config.boot_file == "pxelinux.0"
        assert config.menu_file == "menu.c32"


class TestServiceErrorHandling:
    """Test error handling in core services"""
    
    @pytest.mark.asyncio
    async def test_start_without_initialization(self):
        """Test starting services without initialization"""
        manager = CoreServicesManager()
        
        with pytest.raises(RuntimeError, match="Core services not initialized"):
            await manager.start_all()
    
    @pytest.mark.asyncio
    async def test_double_initialization(self):
        """Test double initialization warning"""
        manager = CoreServicesManager()
        
        dhcp_config = DHCPConfig(
            interface="eth0",
            server_ip="192.168.1.1",
            dhcp_start="192.168.1.100",
            dhcp_end="192.168.1.200",
            subnet_mask="255.255.255.0",
            gateway="192.168.1.1",
            dns_servers=["8.8.8.8"],
            tftp_server="192.168.1.1"
        )
        
        # First initialization
        await manager.initialize(dhcp_config=dhcp_config)
        assert manager.is_initialized()
        
        # Second initialization should warn but not fail
        with patch('src.core.services.logger') as mock_logger:
            await manager.initialize(dhcp_config=dhcp_config)
            mock_logger.warning.assert_called_with("Core services already initialized")
