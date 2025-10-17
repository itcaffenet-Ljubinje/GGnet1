#!/usr/bin/env python3
"""
ggNet Image Management Tool
Inspired by ggRock's ggrock-img

Manages ZFS images, snapshots, and exports.

Usage:
    python3 ggnet-img.py <command> [options]

Commands:
    get_sendsize    - Estimate backup size
    list_snapshots  - List all snapshots for an image
    send            - Send image to stdout (for backup)
    receive         - Receive image from stdin (for restore)
    export          - Export image to VHD/VHDX/VMDK/QCOW2/VDI/RAW
"""

import sys
import subprocess
import argparse
import uuid
import os
from pathlib import Path


def create_new_guid():
    """Generate a new GUID for export operations"""
    return str(uuid.uuid4())


def get_zvol_name(pool_name: str, image_name: str) -> str:
    """Get ZFS volume name for an image"""
    return f"{pool_name}/ggnet/images/{image_name}"


def get_qemu_format(format_name: str) -> str:
    """Map format name to QEMU format"""
    format_map = {
        'vhd': 'vpc',
        'vhdx': 'vhdx',
        'vmdk': 'vmdk',
        'qcow2': 'qcow2',
        'vdi': 'vdi',
        'raw': 'raw',
    }
    return format_map.get(format_name.lower(), '')


