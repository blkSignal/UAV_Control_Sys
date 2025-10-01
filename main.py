"""Main entry point for UAV Mission Control & Anomaly Detection Simulator."""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agents.telemetry_manager import TelemetryManager
from src.anomaly.anomaly_detector import AnomalyDetector
from src.fault_injection.fault_manager import FaultManager
from src.monitoring.logger import uav_logger
from src.monitoring.metrics_collector import MetricsCollector
from src.utils.config import config
from src.utils.models import TelemetryData, Alert


class UAVSimulator:
    """Main UAV Mission Control & Anomaly Detection Simulator."""
    
    def __init__(self):
        """Initialize the UAV simulator."""
        self.telemetry_manager = TelemetryManager()
        self.anomaly_detector = AnomalyDetector()
        self.fault_manager = FaultManager()
        self.metrics_collector = MetricsCollector()
        
        self.is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Register callbacks
        self._register_callbacks()
        
        logger.info("UAV Simulator initialized")
    
    def _register_callbacks(self) -> None:
        """Register callbacks between components."""
        # Telemetry callbacks
        self.telemetry_manager.register_telemetry_callback(self._handle_telemetry)
        self.telemetry_manager.register_alert_callback(self._handle_alert)
        
        # Anomaly detection callbacks
        self.anomaly_detector.register_anomaly_callback(self._handle_anomaly_alert)
        
        # Fault injection callbacks
        self.fault_manager.register_fault_callback(self._handle_fault_alert)
        
        # Metrics callbacks
        self.metrics_collector.register_metrics_callback(self._handle_metrics)
        self.metrics_collector.register_alert_callback(self._handle_performance_alert)
    
    async def _handle_telemetry(self, telemetry_data: TelemetryData) -> None:
        """Handle incoming telemetry data.
        
        Args:
            telemetry_data: Telemetry data from UAV agents
        """
        # Log telemetry
        uav_logger.log_telemetry(
            telemetry_data.uav_id,
            telemetry_data.subsystem,
            telemetry_data.data
        )
        
        # Process for anomaly detection
        anomaly_result = await self.anomaly_detector.process_telemetry(telemetry_data)
        
        # Update telemetry data with anomaly score
        telemetry_data.anomaly_score = anomaly_result.anomaly_score
    
    async def _handle_alert(self, alert: Alert) -> None:
        """Handle alerts from UAV agents.
        
        Args:
            alert: Alert from UAV agent
        """
        uav_logger.log_alert(
            alert.uav_id,
            alert.subsystem,
            alert.severity.value,
            alert.message,
            alert.data
        )
    
    async def _handle_anomaly_alert(self, alert: Alert) -> None:
        """Handle anomaly detection alerts.
        
        Args:
            alert: Anomaly alert
        """
        uav_logger.log_anomaly(
            alert.uav_id,
            alert.subsystem,
            alert.data.get("anomaly_score", 0.0),
            alert.data.get("features", {})
        )
    
    async def _handle_fault_alert(self, alert: Alert) -> None:
        """Handle fault injection alerts.
        
        Args:
            alert: Fault alert
        """
        uav_logger.log_fault(
            alert.uav_id,
            alert.subsystem,
            alert.data.get("fault_type", "unknown"),
            alert.data
        )
    
    async def _handle_metrics(self, metrics) -> None:
        """Handle performance metrics.
        
        Args:
            metrics: Performance metrics
        """
        # Metrics are already logged by the collector
        pass
    
    async def _handle_performance_alert(self, alert: Alert) -> None:
        """Handle performance alerts.
        
        Args:
            alert: Performance alert
        """
        uav_logger.log_alert(
            alert.uav_id,
            alert.subsystem,
            alert.severity.value,
            alert.message,
            alert.data
        )
    
    async def start(self) -> None:
        """Start the UAV simulator."""
        if self.is_running:
            logger.warning("UAV Simulator is already running")
            return
        
        logger.info("Starting UAV Mission Control & Anomaly Detection Simulator")
        
        try:
            # Start components
            await self.telemetry_manager.start()
            await self.fault_manager.start()
            await self.metrics_collector.start()
            
            # Add UAVs
            await self._add_uavs()
            
            self.is_running = True
            logger.info("UAV Simulator started successfully")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error starting UAV Simulator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the UAV simulator."""
        if not self.is_running:
            logger.warning("UAV Simulator is not running")
            return
        
        logger.info("Stopping UAV Simulator")
        
        try:
            # Stop components
            await self.telemetry_manager.stop()
            await self.fault_manager.stop()
            await self.metrics_collector.stop()
            
            self.is_running = False
            logger.info("UAV Simulator stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping UAV Simulator: {e}")
            raise
    
    async def _add_uavs(self) -> None:
        """Add UAVs to the simulation."""
        uav_count = config.get("uav.count", 5)
        
        for i in range(1, uav_count + 1):
            uav_id = f"UAV_{i:03d}"
            await self.telemetry_manager.add_uav(uav_id)
            logger.info(f"Added {uav_id} to simulation")
    
    async def inject_fault(self, uav_id: str, subsystem: str, fault_type: str, 
                          parameters: Dict[str, Any] = None) -> bool:
        """Inject a fault into a UAV subsystem.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            fault_type: Type of fault to inject
            parameters: Fault parameters
            
        Returns:
            True if fault was successfully injected
        """
        return await self.fault_manager.inject_fault(uav_id, subsystem, fault_type, parameters)
    
    async def clear_fault(self, uav_id: str, subsystem: str, fault_type: str) -> bool:
        """Clear a fault from a UAV subsystem.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            fault_type: Type of fault to clear
            
        Returns:
            True if fault was successfully cleared
        """
        return await self.fault_manager.clear_fault(uav_id, subsystem, fault_type)
    
    def get_status(self) -> Dict[str, Any]:
        """Get simulator status.
        
        Returns:
            Dictionary containing simulator status
        """
        return {
            "is_running": self.is_running,
            "uav_count": self.telemetry_manager.get_uav_count(),
            "agent_count": self.telemetry_manager.get_agent_count(),
            "active_faults": len(self.fault_manager.get_active_faults()),
            "anomaly_stats": self.anomaly_detector.get_statistics(),
            "fault_stats": self.fault_manager.get_statistics(),
            "metrics_stats": self.metrics_collector.get_statistics(),
            "log_stats": uav_logger.get_log_statistics()
        }
    
    def get_uav_status(self, uav_id: str) -> Dict[str, Any]:
        """Get status of a specific UAV.
        
        Args:
            uav_id: UAV identifier
            
        Returns:
            Dictionary containing UAV status
        """
        return self.telemetry_manager.get_uav_status(uav_id)
    
    def get_all_uav_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all UAVs.
        
        Returns:
            Dictionary containing all UAV statuses
        """
        return self.telemetry_manager.get_all_uav_status()


async def main():
    """Main function."""
    # Create simulator
    simulator = UAVSimulator()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        simulator._shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start simulator
        await simulator.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Simulator error: {e}")
        sys.exit(1)
    finally:
        # Stop simulator
        await simulator.stop()
        logger.info("UAV Simulator shutdown complete")


if __name__ == "__main__":
    # Run the simulator
    asyncio.run(main())
