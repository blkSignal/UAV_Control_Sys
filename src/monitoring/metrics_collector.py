"""Metrics collection and monitoring system."""

import asyncio
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import deque, defaultdict
from loguru import logger

from ..utils.models import PerformanceMetrics, Alert, SeverityLevel
from ..utils.config import config
from .logger import uav_logger


class MetricsCollector:
    """Collects and monitors system performance metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.enabled = config.get("monitoring.performance_tracking.enabled", True)
        self.collection_interval = config.get("monitoring.monitoring_interval", 1.0)
        self.retention_period = config.get("monitoring.metrics_retention", 86400)
        
        # Thresholds
        self.cpu_threshold = config.get("monitoring.performance_tracking.cpu_threshold", 80)
        self.memory_threshold = config.get("monitoring.performance_tracking.memory_threshold", 85)
        self.disk_threshold = config.get("monitoring.performance_tracking.disk_threshold", 90)
        
        # Data storage
        self.metrics_history: deque = deque(maxlen=1000)
        self.alert_history: deque = deque(maxlen=100)
        
        # Statistics
        self.stats = {
            "total_metrics_collected": 0,
            "alerts_generated": 0,
            "threshold_violations": 0,
            "collection_errors": 0,
            "last_collection_time": None,
            "average_collection_time": 0.0
        }
        
        # Callbacks
        self.metrics_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        
        # Collection task
        self._collection_task: Optional[asyncio.Task] = None
        
        logger.info("MetricsCollector initialized")
    
    async def start(self) -> None:
        """Start metrics collection."""
        if not self.enabled:
            logger.info("Metrics collection is disabled")
            return
        
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Metrics collection started")
    
    async def stop(self) -> None:
        """Stop metrics collection."""
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Metrics collection stopped")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop."""
        while True:
            try:
                start_time = time.time()
                
                # Collect metrics
                metrics = await self._collect_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Check thresholds
                await self._check_thresholds(metrics)
                
                # Update statistics
                collection_time = time.time() - start_time
                self._update_statistics(collection_time)
                
                # Send to callbacks
                await self._send_metrics(metrics)
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                self.stats["collection_errors"] += 1
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics.
        
        Returns:
            PerformanceMetrics object
        """
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network latency (simplified)
            network_latency = await self._measure_network_latency()
            
            # Active connections (with error handling)
            try:
                connections = len(psutil.net_connections())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                connections = 0
            
            # Error rate (simplified)
            error_rate = self._calculate_error_rate()
            
            metrics = PerformanceMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_latency=network_latency,
                active_connections=connections,
                error_rate=error_rate
            )
            
            # Log performance metric
            uav_logger.log_performance("system_cpu_usage", cpu_usage, "%")
            uav_logger.log_performance("system_memory_usage", memory_usage, "%")
            uav_logger.log_performance("system_disk_usage", disk_usage, "%")
            uav_logger.log_performance("system_network_latency", network_latency, "ms")
            uav_logger.log_performance("system_active_connections", connections, "count")
            uav_logger.log_performance("system_error_rate", error_rate, "ratio")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            # Return default metrics
            return PerformanceMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_latency=0.0,
                active_connections=0,
                error_rate=0.0
            )
    
    async def _measure_network_latency(self) -> float:
        """Measure network latency.
        
        Returns:
            Network latency in milliseconds
        """
        try:
            # Simple ping to localhost (simplified)
            start_time = time.time()
            # Simulate network operation
            await asyncio.sleep(0.001)
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except Exception:
            return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate system error rate.
        
        Returns:
            Error rate as a ratio (0.0 to 1.0)
        """
        if self.stats["total_metrics_collected"] == 0:
            return 0.0
        
        return self.stats["collection_errors"] / self.stats["total_metrics_collected"]
    
    async def _check_thresholds(self, metrics: PerformanceMetrics) -> None:
        """Check metrics against thresholds and generate alerts.
        
        Args:
            metrics: Performance metrics to check
        """
        alerts = []
        
        # Check CPU threshold
        if metrics.cpu_usage > self.cpu_threshold:
            alerts.append({
                "type": "cpu_high",
                "value": metrics.cpu_usage,
                "threshold": self.cpu_threshold,
                "severity": SeverityLevel.HIGH if metrics.cpu_usage > 95 else SeverityLevel.MEDIUM
            })
        
        # Check memory threshold
        if metrics.memory_usage > self.memory_threshold:
            alerts.append({
                "type": "memory_high",
                "value": metrics.memory_usage,
                "threshold": self.memory_threshold,
                "severity": SeverityLevel.HIGH if metrics.memory_usage > 95 else SeverityLevel.MEDIUM
            })
        
        # Check disk threshold
        if metrics.disk_usage > self.disk_threshold:
            alerts.append({
                "type": "disk_high",
                "value": metrics.disk_usage,
                "threshold": self.disk_threshold,
                "severity": SeverityLevel.HIGH if metrics.disk_usage > 95 else SeverityLevel.MEDIUM
            })
        
        # Check network latency
        if metrics.network_latency > 100:  # 100ms threshold
            alerts.append({
                "type": "network_latency_high",
                "value": metrics.network_latency,
                "threshold": 100,
                "severity": SeverityLevel.MEDIUM
            })
        
        # Check error rate
        if metrics.error_rate > 0.1:  # 10% error rate threshold
            alerts.append({
                "type": "error_rate_high",
                "value": metrics.error_rate,
                "threshold": 0.1,
                "severity": SeverityLevel.HIGH
            })
        
        # Generate alerts
        for alert_data in alerts:
            await self._generate_alert(alert_data, metrics)
    
    async def _generate_alert(self, alert_data: Dict[str, Any], metrics: PerformanceMetrics) -> None:
        """Generate performance alert.
        
        Args:
            alert_data: Alert data
            metrics: Performance metrics
        """
        alert = Alert(
            uav_id="SYSTEM",
            subsystem="Performance",
            severity=alert_data["severity"],
            message=f"Performance threshold exceeded: {alert_data['type']} "
                   f"({alert_data['value']:.1f} > {alert_data['threshold']:.1f})",
            data={
                "metric_type": alert_data["type"],
                "current_value": alert_data["value"],
                "threshold": alert_data["threshold"],
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Store alert
        self.alert_history.append(alert)
        
        # Update statistics
        self.stats["alerts_generated"] += 1
        self.stats["threshold_violations"] += 1
        
        # Log alert
        uav_logger.log_alert(
            alert.uav_id,
            alert.subsystem,
            alert.severity.value,
            alert.message,
            alert.data
        )
        
        # Send to callbacks
        await self._send_alert(alert)
    
    async def _send_metrics(self, metrics: PerformanceMetrics) -> None:
        """Send metrics to registered callbacks.
        
        Args:
            metrics: Performance metrics
        """
        for callback in self.metrics_callbacks:
            try:
                await callback(metrics)
            except Exception as e:
                logger.error(f"Error in metrics callback: {e}")
    
    async def _send_alert(self, alert: Alert) -> None:
        """Send alert to registered callbacks.
        
        Args:
            alert: Performance alert
        """
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _update_statistics(self, collection_time: float) -> None:
        """Update collection statistics.
        
        Args:
            collection_time: Time taken to collect metrics
        """
        self.stats["total_metrics_collected"] += 1
        self.stats["last_collection_time"] = datetime.now()
        
        # Update average collection time
        if self.stats["total_metrics_collected"] == 1:
            self.stats["average_collection_time"] = collection_time
        else:
            current_avg = self.stats["average_collection_time"]
            count = self.stats["total_metrics_collected"]
            self.stats["average_collection_time"] = (current_avg * (count - 1) + collection_time) / count
    
    def register_metrics_callback(self, callback: Callable) -> None:
        """Register a callback for metrics data.
        
        Args:
            callback: Async callback function that receives PerformanceMetrics
        """
        self.metrics_callbacks.append(callback)
        logger.debug("Registered metrics callback")
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register a callback for performance alerts.
        
        Args:
            callback: Async callback function that receives Alert
        """
        self.alert_callbacks.append(callback)
        logger.debug("Registered performance alert callback")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent metrics.
        
        Returns:
            Most recent PerformanceMetrics or None if no metrics collected
        """
        if not self.metrics_history:
            return None
        
        return self.metrics_history[-1]
    
    def get_metrics_history(self, limit: Optional[int] = None) -> List[PerformanceMetrics]:
        """Get metrics history.
        
        Args:
            limit: Maximum number of metrics to return
            
        Returns:
            List of PerformanceMetrics
        """
        if limit is None:
            return list(self.metrics_history)
        
        return list(self.metrics_history)[-limit:]
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[Alert]:
        """Get alert history.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of Alerts
        """
        if limit is None:
            return list(self.alert_history)
        
        return list(self.alert_history)[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get metrics collection statistics.
        
        Returns:
            Dictionary containing statistics
        """
        stats = self.stats.copy()
        stats["enabled"] = self.enabled
        stats["collection_interval"] = self.collection_interval
        stats["metrics_history_size"] = len(self.metrics_history)
        stats["alert_history_size"] = len(self.alert_history)
        stats["thresholds"] = {
            "cpu": self.cpu_threshold,
            "memory": self.memory_threshold,
            "disk": self.disk_threshold
        }
        
        return stats
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the last N hours.
        
        Args:
            hours: Number of hours to summarize
            
        Returns:
            Dictionary containing metrics summary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics by time (simplified - assumes recent metrics)
        recent_metrics = list(self.metrics_history)[-min(3600, len(self.metrics_history)):]
        
        if not recent_metrics:
            return {}
        
        # Calculate statistics
        cpu_values = [m.cpu_usage for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        disk_values = [m.disk_usage for m in recent_metrics]
        latency_values = [m.network_latency for m in recent_metrics]
        
        summary = {
            "time_range_hours": hours,
            "sample_count": len(recent_metrics),
            "cpu": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": sum(cpu_values) / len(cpu_values),
                "current": cpu_values[-1] if cpu_values else 0
            },
            "memory": {
                "min": min(memory_values),
                "max": max(memory_values),
                "avg": sum(memory_values) / len(memory_values),
                "current": memory_values[-1] if memory_values else 0
            },
            "disk": {
                "min": min(disk_values),
                "max": max(disk_values),
                "avg": sum(disk_values) / len(disk_values),
                "current": disk_values[-1] if disk_values else 0
            },
            "network_latency": {
                "min": min(latency_values),
                "max": max(latency_values),
                "avg": sum(latency_values) / len(latency_values),
                "current": latency_values[-1] if latency_values else 0
            }
        }
        
        return summary
    
    def update_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Update performance thresholds.
        
        Args:
            thresholds: Dictionary of threshold updates
        """
        if "cpu" in thresholds:
            self.cpu_threshold = thresholds["cpu"]
        
        if "memory" in thresholds:
            self.memory_threshold = thresholds["memory"]
        
        if "disk" in thresholds:
            self.disk_threshold = thresholds["disk"]
        
        logger.info(f"Updated performance thresholds: {thresholds}")
    
    def clear_history(self) -> None:
        """Clear metrics and alert history."""
        self.metrics_history.clear()
        self.alert_history.clear()
        logger.info("Cleared metrics and alert history")
