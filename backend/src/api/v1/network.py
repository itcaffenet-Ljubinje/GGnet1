"""
Network API Endpoints

Manage DHCP, PXE boot, and network configuration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.services import get_services_manager

router = APIRouter(prefix="/network", tags=["network"])


# Schemas
class NetworkConfig(BaseModel):
    server_ip: str
    dhcp_start: str
    dhcp_end: str
    subnet_mask: str
    gateway: str
    dns_servers: list[str]


class DHCPReservation(BaseModel):
    mac_address: str
    ip_address: str
    hostname: Optional[str] = None


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
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    dhcp_server = services_manager.get_dhcp_server()
    
    if not dhcp_server:
        raise HTTPException(
            status_code=503,
            detail="DHCP server not initialized"
        )
    
    leases = await dhcp_server.get_leases()
    
    return {
        "leases": leases,
        "total": len(leases)
    }


@router.post("/dhcp/reservations")
async def add_dhcp_reservation(reservation: DHCPReservation):
    """Add static DHCP reservation"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    dhcp_server = services_manager.get_dhcp_server()
    
    if not dhcp_server:
        raise HTTPException(
            status_code=503,
            detail="DHCP server not initialized"
        )
    
    await dhcp_server.add_reservation(
        reservation.mac_address,
        reservation.ip_address,
        reservation.hostname
    )
    
    return {
        "success": True,
        "message": "DHCP reservation added"
    }


@router.delete("/dhcp/reservations/{mac_address}")
async def remove_dhcp_reservation(mac_address: str):
    """Remove static DHCP reservation"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    dhcp_server = services_manager.get_dhcp_server()
    
    if not dhcp_server:
        raise HTTPException(
            status_code=503,
            detail="DHCP server not initialized"
        )
    
    await dhcp_server.remove_reservation(mac_address)
    
    return {
        "success": True,
        "message": "DHCP reservation removed"
    }


@router.get("/services/status")
async def get_services_status():
    """Get status of network services"""
    try:
        services_manager = get_services_manager()
        
        if not services_manager:
            return {
                "dhcp": {"initialized": False, "running": False, "status": "not_initialized"},
                "tftp": {"initialized": False, "running": False, "status": "not_initialized"},
                "nfs": {"initialized": False, "running": False, "status": "not_initialized"},
                "pxe": {"initialized": False, "running": False, "status": "not_initialized"}
            }
        
        return services_manager.get_status()
    except Exception as e:
        return {
            "dhcp": {"initialized": False, "running": False, "status": "error", "error": str(e)},
            "tftp": {"initialized": False, "running": False, "status": "error", "error": str(e)},
            "nfs": {"initialized": False, "running": False, "status": "error", "error": str(e)},
            "pxe": {"initialized": False, "running": False, "status": "error", "error": str(e)}
        }


@router.post("/services/dhcp/restart")
async def restart_dhcp_server():
    """Restart DHCP server"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    dhcp_server = services_manager.get_dhcp_server()
    
    if not dhcp_server:
        raise HTTPException(
            status_code=503,
            detail="DHCP server not initialized"
        )
    
    await dhcp_server.restart()
    
    return {
        "success": True,
        "message": "DHCP server restarted"
    }


@router.post("/services/tftp/restart")
async def restart_tftp_server():
    """Restart TFTP server"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    tftp_server = services_manager.get_tftp_server()
    
    if not tftp_server:
        raise HTTPException(
            status_code=503,
            detail="TFTP server not initialized"
        )
    
    await tftp_server.restart()
    
    return {
        "success": True,
        "message": "TFTP server restarted"
    }


@router.post("/services/nfs/restart")
async def restart_nfs_server():
    """Restart NFS server"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    nfs_server = services_manager.get_nfs_server()
    
    if not nfs_server:
        raise HTTPException(
            status_code=503,
            detail="NFS server not initialized"
        )
    
    await nfs_server.restart()
    
    return {
        "success": True,
        "message": "NFS server restarted"
    }


@router.post("/services/restart-all")
async def restart_all_services():
    """Restart all network services"""
    services_manager = get_services_manager()
    
    if not services_manager:
        raise HTTPException(
            status_code=503,
            detail="Services manager not initialized"
        )
    
    await services_manager.restart_all()
    
    return {
        "success": True,
        "message": "All network services restarted"
    }
