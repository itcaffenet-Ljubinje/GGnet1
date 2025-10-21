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
from core.services import initialize_core_services, start_core_services, stop_core_services
from monitoring.metrics import init_metrics_collector, start_metrics_collection, stop_metrics_collection
from monitoring.monitor import init_monitor, start_monitoring, stop_monitoring
from monitoring.logger import get_logger
from core.cleanup import start_cleanup, stop_cleanup

# Track startup time for uptime calculation
start_time = datetime.now(timezone.utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup on startup/shutdown"""
    # Startup
    print("[STARTUP] Starting ggNet Backend...")
    
    # Initialize logger
    logger = get_logger("ggnet", log_dir="logs", level=10)  # DEBUG level
    logger.info("ggNet Backend starting up")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    print(f"[OK] Database ready")
    
    # Initialize monitoring
    init_metrics_collector(collection_interval=60)
    init_monitor()
    logger.info("Monitoring initialized")
    print(f"[OK] Monitoring initialized")
    
    # Start metrics collection
    start_metrics_collection()
    logger.info("Metrics collection started")
    
    # Start monitoring
    start_monitoring()
    logger.info("Real-time monitoring started")
    
    # Start automated cleanup
    await start_cleanup()
    logger.info("Automated cleanup started")
    print(f"[OK] Automated cleanup started")
    
    # Initialize core services (DHCP, TFTP, NFS, PXE)
    # Note: Core services only work on Linux systems
    import platform
    if platform.system() == "Linux":
        try:
            await initialize_core_services()
            logger.info("Core services initialized")
            print(f"[OK] Core services initialized")
            
            # Start core services
            await start_core_services()
            logger.info("Core services started")
            print(f"[OK] Core services started")
        except Exception as e:
            logger.error(f"Core services failed to start: {e}")
            print(f"[WARNING] Core services failed to start: {e}")
            print(f"[INFO] Server will continue without core services")
    else:
        logger.info("Core services skipped (not Linux)")
        print(f"[INFO] Core services skipped (running on {platform.system()})")
    
    logger.info(f"Server running at http://{settings.HOST}:{settings.PORT}")
    print(f"[OK] Server running at http://{settings.HOST}:{settings.PORT}")
    print(f"[OK] API docs at http://{settings.HOST}:{settings.PORT}/docs")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ggNet Backend")
    print("[SHUTDOWN] Shutting down ggNet Backend...")
    
    # Stop monitoring
    stop_monitoring()
    logger.info("Monitoring stopped")
    
    # Stop metrics collection
    stop_metrics_collection()
    logger.info("Metrics collection stopped")
    
    # Stop automated cleanup
    await stop_cleanup()
    logger.info("Automated cleanup stopped")
    print(f"[OK] Automated cleanup stopped")
    
    # Stop core services
    try:
        await stop_core_services()
        logger.info("Core services stopped")
        print(f"[OK] Core services stopped")
    except Exception as e:
        logger.error(f"Error stopping core services: {e}")
        print(f"[WARNING] Error stopping core services: {e}")
    
    # Close database
    await close_db()
    logger.info("Database closed")
    print(f"[OK] Shutdown complete")


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
from api.v1 import images, writebacks, snapshots, network, system, monitoring, storage, system_settings

app.include_router(machines.router, prefix="/api/v1", tags=["machines"])
app.include_router(images.router, prefix="/api/v1", tags=["images"])
app.include_router(writebacks.router, prefix="/api/v1", tags=["writebacks"])
app.include_router(snapshots.router, prefix="/api/v1", tags=["snapshots"])
app.include_router(storage.router, prefix="/api/v1", tags=["storage"])
app.include_router(system_settings.router, prefix="/api/v1", tags=["settings"])
app.include_router(network.router, prefix="/api/v1", tags=["network"])
app.include_router(system.router, prefix="/api/v1", tags=["system"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])


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
