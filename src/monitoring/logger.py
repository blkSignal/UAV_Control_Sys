"""Advanced logging system for UAV simulator."""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from loguru._logger import Logger

from ..utils.config import config


class UAVLogger:
    """Advanced logging system for UAV simulator."""
    
    def __init__(self):
        """Initialize UAV logger."""
        self.log_level = config.get("monitoring.log_level", "INFO")
        self.log_file = config.get("monitoring.log_file", "logs/uav_simulator.log")
        self.metrics_retention = config.get("monitoring.metrics_retention", 86400)
        
        # Create logs directory
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure loguru
        self._configure_logger()
        
        # Performance tracking
        self.performance_tracking = config.get("monitoring.performance_tracking", {})
        self.enabled = self.performance_tracking.get("enabled", True)
        
        # Alert cooldown
        self.alert_cooldown = config.get("monitoring.alert_cooldown", 60)
        self.last_alerts: Dict[str, datetime] = {}
        
        logger.info("UAVLogger initialized")
    
    def _configure_logger(self) -> None:
        """Configure loguru logger."""
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stdout,
            level=self.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True
        )
        
        # Add file handler
        logger.add(
            self.log_file,
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8"
        )
        
        # Add error file handler
        error_log_file = str(Path(self.log_file).parent / "errors.log")
        logger.add(
            error_log_file,
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="50 MB",
            retention="90 days",
            compression="zip",
            encoding="utf-8"
        )
        
        # Add performance log file
        perf_log_file = str(Path(self.log_file).parent / "performance.log")
        logger.add(
            perf_log_file,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            filter=lambda record: "PERFORMANCE" in record["extra"],
            rotation="50 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8"
        )
    
    def log_telemetry(self, uav_id: str, subsystem: str, data: Dict[str, Any]) -> None:
        """Log telemetry data.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            data: Telemetry data
        """
        logger.bind(
            uav_id=uav_id,
            subsystem=subsystem,
            log_type="telemetry"
        ).info(f"Telemetry: {subsystem} for UAV {uav_id}")
    
    def log_anomaly(self, uav_id: str, subsystem: str, anomaly_score: float, 
                    features: Dict[str, Any]) -> None:
        """Log anomaly detection result.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            anomaly_score: Anomaly score
            features: Features used for detection
        """
        logger.bind(
            uav_id=uav_id,
            subsystem=subsystem,
            log_type="anomaly",
            anomaly_score=anomaly_score
        ).warning(f"Anomaly detected: {subsystem} for UAV {uav_id} (score: {anomaly_score:.3f})")
    
    def log_fault(self, uav_id: str, subsystem: str, fault_type: str, 
                  parameters: Dict[str, Any]) -> None:
        """Log fault injection.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            fault_type: Type of fault
            parameters: Fault parameters
        """
        logger.bind(
            uav_id=uav_id,
            subsystem=subsystem,
            log_type="fault",
            fault_type=fault_type
        ).warning(f"Fault injected: {fault_type} in {subsystem} for UAV {uav_id}")
    
    def log_alert(self, uav_id: str, subsystem: str, severity: str, 
                  message: str, data: Dict[str, Any]) -> None:
        """Log alert.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            severity: Alert severity
            message: Alert message
            data: Alert data
        """
        # Check alert cooldown
        alert_key = f"{uav_id}_{subsystem}_{severity}"
        now = datetime.now()
        
        if alert_key in self.last_alerts:
            time_since_last = (now - self.last_alerts[alert_key]).total_seconds()
            if time_since_last < self.alert_cooldown:
                return  # Skip due to cooldown
        
        self.last_alerts[alert_key] = now
        
        log_level = "ERROR" if severity == "critical" else "WARNING"
        
        logger.bind(
            uav_id=uav_id,
            subsystem=subsystem,
            log_type="alert",
            severity=severity
        ).log(log_level, f"Alert: {message}")
    
    def log_performance(self, metric_name: str, value: float, 
                       unit: str = "", metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        metadata = metadata or {}
        log_data = {
            "metric": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        
        logger.bind(PERFORMANCE=True).info(json.dumps(log_data))
    
    def log_system_event(self, event_type: str, message: str, 
                         data: Optional[Dict[str, Any]] = None) -> None:
        """Log system event.
        
        Args:
            event_type: Type of event
            message: Event message
            data: Event data
        """
        logger.bind(
            log_type="system_event",
            event_type=event_type
        ).info(f"System Event: {message}")
    
    def log_user_action(self, user_id: str, action: str, 
                        target: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log user action.
        
        Args:
            user_id: User identifier
            action: Action performed
            target: Target of the action
            data: Action data
        """
        logger.bind(
            log_type="user_action",
            user_id=user_id,
            action=action,
            target=target
        ).info(f"User Action: {user_id} {action} {target}")
    
    def log_security_event(self, event_type: str, message: str, 
                           severity: str = "medium", data: Optional[Dict[str, Any]] = None) -> None:
        """Log security event.
        
        Args:
            event_type: Type of security event
            message: Event message
            severity: Event severity
            data: Event data
        """
        log_level = "ERROR" if severity == "high" else "WARNING"
        
        logger.bind(
            log_type="security_event",
            event_type=event_type,
            severity=severity
        ).log(log_level, f"Security Event: {message}")
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                        response_time: float, user_id: Optional[str] = None) -> None:
        """Log API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: Response status code
            response_time: Response time in seconds
            user_id: User identifier (optional)
        """
        log_level = "ERROR" if status_code >= 400 else "INFO"
        
        logger.bind(
            log_type="api_request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            user_id=user_id
        ).log(log_level, f"API Request: {method} {endpoint} -> {status_code} ({response_time:.3f}s)")
    
    def log_database_operation(self, operation: str, table: str, 
                              duration: float, success: bool) -> None:
        """Log database operation.
        
        Args:
            operation: Database operation type
            table: Database table name
            duration: Operation duration in seconds
            success: Whether operation was successful
        """
        log_level = "ERROR" if not success else "INFO"
        
        logger.bind(
            log_type="database_operation",
            operation=operation,
            table=table,
            duration=duration,
            success=success
        ).log(log_level, f"Database: {operation} {table} ({duration:.3f}s) - {'SUCCESS' if success else 'FAILED'}")
    
    def log_external_service(self, service_name: str, operation: str, 
                            status: str, duration: float, data: Optional[Dict[str, Any]] = None) -> None:
        """Log external service interaction.
        
        Args:
            service_name: Name of external service
            operation: Operation performed
            status: Operation status
            duration: Operation duration in seconds
            data: Additional data
        """
        log_level = "ERROR" if status == "failed" else "INFO"
        
        logger.bind(
            log_type="external_service",
            service_name=service_name,
            operation=operation,
            status=status,
            duration=duration
        ).log(log_level, f"External Service: {service_name} {operation} -> {status} ({duration:.3f}s)")
    
    def get_logger(self, name: str) -> Logger:
        """Get a logger instance for a specific component.
        
        Args:
            name: Component name
            
        Returns:
            Logger instance
        """
        return logger.bind(component=name)
    
    def set_log_level(self, level: str) -> None:
        """Set the logging level.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level.upper()
        logger.remove()
        self._configure_logger()
        logger.info(f"Log level changed to {self.log_level}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics.
        
        Returns:
            Dictionary containing logging statistics
        """
        log_path = Path(self.log_file)
        
        stats = {
            "log_level": self.log_level,
            "log_file": self.log_file,
            "log_file_exists": log_path.exists(),
            "log_file_size": log_path.stat().st_size if log_path.exists() else 0,
            "performance_tracking_enabled": self.enabled,
            "alert_cooldown": self.alert_cooldown,
            "active_alert_cooldowns": len(self.last_alerts)
        }
        
        return stats


# Global logger instance
uav_logger = UAVLogger()
