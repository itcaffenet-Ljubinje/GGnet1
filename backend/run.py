#!/usr/bin/env python3
"""
Quick Start Script for ggNet Backend

Automatically sets up and runs the server.
"""

import subprocess
import sys
from pathlib import Path
import os

def main():
    # Get paths
    backend_dir = Path(__file__).parent
    src_dir = backend_dir / "src"
    db_path = src_dir / "ggnet.db"
    seed_script = backend_dir / "scripts" / "seed_db.py"
    
    # Check if database exists
    if not db_path.exists():
        print("📦 Database not found. Creating and seeding...")
        print()
        
        # Run seed script
        os.chdir(src_dir)
        result = subprocess.run([sys.executable, str(seed_script)])
        
        if result.returncode != 0:
            print("❌ Failed to seed database")
            return 1
        
        print()
    else:
        print("✅ Database exists")
        print()
    
    # Start server
    print("🚀 Starting server...")
    print("=" * 60)
    os.chdir(src_dir)
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())

