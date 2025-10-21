"""
Tests for Monitoring System

Test logging, metrics collection, and real-time monitoring.
"""

import pytest
import time
from unittest.mock import Mock, patch

from src.monitoring.logger import StructuredLogger, get_logger
from src.monitoring.metrics import MetricsCollector, init_metrics_collector
from src.monitoring.monitor import RealTimeMonitor, init_monitor, Alert


class TestStructuredLogger:
    """Test structured logger"""
    
    def test_logger_initialization(self):
        """Test logger initialization"""
        logger = StructuredLogger(
            name="test",
            log_dir="/tmp/test_logs",
            console_output=False,
            file_output=False
        )
        
        assert logger.name == "test"
        assert logger.log_dir.name == "test_logs"
    
    def test_log_levels(self):
        """Test different log levels"""
        logger = StructuredLogger(
            name="test",
            log_dir="/tmp/test_logs",
            console_output=False,
            file_output=False
        )
        
        # Test all log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_log_event(self):
        """Test structured event logging"""
        logger = StructuredLogger(
            name="test",
            log_dir="/tmp/test_logs",
            console_output=False,
            file_output=False
        )
        
        event_data = {
            "machine_id": "123",
            "action": "boot",
            "status": "success"
        }
        
        logger.log_event("machine_booted", event_data)
    
    def test_get_logger_singleton(self):
        """Test logger singleton pattern"""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        
        assert logger1 is logger2


class TestMetricsCollector:
    """Test metrics collector"""
    
    def test_collector_initialization(self):
        """Test metrics collector initialization"""
        collector = MetricsCollector(collection_interval=1)
        
        assert collector.collection_interval == 1
        assert collector.history_size == 1000
        assert not collector.running
    
    def test_collect_system_metrics(self):
        """Test system metrics collection"""
        collector = MetricsCollector()
        
        metrics = collector._collect_system_metrics()
        
        assert metrics is not None
        assert metrics.cpu_percent >= 0
        assert metrics.cpu_count > 0
        assert metrics.memory_total > 0
        assert metrics.memory_percent >= 0
        assert metrics.disk_total > 0
        assert metrics.disk_percent >= 0
    
    def test_collector_start_stop(self):
        """Test collector start/stop"""
        collector = MetricsCollector(collection_interval=1)
        
        assert not collector.running
        
        collector.start()
        assert collector.running
        
        time.sleep(2)  # Wait for collection
        
        collector.stop()
        assert not collector.running
    
    def test_get_system_metrics(self):
        """Test getting system metrics"""
        collector = MetricsCollector()
        
        # Collect metrics
        metrics_obj = collector._collect_system_metrics()
        collector.current_system_metrics = metrics_obj
        
        # Get metrics
        metrics = collector.get_system_metrics()
        
        assert metrics is not None
        assert "timestamp" in metrics
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
    
    def test_get_metrics_summary(self):
        """Test getting metrics summary"""
        collector = MetricsCollector()
        
        summary = collector.get_metrics_summary()
        
        assert "system" in summary
        assert "application" in summary
        assert "history_size" in summary


class TestRealTimeMonitor:
    """Test real-time monitor"""
    
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        monitor = RealTimeMonitor()
        
        assert not monitor.running
        assert len(monitor.alert_rules) > 0  # Should have default rules
    
    def test_add_alert(self):
        """Test adding alert"""
        monitor = RealTimeMonitor()
        
        monitor.add_alert("warning", "Test alert", "test_source")
        
        assert len(monitor.alerts) == 1
        assert monitor.alerts[0].level == "warning"
        assert monitor.alerts[0].message == "Test alert"
    
    def test_get_alerts(self):
        """Test getting alerts"""
        monitor = RealTimeMonitor()
        
        # Add some alerts
        monitor.add_alert("info", "Info alert", "test")
        monitor.add_alert("warning", "Warning alert", "test")
        monitor.add_alert("error", "Error alert", "test")
        
        # Get all alerts
        alerts = monitor.get_alerts()
        assert len(alerts) == 3
        
        # Get only warnings
        warnings = monitor.get_alerts(level="warning")
        assert len(warnings) == 1
        assert warnings[0]["level"] == "warning"
    
    def test_alert_rules(self):
        """Test alert rules"""
        monitor = RealTimeMonitor()
        
        # Get initial rules
        initial_count = len(monitor.alert_rules)
        
        # Add new rule
        monitor.add_alert_rule(
            name="test_rule",
            condition=lambda m: True,
            level="info",
            message="Test rule"
        )
        
        assert len(monitor.alert_rules) == initial_count + 1
        
        # Get alert rules
        rules = monitor.get_alert_rules()
        assert len(rules) == initial_count + 1
        
        # Remove rule
        monitor.remove_alert_rule("test_rule")
        assert len(monitor.alert_rules) == initial_count
    
    def test_enable_disable_rule(self):
        """Test enabling/disabling alert rules"""
        monitor = RealTimeMonitor()
        
        # Add rule
        monitor.add_alert_rule(
            name="test_rule",
            condition=lambda m: True,
            level="info",
            message="Test rule"
        )
        
        # Disable rule
        monitor.disable_alert_rule("test_rule")
        
        rule = next((r for r in monitor.alert_rules if r.name == "test_rule"), None)
        assert rule is not None
        assert not rule.enabled
        
        # Enable rule
        monitor.enable_alert_rule("test_rule")
        
        rule = next((r for r in monitor.alert_rules if r.name == "test_rule"), None)
        assert rule is not None
        assert rule.enabled
    
    def test_monitor_start_stop(self):
        """Test monitor start/stop"""
        monitor = RealTimeMonitor()
        
        assert not monitor.running
        
        monitor.start()
        assert monitor.running
        
        time.sleep(1)
        
        monitor.stop()
        assert not monitor.running
    
    def test_get_monitoring_status(self):
        """Test getting monitoring status"""
        monitor = RealTimeMonitor()
        
        status = monitor.get_monitoring_status()
        
        assert "running" in status
        assert "alert_count" in status
        assert "rule_count" in status
        assert "enabled_rules" in status


class TestMonitoringIntegration:
    """Test monitoring system integration"""
    
    def test_init_metrics_collector(self):
        """Test metrics collector initialization"""
        collector = init_metrics_collector(collection_interval=1)
        
        assert collector is not None
        assert collector.collection_interval == 1
    
    def test_init_monitor(self):
        """Test monitor initialization"""
        monitor = init_monitor()
        
        assert monitor is not None
        assert len(monitor.alert_rules) > 0


class TestAlert:
    """Test Alert class"""
    
    def test_alert_creation(self):
        """Test alert creation"""
        alert = Alert(
            level="warning",
            message="Test alert",
            source="test",
            data={"key": "value"}
        )
        
        assert alert.level == "warning"
        assert alert.message == "Test alert"
        assert alert.source == "test"
        assert alert.data == {"key": "value"}
        assert alert.timestamp is not None
    
    def test_alert_to_dict(self):
        """Test alert to dictionary conversion"""
        alert = Alert(
            level="error",
            message="Test error",
            source="test"
        )
        
        alert_dict = alert.to_dict()
        
        assert "level" in alert_dict
        assert "message" in alert_dict
        assert "source" in alert_dict
        assert "timestamp" in alert_dict
        assert alert_dict["level"] == "error"

