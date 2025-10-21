"""
Network Configuration API Endpoints

Manage network settings for ggNet server.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import subprocess
import re

router = APIRouter(prefix="/network", tags=["network"])


# Schemas
class NetworkInterface(BaseModel):
    name: str
    ip_address: str | None = None
    netmask: str | None = None
    gateway: str | None = None
    dns: List[str] = []
    dhcp: bool = True
    status: str = "down"


class NetworkConfig(BaseModel):
    interfaces: List[NetworkInterface]
    hostname: str
    domain: str | None = None


class NetworkConfigUpdate(BaseModel):
    interface: str
    ip_address: str | None = None
    netmask: str | None = None
    gateway: str | None = None
    dns: List[str] | None = None
    dhcp: bool = True


# Endpoints
@router.get("/config", response_model=NetworkConfig)
async def get_network_config():
    """Get current network configuration"""
    
    interfaces = []
    
    try:
        # Get hostname
        result = subprocess.run(['hostname'], capture_output=True, text=True)
        hostname = result.stdout.strip()
        
        # Get network interfaces using ip command
        result = subprocess.run(['ip', '-br', 'addr'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                iface_name = parts[0]
                status = parts[1]
                ip_info = parts[2] if len(parts) > 2 else None
                
                # Skip loopback
                if iface_name == 'lo':
                    continue
                
                # Parse IP address
                ip_address = None
                if ip_info and '/' in ip_info:
                    ip_address = ip_info.split('/')[0]
                
                interfaces.append(NetworkInterface(
                    name=iface_name,
                    ip_address=ip_address,
                    status=status,
                    dhcp=True  # Detect DHCP from /etc/network/interfaces or NetworkManager
                ))
        
        return NetworkConfig(
            interfaces=interfaces,
            hostname=hostname
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get network config: {str(e)}")


@router.post("/config")
async def update_network_config(config: NetworkConfigUpdate):
    """
    Update network configuration
    
    WARNING: This modifies system network settings!
    Requires root permissions or sudo.
    """
    
    # TODO: Implement actual network configuration
    # This requires:
    # 1. Writing to /etc/network/interfaces (Debian) or /etc/netplan/ (Ubuntu)
    # 2. Restarting networking service
    # 3. Proper error handling for network changes
    
    # For now, return success (mock)
    return {
        "success": True,
        "message": f"Network configuration for {config.interface} would be updated",
        "config": config.dict(),
        "warning": "Network configuration changes require manual intervention for safety"
    }


@router.get("/interfaces")
async def list_interfaces():
    """List all network interfaces"""
    
    try:
        result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
        
        interfaces = []
        for line in result.stdout.split('\n'):
            # Match interface lines like: "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>"
            match = re.match(r'^\d+:\s+(\w+):', line)
            if match:
                iface_name = match.group(1)
                if iface_name != 'lo':  # Skip loopback
                    interfaces.append({
                        "name": iface_name,
                        "state": "UP" if "UP" in line else "DOWN"
                    })
        
        return {"interfaces": interfaces}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list interfaces: {str(e)}")


@router.get("/dns")
async def get_dns_servers():
    """Get DNS server configuration"""
    
    try:
        dns_servers = []
        
        # Read /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if line.strip().startswith('nameserver'):
                    parts = line.split()
                    if len(parts) >= 2:
                        dns_servers.append(parts[1])
        
        return {"dns_servers": dns_servers}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get DNS servers: {str(e)}")


@router.get("/routes")
async def get_routes():
    """Get routing table"""
    
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        
        routes = []
        for line in result.stdout.strip().split('\n'):
            if line:
                routes.append({"route": line})
        
        return {"routes": routes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get routes: {str(e)}")
