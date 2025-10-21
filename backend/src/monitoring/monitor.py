"""
Real-Time Monitoring for ggNet

Provides real-time monitoring of system and application state.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone
from collections import deque
import threading


class Alert:
    """Alert data structure"""
    
    def __init__(
        self,
        level: str,
        message: str,
        source: str,
        data: Optional[Dict] = None
    ):
        self.level = level  # info, warning, error, critical
        self.message = message
        self.source = source
        self.data = data or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            "level": self.level,
            "message": self.message,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp
        }


class AlertRule:
    """Alert rule definition"""
    
    def __init__(
        self,
        name: str,
        condition: Callable,
        level: str,
        message: str,
        enabled: bool = True
    ):
        self.name = name
        self.condition = condition
        self.level = level
        self.message = message
        self.enabled = enabled
        self.last_triggered: Optional[datetime] = None
        self.trigger_count = 0
    
    def check(self, metrics: Dict) -> Optional[Alert]:
        """Check if rule should trigger"""
        if not self.enabled:
            return None
        
        try:
            if self.condition(metrics):
                self.last_triggered = datetime.now(timezone.utc)
                self.trigger_count += 1
                return Alert(
                    level=self.level,
                    message=self.message,
                    source=f"rule:{self.name}",
                    data={"trigger_count": self.trigger_count}
                )
        except Exception as e:
            print(f"Error checking rule {self.name}: {e}")
        
        return None


class RealTimeMonitor:
    """
    Real-Time Monitor
    
    Monitors system and application state in real-time.
    """
    
    def __init__(self):
        self.alerts: deque = deque(maxlen=1000)
        self.alert_rules: List[AlertRule] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False
        self.monitoring_interval = 30  # seconds
        
        # Setup default alert rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        
        # High CPU usage
        self.add_alert_rule(
            name="high_cpu",
            condition=lambda m: m.get("system", {}).get("cpu_percent", 0) > 80,
            level="warning",
            message="High CPU usage detected"
        )
        
        # High memory usage
        self.add_alert_rule(
            name="high_memory",
            condition=lambda m: m.get("system", {}).get("memory_percent", 0) > 85,
            level="warning",
            message="High memory usage detected"
        )
        
        # High disk usage
        self.add_alert_rule(
            name="high_disk",
            condition=lambda m: m.get("system", {}).get("disk_percent", 0) > 90,
            level="critical",
            message="High disk usage detected"
        )
        
        # Low cache hit rate
        self.add_alert_rule(
            name="low_cache_hit",
            condition=lambda m: m.get("application", {}).get("cache_hit_rate", 100) < 50,
            level="info",
            message="Low cache hit rate detected"
        )
    
    def add_alert_rule(
        self,
        name: str,
        condition: Callable,
        level: str,
        message: str,
        enabled: bool = True
    ):
        """Add alert rule"""
        rule = AlertRule(name, condition, level, message, enabled)
        self.alert_rules.append(rule)
    
    def remove_alert_rule(self, name: str):
        """Remove alert rule"""
        self.alert_rules = [r for r in self.alert_rules if r.name != name]
    
    def enable_alert_rule(self, name: str):
        """Enable alert rule"""
        for rule in self.alert_rules:
            if rule.name == name:
                rule.enabled = True
                break
    
    def disable_alert_rule(self, name: str):
        """Disable alert rule"""
        for rule in self.alert_rules:
            if rule.name == name:
                rule.enabled = False
                break
    
    def start(self):
        """Start monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        from monitoring.metrics import get_metrics_collector
        
        while self.running:
            try:
                # Get current metrics
                collector = get_metrics_collector()
                if collector:
                    metrics = collector.get_metrics_summary()
                    
                    # Check alert rules
                    for rule in self.alert_rules:
                        alert = rule.check(metrics)
                        if alert:
                            self.alerts.append(alert)
                            print(f"Alert: {alert.level} - {alert.message}")
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
            
            time.sleep(self.monitoring_interval)
    
    def add_alert(
        self,
        level: str,
        message: str,
        source: str,
        data: Optional[Dict] = None
    ):
        """Manually add alert"""
        alert = Alert(level, message, source, data)
        self.alerts.append(alert)
    
    def get_alerts(
        self,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get recent alerts
        
        Args:
            level: Filter by alert level
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dictionaries
        """
        alerts = list(self.alerts)
        
        # Filter by level
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # Get most recent
        alerts = alerts[-limit:]
        
        return [alert.to_dict() for alert in alerts]
    
    def get_alert_rules(self) -> List[Dict]:
        """Get all alert rules"""
        return [
            {
                "name": rule.name,
                "level": rule.level,
                "message": rule.message,
                "enabled": rule.enabled,
                "trigger_count": rule.trigger_count,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            }
            for rule in self.alert_rules
        ]
    
    def get_monitoring_status(self) -> Dict:
        """Get monitoring status"""
        return {
            "running": self.running,
            "alert_count": len(self.alerts),
            "rule_count": len(self.alert_rules),
            "enabled_rules": sum(1 for r in self.alert_rules if r.enabled),
            "monitoring_interval": self.monitoring_interval
        }


# Global monitor instance
_monitor: Optional[RealTimeMonitor] = None


def get_monitor() -> Optional[RealTimeMonitor]:
    """Get global monitor instance"""
    return _monitor


def init_monitor() -> RealTimeMonitor:
    """Initialize global monitor"""
    global _monitor
    _monitor = RealTimeMonitor()
    return _monitor


def start_monitoring():
    """Start monitoring"""
    monitor = get_monitor()
    if monitor:
        monitor.start()


def stop_monitoring():
    """Stop monitoring"""
    monitor = get_monitor()
    if monitor:
        monitor.stop()

