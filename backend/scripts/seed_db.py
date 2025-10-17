#!/usr/bin/env python3
"""
Database Seed Script

Creates sample machines and images for testing.
Run from backend/src/ directory:
    python ../scripts/seed_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select
from db.base import init_db, async_session_maker
from db.models import Machine, Image, User
from datetime import datetime


async def seed_database():
    """Create sample data"""
    
    print("🌱 Seeding database...")
    
    # Initialize database
    await init_db()
    
    async with async_session_maker() as session:
        # Check if data already exists
        result = await session.execute(select(Machine))
        existing_machines = result.scalars().all()
        
        if existing_machines:
            print("ℹ️  Database already contains data. Skipping seed.")
            return
        
        # Create sample machines
        machines = [
            Machine(
                name="Gaming PC 1",
                mac_address="00:11:22:33:44:01",
                ip_address="192.168.1.101",
                status="offline",
                image_name="Windows 10 Gaming",
                writeback_size=0,
                keep_writeback=False
            ),
            Machine(
                name="Gaming PC 2",
                mac_address="00:11:22:33:44:02",
                ip_address="192.168.1.102",
                status="offline",
                image_name="Windows 10 Gaming",
                writeback_size=0,
                keep_writeback=False
            ),
            Machine(
                name="Gaming PC 3",
                mac_address="00:11:22:33:44:03",
                ip_address="192.168.1.103",
                status="online",
                image_name="Windows 11 Pro",
                writeback_size=2147483648,  # 2 GB
                keep_writeback=False,
                last_boot=datetime.utcnow()
            ),
            Machine(
                name="Admin Workstation",
                mac_address="00:11:22:33:44:04",
                ip_address="192.168.1.104",
                status="offline",
                image_name=None,
                writeback_size=0,
                keep_writeback=True
            ),
        ]
        
        # Create sample images
        images = [
            Image(
                name="Windows 10 Gaming",
                path="os/windows10_gaming.img",
                type="os",
                size_bytes=107374182400,  # 100 GB
                active_snapshot_id=None
            ),
            Image(
                name="Windows 11 Pro",
                path="os/windows11_pro.img",
                type="os",
                size_bytes=107374182400,  # 100 GB
                active_snapshot_id=None
            ),
            Image(
                name="Steam Library",
                path="games/steam_common.img",
                type="game",
                size_bytes=536870912000,  # 500 GB
                active_snapshot_id=None
            ),
        ]
        
        # Create sample admin user
        # Note: In production, use proper password hashing!
        users = [
            User(
                username="admin",
                password_hash="$2b$12$dummy_hash_replace_with_real_hash",  # TODO: Use real bcrypt
                role="admin"
            ),
        ]
        
        # Add all to session
        for machine in machines:
            session.add(machine)
        
        for image in images:
            session.add(image)
        
        for user in users:
            session.add(user)
        
        # Commit
        await session.commit()
        
        print(f"✅ Created {len(machines)} machines")
        print(f"✅ Created {len(images)} images")
        print(f"✅ Created {len(users)} users")
        print("\n📊 Sample Data:")
        print("   Machines:")
        for m in machines:
            print(f"     - {m.name} ({m.mac_address}) - {m.status}")
        print("   Images:")
        for i in images:
            print(f"     - {i.name} ({i.type}) - {i.size_bytes / (1024**3):.1f} GB")
        print("\n✅ Database seeded successfully!")
        print("\n🚀 Start the server with:")
        print("   cd src && python main.py")
        print("\n🌐 Then visit:")
        print("   http://localhost:5000/docs")
        print("   http://localhost:5000/api/v1/machines")


if __name__ == "__main__":
    asyncio.run(seed_database())

