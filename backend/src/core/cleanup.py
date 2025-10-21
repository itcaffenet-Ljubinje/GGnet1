"""
Automated Cleanup Logic

Handles automatic deletion of old snapshots and writebacks based on retention settings.
"""

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
import asyncio

from db.base import async_session_maker
from db.models import Snapshot, Writeback
from monitoring.logger import get_logger

logger = get_logger("cleanup")


class CleanupManager:
    """Manages automated cleanup of snapshots and writebacks"""
    
    def __init__(self):
        self.is_running = False
        self.cleanup_interval = 3600  # Run every hour (3600 seconds)
        self.background_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the cleanup background task"""
        if self.is_running:
            logger.warning("Cleanup manager is already running")
            return
        
        self.is_running = True
        self.background_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Automated cleanup started")
    
    async def stop(self):
        """Stop the cleanup background task"""
        self.is_running = False
        if self.background_task:
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
        logger.info("Automated cleanup stopped")
    
    async def _cleanup_loop(self):
        """Main cleanup loop"""
        while self.is_running:
            try:
                await self.run_cleanup()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def run_cleanup(self):
        """
        Run cleanup process
        
        This method:
        1. Deletes unutilized snapshots older than configured days
        2. Keeps only N unprotected snapshots
        3. Deletes inactive writebacks after configured hours
        """
        logger.info("Running automated cleanup...")
        
        try:
            # Get retention settings
            settings = await self._get_retention_settings()
            
            if not settings:
                logger.warning("No retention settings found, skipping cleanup")
                return
            
            # Clean up snapshots
            snapshot_deleted = await self._cleanup_snapshots(
                unutilized_days=settings.get("unutilized_snapshots_days", 30),
                unprotected_count=settings.get("unprotected_snapshots_count", 5)
            )
            
            # Clean up writebacks
            writeback_deleted = await self._cleanup_writebacks(
                inactive_hours=settings.get("inactive_writebacks_hours", 168)
            )
            
            logger.info(
                f"Cleanup completed: {snapshot_deleted} snapshots deleted, "
                f"{writeback_deleted} writebacks deleted"
            )
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _cleanup_snapshots(
        self,
        unutilized_days: int = 30,
        unprotected_count: int = 5
    ) -> int:
        """
        Clean up old snapshots
        
        Args:
            unutilized_days: Days to retain unutilized snapshots
            unprotected_count: Number of unprotected snapshots to keep
        
        Returns:
            Number of snapshots deleted
        """
        deleted_count = 0
        
        async with async_session_maker() as session:
            try:
                # Get cutoff date for unutilized snapshots
                cutoff_date = datetime.utcnow() - timedelta(days=unutilized_days)
                
                # Find all unutilized snapshots older than cutoff date
                # Unutilized = not protected and not in use (status != 'active')
                result = await session.execute(
                    select(Snapshot)
                    .where(Snapshot.protected == False)
                    .where(Snapshot.status != "active")
                    .where(Snapshot.date_created < cutoff_date)
                    .order_by(Snapshot.date_created.desc())
                )
                old_snapshots = result.scalars().all()
                
                # Keep only the most recent N unprotected snapshots
                if len(old_snapshots) > unprotected_count:
                    # Delete older snapshots, keep the newest N
                    snapshots_to_delete = old_snapshots[unprotected_count:]
                    
                    for snapshot in snapshots_to_delete:
                        # TODO: Delete actual snapshot files from storage
                        # For now, just delete database record
                        await session.delete(snapshot)
                        deleted_count += 1
                        logger.info(
                            f"Deleted old snapshot: {snapshot.name} "
                            f"(created: {snapshot.date_created})"
                        )
                    
                    await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error cleaning up snapshots: {e}")
        
        return deleted_count
    
    async def _cleanup_writebacks(
        self,
        inactive_hours: int = 168
    ) -> int:
        """
        Clean up inactive writebacks
        
        Args:
            inactive_hours: Hours to retain inactive writebacks
        
        Returns:
            Number of writebacks deleted
        """
        deleted_count = 0
        
        async with async_session_maker() as session:
            try:
                # Get cutoff time for inactive writebacks
                cutoff_time = datetime.utcnow() - timedelta(hours=inactive_hours)
                
                # Find all inactive writebacks older than cutoff time
                # Inactive = status 'inactive' and not recently updated
                result = await session.execute(
                    select(Writeback)
                    .where(Writeback.status == "inactive")
                    .where(Writeback.created_at < cutoff_time)
                )
                old_writebacks = result.scalars().all()
                
                for writeback in old_writebacks:
                    # TODO: Delete actual writeback files from storage
                    # For now, just delete database record
                    await session.delete(writeback)
                    deleted_count += 1
                    logger.info(
                        f"Deleted inactive writeback: {writeback.writeback_id} "
                        f"(created: {writeback.created_at})"
                    )
                
                if deleted_count > 0:
                    await session.commit()
            
            except Exception as e:
                await session.rollback()
                logger.error(f"Error cleaning up writebacks: {e}")
        
        return deleted_count
    
    async def _get_retention_settings(self) -> dict:
        """
        Get retention settings from database or config
        
        Returns:
            Dictionary with retention settings
        """
        # TODO: Load from actual settings storage (database or config file)
        # For now, return default values
        return {
            "unutilized_snapshots_days": 30,
            "unprotected_snapshots_count": 5,
            "inactive_writebacks_hours": 168
        }


# Global cleanup manager instance
_cleanup_manager: Optional[CleanupManager] = None


def get_cleanup_manager() -> CleanupManager:
    """Get the global cleanup manager instance"""
    global _cleanup_manager
    if _cleanup_manager is None:
        _cleanup_manager = CleanupManager()
    return _cleanup_manager


async def start_cleanup():
    """Start the cleanup manager"""
    manager = get_cleanup_manager()
    await manager.start()


async def stop_cleanup():
    """Stop the cleanup manager"""
    manager = get_cleanup_manager()
    await manager.stop()


async def trigger_cleanup():
    """Manually trigger cleanup (useful when settings change)"""
    manager = get_cleanup_manager()
    await manager.run_cleanup()