def get_latest_snapshot_fullname(pool_name: str, image_name: str) -> str:
    """Get the latest snapshot full name for an image"""
    zvol_name = get_zvol_name(pool_name, image_name)
    
    try:
        result = subprocess.run(
            ['zfs', 'list', '-t', 'snapshot', '-o', 'name', '-s', 'creation', '-r', zvol_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        snapshots = result.stdout.strip().split('\n')
        if len(snapshots) > 1:  # First line is header
            return snapshots[-1]
        return ""
    except subprocess.CalledProcessError:
        return ""


def get_sendsize(pool_name: str, image_name: str):
    """Estimate the size of a backup"""
    latest_snapshot = get_latest_snapshot_fullname(pool_name, image_name)
    
    if not latest_snapshot:
        print("Error: Image doesn't have any snapshots.", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = subprocess.run(
            ['zfs', 'send', '-nPR', latest_snapshot],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract size from output
        for line in result.stdout.split('\n'):
            if 'size' in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    print(parts[1])
                    return
        
        print("Error: Could not determine send size", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_snapshots(pool_name: str, image_name: str):
    """List all snapshots for an image"""
    zvol_name = get_zvol_name(pool_name, image_name)
    
    try:
        result = subprocess.run(
            ['zfs', 'list', '-t', 'snapshot', '-Hp', '-r', '-o', 
             'creation,guid,name,com.ggnet:snapshot:name', zvol_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("CREATION_TIMESTAMP\tGUID\tNAME\tCOMMENT")
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    # Extract snapshot name (after @)
                    snapshot_name = parts[2].split('@')[-1] if '@' in parts[2] else parts[2]
                    print(f"{parts[0]}\t{parts[1]}\t{snapshot_name}\t{parts[3]}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def send_image(pool_name: str, image_name: str, first_snapshot_name: str = None):
    """Send image to stdout (for backup)"""
    latest_snapshot = get_latest_snapshot_fullname(pool_name, image_name)
    
    if not latest_snapshot:
        print("Error: Source image doesn't have any snapshots.", file=sys.stderr)
        sys.exit(1)
    
    cmd = ['zfs', 'send', '-R']
    if first_snapshot_name:
        cmd.extend(['-I', first_snapshot_name])
    cmd.append(latest_snapshot)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def receive_image(pool_name: str, image_name: str, force: bool = False):
    """Receive image from stdin (for restore)"""
    zvol_name = get_zvol_name(pool_name, image_name)
    
    cmd = ['zfs', 'receive', '-s']
    if force:
        cmd.append('-F')
    cmd.append(zvol_name)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def export_image(pool_name: str, image_name: str, output_format: str, 
                 output_filename: str, snapshot_name: str = None):
    """Export image to VHD/VHDX/VMDK/QCOW2/VDI/RAW"""
    zvol_name = get_zvol_name(pool_name, image_name)
    
    qemu_format = get_qemu_format(output_format)
    if not qemu_format:
        print(f"Error: Wrong output format: {output_format}", file=sys.stderr)
        print(f"Supported formats: vhd, vhdx, vmdk, qcow2, vdi, raw", file=sys.stderr)
        sys.exit(1)
    
    # Determine snapshot to export
    if snapshot_name:
        snapshot_fullname = f"{zvol_name}@{snapshot_name}"
    else:
        snapshot_fullname = get_latest_snapshot_fullname(pool_name, image_name)
        if not snapshot_fullname:
            print("Error: Source image doesn't have any snapshots.", file=sys.stderr)
            sys.exit(1)
    
    # Create temporary clone for export
    export_guid = create_new_guid()
    export_zvol_name = f"{pool_name}/ggnet/export/{export_guid}"
    
    try:
        # Clone snapshot
        subprocess.run(['zfs', 'clone', '-p', snapshot_fullname, export_zvol_name], check=True)
        
        # Wait for ZFS to complete clone (async operation)
        import time
        time.sleep(1)
        
        # Convert to target format using qemu-img
        subprocess.run([
            'qemu-img', 'convert', '-p', '-f', 'raw',
            f'/dev/zvol/{export_zvol_name}', '-O', qemu_format, output_filename
        ], check=True)
        
        print(f"Export complete: {output_filename}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up temporary clone
        try:
            subprocess.run(['zfs', 'destroy', export_zvol_name], check=False)
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description='ggNet Image Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  Estimate backup size:
    ggnet-img get_sendsize -p pool0 -i games

  List all image snapshots:
    ggnet-img list_snapshots -p pool0 -i games

  Backup image to file:
    ggnet-img send -p pool0 -i games > games.img

  Restore image from backup:
    ggnet-img receive -p pool0 -i games < games.img

  Backup with progress:
    ggnet-img send -p pool0 -i games | pv > games.img

  Restore with progress:
    cat games.img | pv | ggnet-img receive -p pool0 -i games

  Clone to another server via SSH:
    ggnet-img send -p pool0 -i games | pv | ssh host2 ggnet-img receive -p pool0 -i games

  Incremental backup:
    ggnet-img send -p pool0 -i games -I last_sent_snapshot | pv | ssh host2 ggnet-img receive -p pool0 -i games

  Export to VHD:
    ggnet-img export -p pool0 -i games -t vhd -f games.vhd

  Export to VMDK:
    ggnet-img export -p pool0 -i games -t vmdk -f games.vmdk

  Export specific snapshot:
    ggnet-img export -p pool0 -i games -t qcow2 -f games.qcow2 -s snapshot_name
        """
    )
    
    parser.add_argument('command', choices=['get_sendsize', 'list_snapshots', 'send', 'receive', 'export'],
                        help='Command to execute')
    parser.add_argument('-p', '--pool', required=True, help='ZFS pool name')
    parser.add_argument('-i', '--image', required=True, help='Image name')
    parser.add_argument('-I', '--incremental', help='First snapshot name for incremental backup (send only)')
    parser.add_argument('-F', '--force', action='store_true', help='Force receive (receive only)')
    parser.add_argument('-t', '--format', help='Output format: vhd, vhdx, vmdk, qcow2, vdi, raw (export only)')
    parser.add_argument('-f', '--filename', help='Output filename (export only)')
    parser.add_argument('-s', '--snapshot', help='Specific snapshot to export (export only)')
    
    args = parser.parse_args()
    
    # Validate arguments based on command
    if args.command == 'export':
        if not args.format or not args.filename:
            print("Error: --format and --filename are required for export command", file=sys.stderr)
            sys.exit(1)
        if args.incremental or args.force:
            print("Error: --incremental and --force are not valid for export command", file=sys.stderr)
            sys.exit(1)
    elif args.command == 'send':
        if args.format or args.filename or args.snapshot:
            print("Error: --format, --filename, and --snapshot are not valid for send command", file=sys.stderr)
            sys.exit(1)
    elif args.command == 'receive':
        if args.incremental or args.format or args.filename or args.snapshot:
            print("Error: --incremental, --format, --filename, and --snapshot are not valid for receive command", file=sys.stderr)
            sys.exit(1)
    else:  # get_sendsize or list_snapshots
        if args.incremental or args.force or args.format or args.filename or args.snapshot:
            print("Error: Invalid arguments for this command", file=sys.stderr)
            sys.exit(1)
    
    # Execute command
    if args.command == 'get_sendsize':
        get_sendsize(args.pool, args.image)
    elif args.command == 'list_snapshots':
        list_snapshots(args.pool, args.image)
    elif args.command == 'send':
        send_image(args.pool, args.image, args.incremental)
    elif args.command == 'receive':
        receive_image(args.pool, args.image, args.force)
    elif args.command == 'export':
        export_image(args.pool, args.image, args.format, args.filename, args.snapshot)


if __name__ == '__main__':
    main()

