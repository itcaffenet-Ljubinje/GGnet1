"""
Logging System for ggNet

Provides structured logging with multiple handlers and log levels.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


class StructuredLogger:
    """
    Structured Logger for ggNet
    
    Provides structured logging with file rotation and console output.
    """
    
    def __init__(
        self,
        name: str,
        log_dir: str = "/var/log/ggnet",
        level: int = logging.INFO,
        console_output: bool = True,
        file_output: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.name = name
        self.log_dir = Path(log_dir)
        self.level = level
        self.console_output = console_output
        self.file_output = file_output
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()
        
        # Create formatters
        self.console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.file_formatter = JSONFormatter()
        
        # Add console handler
        if self.console_output:
            self._add_console_handler()
        
        # Add file handler
        if self.file_output:
            self._add_file_handler()
    
    def _add_console_handler(self):
        """Add console handler"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add rotating file handler"""
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file path
        log_file = self.log_dir / f"{self.name}.log"
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, extra=kwargs)
    
    def log_event(
        self,
        event_type: str,
        event_data: dict,
        level: int = logging.INFO
    ):
        """
        Log structured event
        
        Args:
            event_type: Type of event (e.g., "machine_created", "boot_started")
            event_data: Event data dictionary
            level: Log level
        """
        extra = {
            "event_type": event_type,
            "event_data": event_data
        }
        extra.update(event_data)
        
        self.logger.log(level, f"Event: {event_type}", extra=extra)
    
    def get_logs(
        self,
        level: Optional[str] = None,
        limit: int = 100,
        tail: bool = True
    ) -> list[dict]:
        """
        Get recent logs
        
        Args:
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            limit: Maximum number of logs to return
            tail: If True, return most recent logs (tail), else oldest
        
        Returns:
            List of log entries
        """
        logs = []
        
        if not self.file_output:
            return logs
        
        log_file = self.log_dir / f"{self.name}.log"
        
        if not log_file.exists():
            return logs
        
        # Read log file
        with open(log_file, "r") as f:
            lines = f.readlines()
        
        # Filter by level if specified
        if level:
            level_num = getattr(logging, level.upper(), logging.INFO)
            filtered_lines = []
            for line in lines:
                try:
                    log_entry = json.loads(line)
                    if log_entry.get("level") == level:
                        filtered_lines.append(line)
                except json.JSONDecodeError:
                    continue
            lines = filtered_lines
        
        # Get tail or head
        if tail:
            lines = lines[-limit:]
        else:
            lines = lines[:limit]
        
        # Parse JSON logs
        for line in lines:
            try:
                log_entry = json.loads(line)
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue
        
        return logs


# Global logger instances
_loggers = {}


def get_logger(
    name: str = "ggnet",
    log_dir: str = "/var/log/ggnet",
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True
) -> StructuredLogger:
    """
    Get or create logger instance
    
    Args:
        name: Logger name
        log_dir: Log directory
        level: Log level
        console_output: Enable console output
        file_output: Enable file output
    
    Returns:
        StructuredLogger instance
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(
            name=name,
            log_dir=log_dir,
            level=level,
            console_output=console_output,
            file_output=file_output
        )
    
    return _loggers[name]


# Default logger
default_logger = get_logger()


# Convenience functions
def log_debug(message: str, **kwargs):
    """Log debug message"""
    default_logger.debug(message, **kwargs)


def log_info(message: str, **kwargs):
    """Log info message"""
    default_logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message"""
    default_logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error message"""
    default_logger.error(message, **kwargs)


def log_critical(message: str, **kwargs):
    """Log critical message"""
    default_logger.critical(message, **kwargs)


def log_exception(message: str, **kwargs):
    """Log exception with traceback"""
    default_logger.exception(message, **kwargs)


def log_event(event_type: str, event_data: dict, level: int = logging.INFO):
    """Log structured event"""
    default_logger.log_event(event_type, event_data, level)

