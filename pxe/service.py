#!/usr/bin/env python3
"""
ggNet PXE Service Manager

Manages PXE boot allocations and generates per-machine iPXE scripts.
Integrates with backend pxe_manager core service.

Usage:
    python pxe/service.py generate-all        # Generate configs for all machines
    python pxe/service.py generate MAC_ADDR   # Generate config for specific machine
    python pxe/service.py serve               # Run HTTP server for iPXE scripts
    python pxe/service.py sync                # Sync from ggNet backend database
"""

import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

# Add backend src to path
BACKEND_SRC = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))

try:
    from sqlalchemy import select
    from db.base import init_db, async_session_maker
    from db.models import Machine, Image
    from config.settings import settings
except ImportError as e:
    print(f"⚠️  Warning: Could not import backend modules: {e}")
    print("   Running in standalone mode with mock data")
    settings = None


class PXEServiceManager:
    """Manages PXE configurations and iPXE script generation"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).parent / "tftp"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Server configuration
        self.server_ip = "192.168.1.1"
        self.server_port = 5000
        self.tftp_root = "/var/lib/tftpboot"
        
    async def load_machines_from_db(self) -> List[Dict]:
        """Load all machines from ggNet backend database"""
        if not settings:
            print("⚠️  Backend not available, using mock data")
            return self._get_mock_machines()
        
        machines = []
        async with async_session_maker() as session:
            result = await session.execute(select(Machine))
            db_machines = result.scalars().all()
            
            for m in db_machines:
                machines.append({
                    "id": m.id,
                    "name": m.name,
                    "mac_address": m.mac_address,
                    "ip_address": m.ip_address,
                    "image_name": m.image_name or "default",
                    "keep_writeback": m.keep_writeback
                })
        
        return machines
    
    def _get_mock_machines(self) -> List[Dict]:
        """Mock machine data for testing"""
        return [
            {
                "id": 1,
                "name": "Gaming PC 1",
                "mac_address": "00:11:22:33:44:01",
                "ip_address": "192.168.1.101",
                "image_name": "Windows 10 Gaming",
                "keep_writeback": False
            },
            {
                "id": 2,
                "name": "Gaming PC 2",
                "mac_address": "00:11:22:33:44:02",
                "ip_address": "192.168.1.102",
                "image_name": "Windows 10 Gaming",
                "keep_writeback": False
            },
        ]
    
    def generate_ipxe_script(
        self, 
        machine: Dict,
        boot_mode: str = "auto"
    ) -> str:
        """
        Generate machine-specific iPXE boot script
        
        Args:
            machine: Machine dict with mac_address, name, image_name
            boot_mode: 'uefi', 'bios', or 'auto'
        
        Returns:
            iPXE script content as string
        """
        mac = machine["mac_address"]
        name = machine["name"]
        image = machine["image_name"]
        keep_wb = machine["keep_writeback"]
        
        # Normalize image name for iSCSI target
        iscsi_target = image.lower().replace(" ", "-")
        
        script = f"""#!ipxe
################################################################################
# ggNet Machine-Specific Boot Script
# 
# Machine: {name}
# MAC: {mac}
# Image: {image}
# Keep Writeback: {keep_wb}
# Generated: {datetime.now().isoformat()}
################################################################################

echo ========================================
echo   ggNet Boot: {name}
echo ========================================
echo.
echo MAC: {mac}
echo IP: ${{net0/ip}}
echo Image: {image}
echo Keep Writeback: {keep_wb}
echo.

# Server configuration
set ggnet-server {self.server_ip}
set ggnet-port {self.server_port}
set image-name {iscsi_target}

# Detect boot mode
iseq ${{platform}} efi && set boot-mode uefi || set boot-mode bios
echo Boot mode: ${{boot-mode}}
echo.

"""

        if boot_mode == "uefi" or boot_mode == "auto":
            script += """
# UEFI Boot
:uefi_boot
set kernel vmlinuz-uefi
set initrd initrd-uefi.img
goto boot_kernel

"""

        if boot_mode == "bios" or boot_mode == "auto":
            script += """
# BIOS Boot
:bios_boot
set kernel vmlinuz
set initrd initrd.img
goto boot_kernel

"""

        script += f"""
:boot_kernel
# Kernel parameters
set kernel-params initrd=${{initrd}} root=iscsi:${{ggnet-server}}::::iqn.2025.net.ggnet:${{image-name}} ip=dhcp rw quiet splash

# Keep writeback parameter
"""

        if keep_wb:
            script += """set kernel-params ${kernel-params} ggnet.keep_writeback=1
"""

        script += f"""
# Machine ID for writeback identification
set kernel-params ${{kernel-params}} ggnet.machine_id={machine['id']} ggnet.mac={mac}

# Load and boot
echo Loading kernel: ${{kernel}}
kernel http://${{ggnet-server}}:${{ggnet-port}}/boot/${{kernel}} ${{kernel-params}} || goto boot_failed
echo Loading initrd: ${{initrd}}
initrd http://${{ggnet-server}}:${{ggnet-port}}/boot/${{initrd}} || goto boot_failed
echo Booting {name}...
boot || goto boot_failed

:boot_failed
echo.
echo ========================================
echo   BOOT FAILED: {name}
echo ========================================
echo.
echo Troubleshooting:
echo - Check ggNet server: {self.server_ip}:{self.server_port}
echo - Verify image exists: {image}
echo - Check network connectivity
echo.
echo Press any key to try local boot...
prompt
exit

