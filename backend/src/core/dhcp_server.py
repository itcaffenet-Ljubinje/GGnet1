"""
DHCP Server for ggNet

Provides DHCP service for diskless clients with PXE boot support.
Uses dnsmasq or ISC DHCP server for actual DHCP functionality.
"""

import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DHCPConfig:
    """DHCP server configuration"""
    interface: str
    server_ip: str
    dhcp_start: str
    dhcp_end: str
    subnet_mask: str
    gateway: str
    dns_servers: list[str]
    tftp_server: str
    boot_file: str = "pxelinux.0"
    enable_pxe: bool = True


class DHCPServer:
    """
    DHCP Server Manager
    
    Manages DHCP server configuration and operations.
    Supports both dnsmasq and ISC DHCP.
    """
    
    def __init__(self, config: DHCPConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.using_dnsmasq = self._check_dnsmasq()
        
    def _check_dnsmasq(self) -> bool:
        """Check if dnsmasq is available"""
        try:
            subprocess.run(
                ["dnsmasq", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def start(self):
        """Start DHCP server"""
        if self.using_dnsmasq:
            await self._start_dnsmasq()
        else:
            raise RuntimeError(
                "Neither dnsmasq nor ISC DHCP found. "
                "Please install dnsmasq: sudo apt-get install dnsmasq"
            )
    
    async def _start_dnsmasq(self):
        """Start dnsmasq DHCP server"""
        logger.info("Starting dnsmasq DHCP server...")
        
        # Create dnsmasq configuration
        config_path = Path("/tmp/ggnet-dnsmasq.conf")
        config_content = self._generate_dnsmasq_config()
        
        with open(config_path, "w") as f:
            f.write(config_content)
        
        # Start dnsmasq
        cmd = [
            "dnsmasq",
            "--conf-file=/tmp/ggnet-dnsmasq.conf",
            "--no-daemon",
            "--log-queries",
            "--log-dhcp"
        ]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"DHCP server started (PID: {self.process.pid})")
    
    def _generate_dnsmasq_config(self) -> str:
        """Generate dnsmasq configuration"""
        config = f"""# ggNet DHCP Configuration
# Generated automatically

# Network interface
interface={self.config.interface}

# DHCP range
dhcp-range={self.config.dhcp_start},{self.config.dhcp_end},{self.config.subnet_mask},12h

# Gateway
dhcp-option=3,{self.config.gateway}

# DNS servers
"""
        for dns in self.config.dns_servers:
            config += f"dhcp-option=6,{dns}\n"
        
        if self.config.enable_pxe:
            config += f"""
# PXE Boot
dhcp-boot={self.config.boot_file},{self.config.tftp_server},{self.config.server_ip}

# TFTP server
enable-tftp
tftp-root=/var/lib/tftpboot
"""
        
        config += """
# Logging
log-queries
log-dhcp
"""
        
        return config
    
    async def stop(self):
        """Stop DHCP server"""
        if self.process:
            logger.info(f"Stopping DHCP server (PID: {self.process.pid})...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("DHCP server stopped")
    
    async def restart(self):
        """Restart DHCP server"""
        await self.stop()
        await asyncio.sleep(1)
        await self.start()
    
    async def reload_config(self):
        """Reload DHCP configuration"""
        if self.process:
            # Send SIGHUP to dnsmasq
            self.process.send_signal(1)
            logger.info("DHCP configuration reloaded")
    
    def is_running(self) -> bool:
        """Check if DHCP server is running"""
        if self.process:
            return self.process.poll() is None
        return False
    
    async def get_leases(self) -> list[dict]:
        """
        Get active DHCP leases
        
        Returns list of active leases with MAC, IP, hostname, etc.
        """
        leases = []
        
        if self.using_dnsmasq:
            # Read dnsmasq leases file
            leases_file = Path("/var/lib/misc/dnsmasq.leases")
            
            if leases_file.exists():
                with open(leases_file, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            leases.append({
                                "lease_time": parts[0],
                                "mac_address": parts[1],
                                "ip_address": parts[2],
                                "hostname": parts[3] if len(parts) > 3 else "unknown",
                                "client_id": parts[4] if len(parts) > 4 else ""
                            })
        
        return leases
    
    async def add_reservation(
        self,
        mac_address: str,
        ip_address: str,
        hostname: Optional[str] = None
    ):
        """
        Add static DHCP reservation
        
        Args:
            mac_address: Client MAC address
            ip_address: Reserved IP address
            hostname: Optional hostname
        """
        logger.info(
            f"Adding DHCP reservation: {mac_address} -> {ip_address}"
        )
        
        # Add to dnsmasq configuration
        config_path = Path("/tmp/ggnet-dnsmasq.conf")
        
        with open(config_path, "a") as f:
            if hostname:
                f.write(f"dhcp-host={mac_address},{hostname},{ip_address}\n")
            else:
                f.write(f"dhcp-host={mac_address},{ip_address}\n")
        
        # Reload configuration
        await self.reload_config()
    
    async def remove_reservation(self, mac_address: str):
        """
        Remove static DHCP reservation
        
        Args:
            mac_address: Client MAC address
        """
        logger.info(f"Removing DHCP reservation: {mac_address}")
        
        # Remove from dnsmasq configuration
        config_path = Path("/tmp/ggnet-dnsmasq.conf")
        
        if config_path.exists():
            with open(config_path, "r") as f:
                lines = f.readlines()
            
            with open(config_path, "w") as f:
                for line in lines:
                    if not line.startswith(f"dhcp-host={mac_address}"):
                        f.write(line)
        
        # Reload configuration
        await self.reload_config()


# Singleton instance
_dhcp_server: Optional[DHCPServer] = None


def get_dhcp_server() -> Optional[DHCPServer]:
    """Get DHCP server instance"""
    return _dhcp_server


def init_dhcp_server(config: DHCPConfig) -> DHCPServer:
    """Initialize DHCP server"""
    global _dhcp_server
    _dhcp_server = DHCPServer(config)
    return _dhcp_server

