"""
Monitoring Module for ggNet

Provides logging, metrics collection, and real-time monitoring.
"""

from .logger import (
    StructuredLogger,
    get_logger,
    log_debug,
    log_info,
    log_warning,
    log_error,
    log_critical,
    log_exception,
    log_event
)

from .metrics import (
    MetricsCollector,
    SystemMetrics,
    ApplicationMetrics,
    get_metrics_collector,
    init_metrics_collector,
    start_metrics_collection,
    stop_metrics_collection
)

from .monitor import (
    RealTimeMonitor,
    Alert,
    AlertRule,
    get_monitor,
    init_monitor,
    start_monitoring,
    stop_monitoring
)

__all__ = [
    # Logger
    "StructuredLogger",
    "get_logger",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "log_critical",
    "log_exception",
    "log_event",
    # Metrics
    "MetricsCollector",
    "SystemMetrics",
    "ApplicationMetrics",
    "get_metrics_collector",
    "init_metrics_collector",
    "start_metrics_collection",
    "stop_metrics_collection",
    # Monitor
    "RealTimeMonitor",
    "Alert",
    "AlertRule",
    "get_monitor",
    "init_monitor",
    "start_monitoring",
    "stop_monitoring"
]

