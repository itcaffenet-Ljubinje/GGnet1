#!/usr/bin/env python3
"""
ggNet Backend - Main Application Entry Point

Minimal working FastAPI server for diskless boot management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import uvicorn
import psutil

from config.settings import settings
from db.base import init_db, close_db
from api.v1 import machines

# Track startup time for uptime calculation
start_time = datetime.now(timezone.utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup on startup/shutdown"""
    # Startup
    print("🚀 Starting ggNet Backend...")
    await init_db()
    print(f"✅ Database ready")
    print(f"✅ Server running at http://{settings.HOST}:{settings.PORT}")
    print(f"✅ API docs at http://{settings.HOST}:{settings.PORT}/docs")
    yield
    # Shutdown
    print("🛑 Shutting down ggNet Backend...")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="Diskless Boot Management System",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - Allow frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint

    Returns 200 OK if server is running.
    """
    return {"status": "ok"}


# Status endpoint with detailed info
@app.get("/api/status")
async def get_status():
    """
    System status and health check

    Returns app name, version, uptime, and basic system stats.
    """
    uptime_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "uptime_seconds": uptime_seconds,
        "db_status": "connected",
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """API root - redirect to docs"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": "/api/v1"
    }


# Register API routers
app.include_router(machines.router, prefix="/api/v1", tags=["machines"])

# Additional routers will be added here as endpoints are implemented
# from api.v1 import images, writebacks, snapshots, network, system
# app.include_router(images.router, prefix="/api/v1", tags=["images"])
# app.include_router(writebacks.router, prefix="/api/v1", tags=["writebacks"])
# app.include_router(snapshots.router, prefix="/api/v1", tags=["snapshots"])


# System logs endpoint (minimal implementation)
@app.get("/api/v1/system/logs")
async def get_system_logs(limit: int = 100):
    """
    Get system logs (placeholder)

    TODO: Implement actual log reading from journald or log files
    """
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": "ggNet backend started",
                "source": "main"
            }
        ],
        "total": 1,
        "limit": limit
    }


# System metrics endpoint
@app.get("/api/v1/system/metrics")
async def get_system_metrics():
    """
    Get system metrics including cache and array stats

    TODO: Integrate with actual cache manager
    TODO: Read RAID/ZFS array statistics
    """
    return {
        "cache": {
            "hit_rate_percent": 0,
            "size_mb": 0,
            "max_size_mb": 512,
            "entries": 0
        },
        "array": {
            "type": "RAID10",
            "health": "unknown",
            "total_gb": 0,
            "used_gb": 0,
            "available_gb": 0
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
