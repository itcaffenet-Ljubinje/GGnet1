"""
Metrics Collection for ggNet

Collects and stores system and application metrics.
"""

import time
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import deque
import threading


@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: str
    cpu_percent: float
    cpu_count: int
    memory_total: int
    memory_used: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    network_sent: int
    network_recv: int
    load_avg: List[float]


@dataclass
class ApplicationMetrics:
    """Application metrics data structure"""
    timestamp: str
    total_machines: int
    online_machines: int
    offline_machines: int
    active_sessions: int
    total_images: int
    total_writebacks: int
    total_snapshots: int
    cache_hit_rate: float
    cache_size: int
    cache_max_size: int


class MetricsCollector:
    """
    Metrics Collector
    
    Collects system and application metrics at regular intervals.
    """
    
    def __init__(
        self,
        collection_interval: int = 60,
        history_size: int = 1000
    ):
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        # Metrics history
        self.system_metrics_history = deque(maxlen=history_size)
        self.application_metrics_history = deque(maxlen=history_size)
        
        # Current metrics
        self.current_system_metrics: Optional[SystemMetrics] = None
        self.current_application_metrics: Optional[ApplicationMetrics] = None
        
        # Collection thread
        self.collection_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Network stats baseline
        self.network_baseline = {
            'sent': psutil.net_io_counters().bytes_sent,
            'recv': psutil.net_io_counters().bytes_recv
        }
    
    def start(self):
        """Start metrics collection"""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self.collection_thread.start()
    
    def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.current_system_metrics = system_metrics
                self.system_metrics_history.append(system_metrics)
                
                # Collect application metrics
                application_metrics = self._collect_application_metrics()
                self.current_application_metrics = application_metrics
                self.application_metrics_history.append(application_metrics)
                
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_used = memory.used
        memory_percent = memory.percent
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_total = disk.total
        disk_used = disk.used
        disk_percent = disk.percent
        
        # Network metrics
        network = psutil.net_io_counters()
        network_sent = network.bytes_sent - self.network_baseline['sent']
        network_recv = network.bytes_recv - self.network_baseline['recv']
        
        # Load average
        load_avg = list(psutil.getloadavg())
        
        return SystemMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            cpu_count=cpu_count,
            memory_total=memory_total,
            memory_used=memory_used,
            memory_percent=memory_percent,
            disk_total=disk_total,
            disk_used=disk_used,
            disk_percent=disk_percent,
            network_sent=network_sent,
            network_recv=network_recv,
            load_avg=load_avg
        )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application metrics"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # TODO: Get actual metrics from database/services
        # For now, return placeholder data
        return ApplicationMetrics(
            timestamp=timestamp,
            total_machines=0,
            online_machines=0,
            offline_machines=0,
            active_sessions=0,
            total_images=0,
            total_writebacks=0,
            total_snapshots=0,
            cache_hit_rate=0.0,
            cache_size=0,
            cache_max_size=512 * 1024 * 1024  # 512MB
        )
    
    def get_system_metrics(self) -> Optional[Dict]:
        """Get current system metrics"""
        if self.current_system_metrics:
            return asdict(self.current_system_metrics)
        return None
    
    def get_application_metrics(self) -> Optional[Dict]:
        """Get current application metrics"""
        if self.current_application_metrics:
            return asdict(self.current_application_metrics)
        return None
    
    def get_system_metrics_history(
        self,
        limit: int = 100
    ) -> List[Dict]:
        """Get system metrics history"""
        return [
            asdict(metrics)
            for metrics in list(self.system_metrics_history)[-limit:]
        ]
    
    def get_application_metrics_history(
        self,
        limit: int = 100
    ) -> List[Dict]:
        """Get application metrics history"""
        return [
            asdict(metrics)
            for metrics in list(self.application_metrics_metrics)[-limit:]
        ]
    
    def get_metrics_summary(self) -> Dict:
        """Get metrics summary"""
        return {
            "system": self.get_system_metrics(),
            "application": self.get_application_metrics(),
            "history_size": {
                "system": len(self.system_metrics_history),
                "application": len(self.application_metrics_history)
            }
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> Optional[MetricsCollector]:
    """Get global metrics collector instance"""
    return _metrics_collector


def init_metrics_collector(
    collection_interval: int = 60,
    history_size: int = 1000
) -> MetricsCollector:
    """Initialize global metrics collector"""
    global _metrics_collector
    _metrics_collector = MetricsCollector(
        collection_interval=collection_interval,
        history_size=history_size
    )
    return _metrics_collector


def start_metrics_collection():
    """Start metrics collection"""
    collector = get_metrics_collector()
    if collector:
        collector.start()


def stop_metrics_collection():
    """Stop metrics collection"""
    collector = get_metrics_collector()
    if collector:
        collector.stop()

