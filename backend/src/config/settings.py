"""
ggNet Configuration Settings

Load configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Settings:
    """Application settings"""
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "ggNet")
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS - Allow frontend development server
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend
    ]
    
    # Database - SQLite for development
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./ggnet.db"
    )
    
    # Storage paths
    STATIC_ROOT: Path = Path(os.getenv("STATIC_ROOT", "./storage"))
    TFTP_ROOT: Path = Path(os.getenv("TFTP_ROOT", "./pxe/tftp"))
    NFS_ROOT: Path = Path(os.getenv("NFS_ROOT", "./storage/nfs"))
    IMAGE_ROOT: Path = Path(os.getenv("IMAGE_ROOT", "./storage/images"))
    WRITEBACK_ROOT: Path = Path(os.getenv("WRITEBACK_ROOT", "./storage/writebacks"))
    SNAPSHOT_ROOT: Path = Path(os.getenv("SNAPSHOT_ROOT", "./storage/snapshots"))
    
    # Cache
    CACHE_LIMIT_MB: int = int(os.getenv("CACHE_LIMIT_MB", "51200"))  # 50 GB default
    
    # Ensure directories exist
    def __init__(self):
        for path in [
            self.STATIC_ROOT,
            self.TFTP_ROOT,
            self.NFS_ROOT,
            self.IMAGE_ROOT,
            self.WRITEBACK_ROOT,
            self.SNAPSHOT_ROOT,
        ]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()

