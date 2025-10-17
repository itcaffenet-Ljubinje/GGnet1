"""
Network API Endpoints

Manage DHCP, PXE boot, and network configuration.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/network", tags=["network"])


# Schemas
class NetworkConfig(BaseModel):
    server_ip: str
    dhcp_start: str
    dhcp_end: str
    subnet_mask: str
    gateway: str
    dns_servers: list[str]


# Endpoints
@router.get("/config")
async def get_network_config():
    """Get current network configuration"""
    # TODO: Read from actual network configuration files
    return {
        "server_ip": "192.168.1.1",
        "dhcp_start": "192.168.1.100",
        "dhcp_end": "192.168.1.200",
        "subnet_mask": "255.255.255.0",
        "gateway": "192.168.1.1",
        "dns_servers": ["8.8.8.8", "8.8.4.4"]
    }


@router.put("/config")
async def update_network_config(config: NetworkConfig):
    """
    Update network configuration
    
    TODO: Update dnsmasq or ISC DHCP configuration
    TODO: Reload network services
    """
    return {
        "success": True,
        "message": "Network configuration updated"
    }


@router.get("/dhcp/leases")
async def get_dhcp_leases():
    """Get active DHCP leases"""
    # TODO: Parse dnsmasq leases file or ISC DHCP leases
    return {
        "leases": []
    }

