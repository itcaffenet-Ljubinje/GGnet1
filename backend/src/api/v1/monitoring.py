"""
Monitoring API Endpoints

Provides monitoring, metrics, and alerting endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from monitoring.metrics import get_metrics_collector
from monitoring.monitor import get_monitor
from monitoring.logger import get_logger

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# Schemas
class AlertRuleCreate(BaseModel):
    name: str
    level: str
    message: str
    enabled: bool = True


# Endpoints
@router.get("/metrics/system")
async def get_system_metrics():
    """Get current system metrics"""
    collector = get_metrics_collector()
    
    if not collector:
        raise HTTPException(
            status_code=503,
            detail="Metrics collector not initialized"
        )
    
    metrics = collector.get_system_metrics()
    
    if not metrics:
        raise HTTPException(
            status_code=503,
            detail="No system metrics available"
        )
    
    return metrics


@router.get("/metrics/application")
async def get_application_metrics():
    """Get current application metrics"""
    collector = get_metrics_collector()
    
    if not collector:
        raise HTTPException(
            status_code=503,
            detail="Metrics collector not initialized"
        )
    
    metrics = collector.get_application_metrics()
    
    if not metrics:
        raise HTTPException(
            status_code=503,
            detail="No application metrics available"
        )
    
    return metrics


@router.get("/metrics/history/system")
async def get_system_metrics_history(
    limit: int = Query(100, ge=1, le=1000)
):
    """Get system metrics history"""
    collector = get_metrics_collector()
    
    if not collector:
        raise HTTPException(
            status_code=503,
            detail="Metrics collector not initialized"
        )
    
    history = collector.get_system_metrics_history(limit=limit)
    
    return {
        "metrics": history,
        "count": len(history)
    }


@router.get("/metrics/history/application")
async def get_application_metrics_history(
    limit: int = Query(100, ge=1, le=1000)
):
    """Get application metrics history"""
    collector = get_metrics_collector()
    
    if not collector:
        raise HTTPException(
            status_code=503,
            detail="Metrics collector not initialized"
        )
    
    history = collector.get_application_metrics_history(limit=limit)
    
    return {
        "metrics": history,
        "count": len(history)
    }


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary"""
    collector = get_metrics_collector()
    
    if not collector:
        raise HTTPException(
            status_code=503,
            detail="Metrics collector not initialized"
        )
    
    summary = collector.get_metrics_summary()
    
    return summary


@router.get("/alerts")
async def get_alerts(
    level: Optional[str] = Query(None, regex="^(info|warning|error|critical)$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get recent alerts"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    alerts = monitor.get_alerts(level=level, limit=limit)
    
    return {
        "alerts": alerts,
        "count": len(alerts)
    }


@router.post("/alerts")
async def create_alert(
    level: str,
    message: str,
    source: str,
    data: Optional[dict] = None
):
    """Manually create alert"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    if level not in ["info", "warning", "error", "critical"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid alert level"
        )
    
    monitor.add_alert(level, message, source, data)
    
    return {
        "success": True,
        "message": "Alert created"
    }


@router.get("/alerts/rules")
async def get_alert_rules():
    """Get all alert rules"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    rules = monitor.get_alert_rules()
    
    return {
        "rules": rules,
        "count": len(rules)
    }


@router.post("/alerts/rules")
async def create_alert_rule(rule: AlertRuleCreate):
    """Create new alert rule"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    if rule.level not in ["info", "warning", "error", "critical"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid alert level"
        )
    
    # TODO: Implement rule creation with condition
    # For now, just return success
    
    return {
        "success": True,
        "message": "Alert rule created (placeholder)"
    }


@router.delete("/alerts/rules/{rule_name}")
async def delete_alert_rule(rule_name: str):
    """Delete alert rule"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    monitor.remove_alert_rule(rule_name)
    
    return {
        "success": True,
        "message": f"Alert rule '{rule_name}' deleted"
    }


@router.post("/alerts/rules/{rule_name}/enable")
async def enable_alert_rule(rule_name: str):
    """Enable alert rule"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    monitor.enable_alert_rule(rule_name)
    
    return {
        "success": True,
        "message": f"Alert rule '{rule_name}' enabled"
    }


@router.post("/alerts/rules/{rule_name}/disable")
async def disable_alert_rule(rule_name: str):
    """Disable alert rule"""
    monitor = get_monitor()
    
    if not monitor:
        raise HTTPException(
            status_code=503,
            detail="Monitor not initialized"
        )
    
    monitor.disable_alert_rule(rule_name)
    
    return {
        "success": True,
        "message": f"Alert rule '{rule_name}' disabled"
    }


@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query(None, regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    limit: int = Query(100, ge=1, le=1000),
    tail: bool = Query(True)
):
    """Get recent logs"""
    logger = get_logger()
    
    logs = logger.get_logs(level=level, limit=limit, tail=tail)
    
    return {
        "logs": logs,
        "count": len(logs)
    }


@router.get("/status")
async def get_monitoring_status():
    """Get monitoring status"""
    collector = get_metrics_collector()
    monitor = get_monitor()
    
    return {
        "metrics_collector": {
            "running": collector is not None
        },
        "monitor": {
            "running": monitor.running if monitor else False,
            "alert_count": len(monitor.alerts) if monitor else 0,
            "rule_count": len(monitor.alert_rules) if monitor else 0
        } if monitor else None
    }