################################################################################
# Machine-specific notes:
# - This script is auto-generated by pxe/service.py
# - Edit via ggNet backend API, don't modify manually
# - To regenerate: python pxe/service.py generate {mac}
################################################################################
"""

        return script
    
    async def generate_machine_config(self, mac_address: str) -> bool:
        """Generate iPXE config for specific machine"""
        machines = await self.load_machines_from_db()
        
        machine = next((m for m in machines if m["mac_address"].upper() == mac_address.upper()), None)
        if not machine:
            print(f"❌ Machine with MAC {mac_address} not found")
            return False
        
        # Generate script
        script = self.generate_ipxe_script(machine)
        
        # Write to file
        output_file = self.output_dir / f"{mac_address.replace(':', '-')}.ipxe"
        output_file.write_text(script)
        
        print(f"✅ Generated: {output_file}")
        print(f"   Machine: {machine['name']}")
        print(f"   Image: {machine['image_name']}")
        
        return True
    
    async def generate_all_configs(self) -> int:
        """Generate iPXE configs for all machines"""
        machines = await self.load_machines_from_db()
        
        print(f"📋 Generating iPXE configs for {len(machines)} machines...")
        print()
        
        count = 0
        for machine in machines:
            script = self.generate_ipxe_script(machine)
            mac = machine["mac_address"].replace(":", "-")
            output_file = self.output_dir / f"{mac}.ipxe"
            output_file.write_text(script)
            
            print(f"✅ {machine['name']:<20} ({machine['mac_address']}) → {output_file.name}")
            count += 1
        
        print()
        print(f"✅ Generated {count} machine configs")
        print(f"📁 Output directory: {self.output_dir}")
        
        return count
    
    async def generate_dhcp_config(self) -> str:
        """Generate DHCP configuration from machines"""
        machines = await self.load_machines_from_db()
        
        dhcp_config = f"""# ggNet Auto-Generated DHCP Configuration
# Generated: {datetime.now().isoformat()}
# Machines: {len(machines)}

"""
        
        for machine in machines:
            mac = machine["mac_address"]
            ip = machine["ip_address"] or f"192.168.1.{100 + machine['id']}"
            name = machine["name"].lower().replace(" ", "-")
            
            dhcp_config += f"""
host {name} {{
    hardware ethernet {mac};
    fixed-address {ip};
    option host-name "{name}";
    filename "http://{self.server_ip}:{self.server_port}/pxe/{mac}.ipxe";
}}
"""
        
        return dhcp_config
    
    async def sync_from_backend(self) -> bool:
        """Sync configurations from backend database"""
        print("🔄 Syncing from ggNet backend database...")
        
        if not settings:
            await init_db()
        
        # Generate all configs
        count = await self.generate_all_configs()
        
        # Generate DHCP config
        dhcp_config = await self.generate_dhcp_config()
        dhcp_file = Path(__file__).parent / "dhcp" / "generated-dhcp.conf"
        dhcp_file.parent.mkdir(parents=True, exist_ok=True)
        dhcp_file.write_text(dhcp_config)
        
        print(f"✅ Generated DHCP config: {dhcp_file}")
        print()
        print("📝 Next steps:")
        print(f"   1. Review configs in: {self.output_dir}")
        print(f"   2. Copy DHCP config to: /etc/dhcp/dhcpd.conf")
        print(f"   3. Restart DHCP: systemctl restart isc-dhcp-server")
        print(f"   4. Test PXE boot on client machines")
        
        return True
    
    def serve_http(self, port: int = 8080):
        """
        Run simple HTTP server for iPXE scripts
        
        This is a development helper. In production, use Nginx or Apache.
        """
        import http.server
        import socketserver
        
        os.chdir(self.output_dir)
        
        Handler = http.server.SimpleHTTPRequestHandler
        
        print(f"🌐 Starting HTTP server for iPXE scripts...")
        print(f"   URL: http://0.0.0.0:{port}")
        print(f"   Directory: {self.output_dir}")
        print(f"   Press Ctrl+C to stop")
        print()
        
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ggNet PXE Service Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pxe/service.py sync
  python pxe/service.py generate-all
  python pxe/service.py generate 00:11:22:33:44:01
  python pxe/service.py serve
        """
    )
    
    parser.add_argument(
        "command",
        choices=["sync", "generate", "generate-all", "serve"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "mac_address",
        nargs="?",
        help="MAC address for 'generate' command"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for iPXE scripts"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP server (default: 8080)"
    )
    
    args = parser.parse_args()
    
    # Create service manager
    manager = PXEServiceManager(output_dir=args.output)
    
    # Execute command
    if args.command == "sync":
        await manager.sync_from_backend()
    
    elif args.command == "generate-all":
        await manager.generate_all_configs()
    
    elif args.command == "generate":
        if not args.mac_address:
            print("❌ MAC address required for 'generate' command")
            print("   Usage: python pxe/service.py generate 00:11:22:33:44:01")
            sys.exit(1)
        await manager.generate_machine_config(args.mac_address)
    
    elif args.command == "serve":
        manager.serve_http(port=args.port)


if __name__ == "__main__":
    import os
    asyncio.run(main())

