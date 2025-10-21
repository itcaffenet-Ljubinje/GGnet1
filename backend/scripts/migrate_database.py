#!/usr/bin/env python3
"""
Database Migration Script for ggNet

This script migrates the old database schema to the new schema.
Run this on production server to fix 'no such column: images.image_id' error.

USAGE:
    cd /opt/ggnet/backend
    python scripts/migrate_database.py

WARNING: This will backup and recreate the database!
"""

import sqlite3
import os
import shutil
from datetime import datetime


def backup_database(db_path: str) -> str:
    """Create backup of existing database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    else:
        print(f"⚠️  Database not found: {db_path}")
        return None


def migrate_database(db_path: str):
    """Migrate database schema"""
    
    print("=" * 60)
    print("ggNet Database Migration Script")
    print("=" * 60)
    
    # Step 1: Backup
    print("\n[1/4] Creating backup...")
    backup_path = backup_database(db_path)
    
    if not os.path.exists(db_path):
        print(f"⚠️  No existing database found. Will create new one.")
        print(f"    Run: python -m src.main")
        return
    
    # Step 2: Check if migration is needed
    print("\n[2/4] Checking schema...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT image_id FROM images LIMIT 1")
        print("✅ Schema is up-to-date! No migration needed.")
        conn.close()
        return
    except sqlite3.OperationalError as e:
        if "no such column: images.image_id" in str(e):
            print("⚠️  OLD SCHEMA DETECTED - Migration required!")
        else:
            raise
    
    # Step 3: Export old data
    print("\n[3/4] Exporting old data...")
    
    # Get old images
    cursor.execute("SELECT * FROM images")
    old_images = cursor.fetchall()
    cursor.execute("PRAGMA table_info(images)")
    old_columns = [row[1] for row in cursor.fetchall()]
    
    print(f"    Found {len(old_images)} images")
    print(f"    Old columns: {old_columns}")
    
    conn.close()
    
    # Step 4: Recreate database
    print("\n[4/4] Recreating database with new schema...")
    
    # Delete old database
    os.remove(db_path)
    print(f"    ✅ Removed old database")
    
    # Let SQLAlchemy create new one
    print(f"    ⚠️  Run the following command to create new database:")
    print(f"    cd /opt/ggnet/backend")
    print(f"    python -c 'import asyncio; from src.db.base import init_db; asyncio.run(init_db())'")
    print("")
    print(f"    OR restart the backend service:")
    print(f"    sudo systemctl restart ggnet-backend")
    
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print(f"✅ Backup saved: {backup_path}")
    print(f"⚠️  Old data was NOT migrated (need manual import)")
    print(f"    Restart backend to create new schema")


if __name__ == "__main__":
    # Default database path
    db_path = os.path.join(os.path.dirname(__file__), "..", "ggnet.db")
    
    # Check for custom path
    import sys
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    migrate_database(db_path)

