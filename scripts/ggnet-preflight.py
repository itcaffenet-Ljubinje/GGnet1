#!/usr/bin/env python3
"""
ggNet Preflight Check Tool
Inspired by ggRock's ggrock-preflight

Performs system checks and updates before starting ggNet service.

Usage:
    python3 ggnet-preflight.py start    - Run preflight checks and updates
    python3 ggnet-preflight.py cleanup  - Cleanup after service stop
"""

import sys
import subprocess
import os
from pathlib import Path


def check_ggnet_installed():
    """Check if ggNet service is installed and enabled"""
    print("Checking for ggnet service...")
    try:
        result = subprocess.run(
            ['systemctl', 'is-enabled', 'ggnet-backend'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or 'disabled' in result.stdout.lower():
            print("ggnet is not installed. Exiting.")
            sys.exit(0)
        
        print("✓ ggnet service is enabled")
        return True
    except FileNotFoundError:
        print("Warning: systemctl not found")
        return False


def check_headers():
    """Check for Linux headers matching current kernel"""
    print(f"Checking for Linux headers for {os.uname().release}...")
    
    headers_path = f"/usr/src/linux-headers-{os.uname().release}"
    
    if os.path.exists(headers_path):
        print(f"✓ Found headers for {os.uname().release}. Update not required.")
        return False
    else:
        print(f"⚠ Could not find headers for {os.uname().release}.")
        return True


def check_dns():
    """Verify DNS is configured"""
    print("Verifying DNS is set...")
    
    resolv_conf = Path('/etc/resolv.conf')
    if not resolv_conf.exists():
        print("⚠ /etc/resolv.conf not found. Creating...")
        with open(resolv_conf, 'w') as f:
            f.write("nameserver 8.8.8.8\n")
        return True
    
    with open(resolv_conf, 'r') as f:
        content = f.read()
        if 'nameserver' not in content.lower():
            print("⚠ No nameservers found in resolv.conf. Adding...")
            with open(resolv_conf, 'a') as f:
                f.write("nameserver 8.8.8.8\n")
            return True
    
    print("✓ DNS is configured")
    return False


def update_headers():
    """Install missing Linux headers"""
    print("Installing missing linux headers...")
    
    kernel_release = os.uname().release
    
    try:
        # Update package lists
        subprocess.run(
            ['apt-get', 'update'],
            check=True,
            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
        )
        
        # Install headers
        subprocess.run(
            ['apt-get', 'install', '-y', f'linux-headers-{kernel_release}'],
            check=True,
            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
        )
        
        # Verify installation
        headers_path = f"/usr/src/linux-headers-{kernel_release}"
        if os.path.exists(headers_path):
            print(f"✓ Successfully installed headers for {kernel_release}")
            
            # Load ZFS module
            try:
                subprocess.run(['modprobe', 'zfs'], check=True)
                print("✓ ZFS module loaded")
            except subprocess.CalledProcessError:
                print("⚠ Failed to load ZFS module")
            
            return True
        else:
            print(f"✗ Failed to install headers for {kernel_release}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing headers: {e}")
        return False


def create_error_html(html_body: str):
    """Create error HTML page"""
    html_dir = Path('/opt/ggnet/html')
    html_dir.mkdir(parents=True, exist_ok=True)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>ggNet Preflight</title>
    <meta http-equiv="refresh" content="5">
    <style>
       body {{
           background-color: #3B4852;
           color: white;
           font-size: 16px;
       }}
   </style>
</head>
<body>
    {html_body}
</body>
</html>
"""
    
    html_file = html_dir / 'ggnet_preflight.html'
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"✓ Created preflight HTML: {html_file}")


def create_nginx_preflight_conf():
    """Create temporary nginx config for preflight page"""
    nginx_conf = Path('/etc/nginx/sites-available/ggnet')
    backup_conf = Path('/etc/nginx/sites-available/ggnet.preflight.backup')
    
    # Backup existing config
    if nginx_conf.exists():
        import shutil
        shutil.copy2(nginx_conf, backup_conf)
        print(f"✓ Backed up nginx config to {backup_conf}")
    
    # Create preflight config
    preflight_config = """
server {
  listen      80 default_server;
  listen      [::]:80 default_server;

  root /opt/ggnet/html;
  index ggnet_preflight.html;

  location / {
    add_header Cache-Control 'no-store';
    return 301  https://$host$request_uri;
  }
}

server {
  listen      443 ssl http2 default_server;
  listen      [::]:443 ssl http2 default_server;

  root /opt/ggnet/html;
  index ggnet_preflight.html;
  
  include snippets/ggnet-cert.conf;

  ssl_session_timeout 1d;
  ssl_session_cache shared:MozSSL:10m;
  ssl_session_tickets off;

  ssl_dhparam /etc/nginx/ssl/dhparam.pem;

  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
  ssl_prefer_server_ciphers off;

  location / {
    add_header Cache-Control 'no-store';
    try_files $uri $uri/ /;
  }
}
"""
    
    with open(nginx_conf, 'w') as f:
        f.write(preflight_config)
    
    print(f"✓ Created preflight nginx config")
    
    # Reload nginx
    try:
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        print("✓ Nginx reloaded")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Failed to reload nginx: {e}")


def cleanup_preflight():
    """Restore original nginx config"""
    print("Cleaning up preflight...")
    
    nginx_conf = Path('/etc/nginx/sites-available/ggnet')
    backup_conf = Path('/etc/nginx/sites-available/ggnet.preflight.backup')
    
    if backup_conf.exists():
        import shutil
        shutil.move(backup_conf, nginx_conf)
        print(f"✓ Restored original nginx config")
        
        try:
            subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
            print("✓ Nginx reloaded")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Failed to reload nginx: {e}")
    
    print("✓ Cleanup complete")


def run_preflight_checks():
    """Run all preflight checks"""
    print("=" * 60)
    print("  ggNet Preflight Checks")
    print("=" * 60)
    print()
    
    preflight_failed = False
    header_update_required = False
    html_body = ""
    
    # Check if ggNet is installed
    if not check_ggnet_installed():
        return False
    
    # Check headers
    if check_headers():
        header_update_required = True
        preflight_failed = True
        html_body += "<p>* A kernel change has been detected since the last configuration. The linux headers will be updated.</p><br>"
    
    # Check DNS
    if check_dns():
        preflight_failed = True
    
    if preflight_failed:
        html_body = "<h3>ggNet has detected the following preflight errors. Please wait while they are automatically corrected.</h3>" + html_body
        html_body += "<br><p>ggNet will automatically finish loading when this process is complete. This may take a few minutes.</p><br>"
    
    return preflight_failed, header_update_required, html_body


def run_preflight_updates(preflight_failed: bool, header_update_required: bool, html_body: str):
    """Run preflight updates"""
    if preflight_failed:
        create_nginx_preflight_conf()
        create_error_html(html_body)
    
    if header_update_required:
        update_headers()


def run_preflight_complete(preflight_failed: bool):
    """Complete preflight process"""
    if preflight_failed:
        print()
        print("Restarting ggnet service...")
        try:
            subprocess.run(['systemctl', 'restart', 'ggnet-backend'], check=True)
            print("✓ ggnet service restarted")
            
            import time
            print("Waiting 10 seconds for service to start...")
            time.sleep(10)
        except subprocess.CalledProcessError as e:
            print(f"⚠ Failed to restart ggnet service: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 ggnet-preflight.py start    - Run preflight checks and updates")
        print("  python3 ggnet-preflight.py cleanup  - Cleanup after service stop")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        preflight_failed, header_update_required, html_body = run_preflight_checks()
        run_preflight_updates(preflight_failed, header_update_required, html_body)
        run_preflight_complete(preflight_failed)
        print()
        print("=" * 60)
        print("  Preflight Complete")
        print("=" * 60)
        
    elif command == 'cleanup':
        cleanup_preflight()
        
    else:
        print(f"Unknown command: {command}")
        print("Usage: start|cleanup")
        sys.exit(1)


if __name__ == '__main__':
    main()

