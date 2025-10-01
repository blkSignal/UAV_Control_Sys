"""Base agent class for UAV subsystems."""

import asyncio
import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from loguru import logger

from ..utils.models import TelemetryData, SystemStatus, SeverityLevel, Alert
from ..utils.config import config


class BaseAgent(ABC):
    """Base class for all UAV subsystem agents."""
    
    def __init__(self, uav_id: str, subsystem_name: str, telemetry_rate: float = 10.0):
        """Initialize base agent.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystem_name: Name of the subsystem
            telemetry_rate: Telemetry data generation rate in Hz
        """
        self.uav_id = uav_id
        self.subsystem_name = subsystem_name
        self.telemetry_rate = telemetry_rate
        self.status = SystemStatus.NOMINAL
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._callbacks: Dict[str, Callable] = {}
        self._fault_active = False
        self._fault_params: Dict[str, Any] = {}
        self._telemetry_history: List[TelemetryData] = []
        
        logger.info(f"Initialized {subsystem_name} agent for UAV {uav_id}")
    
    async def start(self) -> None:
        """Start the agent telemetry generation."""
        if self.is_running:
            logger.warning(f"Agent {self.subsystem_name} is already running")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._telemetry_loop())
        logger.info(f"Started {self.subsystem_name} agent for UAV {self.uav_id}")
    
    async def stop(self) -> None:
        """Stop the agent telemetry generation."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"Stopped {self.subsystem_name} agent for UAV {self.uav_id}")
    
    async def _telemetry_loop(self) -> None:
        """Main telemetry generation loop."""
        interval = 1.0 / self.telemetry_rate
        
        while self.is_running:
            try:
                # Generate telemetry data
                telemetry_data = await self.generate_telemetry()
                
                # Apply fault injection if active
                if self._fault_active:
                    telemetry_data = await self._apply_fault(telemetry_data)
                
                # Send telemetry data
                await self._send_telemetry(telemetry_data)
                
                # Wait for next iteration
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in telemetry loop for {self.subsystem_name}: {e}")
                await asyncio.sleep(interval)
    
    @abstractmethod
    async def generate_telemetry(self) -> TelemetryData:
        """Generate telemetry data for the subsystem.
        
        Returns:
            TelemetryData object containing subsystem-specific data
        """
        pass
    
    @abstractmethod
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply fault injection to telemetry data.
        
        Args:
            telemetry_data: Original telemetry data
            fault_params: Fault injection parameters
            
        Returns:
            Modified telemetry data with fault applied
        """
        pass
    
    async def _apply_fault(self, telemetry_data: TelemetryData) -> TelemetryData:
        """Internal method to apply active fault."""
        try:
            return await self.apply_fault(telemetry_data, self._fault_params)
        except Exception as e:
            logger.error(f"Error applying fault to {self.subsystem_name}: {e}")
            return telemetry_data
    
    async def _send_telemetry(self, telemetry_data: TelemetryData) -> None:
        """Send telemetry data to registered callbacks."""
        # Store in history
        self._telemetry_history.append(telemetry_data)
        
        # Keep only recent data (last 100 points)
        if len(self._telemetry_history) > 100:
            self._telemetry_history = self._telemetry_history[-100:]
        
        # Send to callbacks
        for callback_name, callback in self._callbacks.items():
            try:
                await callback(telemetry_data)
            except Exception as e:
                logger.error(f"Error in callback {callback_name}: {e}")
    
    def register_callback(self, name: str, callback: Callable) -> None:
        """Register a callback for telemetry data.
        
        Args:
            name: Callback name
            callback: Async callback function
        """
        self._callbacks[name] = callback
        logger.debug(f"Registered callback {name} for {self.subsystem_name}")
    
    def unregister_callback(self, name: str) -> None:
        """Unregister a callback.
        
        Args:
            name: Callback name to remove
        """
        if name in self._callbacks:
            del self._callbacks[name]
            logger.debug(f"Unregistered callback {name} for {self.subsystem_name}")
    
    async def inject_fault(self, fault_params: Dict[str, Any]) -> None:
        """Inject a fault into the subsystem.
        
        Args:
            fault_params: Fault injection parameters
        """
        self._fault_active = True
        self._fault_params = fault_params
        self.status = SystemStatus.ERROR
        
        # Generate alert
        alert = Alert(
            uav_id=self.uav_id,
            subsystem=self.subsystem_name,
            severity=SeverityLevel.HIGH,
            message=f"Fault injected in {self.subsystem_name}",
            data=fault_params
        )
        
        await self._send_alert(alert)
        logger.warning(f"Fault injected in {self.subsystem_name} for UAV {self.uav_id}")
    
    async def clear_fault(self) -> None:
        """Clear active fault."""
        self._fault_active = False
        self._fault_params = {}
        self.status = SystemStatus.NOMINAL
        
        # Generate alert
        alert = Alert(
            uav_id=self.uav_id,
            subsystem=self.subsystem_name,
            severity=SeverityLevel.LOW,
            message=f"Fault cleared in {self.subsystem_name}",
            data={"cleared": True}
        )
        
        await self._send_alert(alert)
        logger.info(f"Fault cleared in {self.subsystem_name} for UAV {self.uav_id}")
    
    async def _send_alert(self, alert: Alert) -> None:
        """Send alert to registered callbacks."""
        if "alert" in self._callbacks:
            try:
                await self._callbacks["alert"](alert)
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "uav_id": self.uav_id,
            "subsystem": self.subsystem_name,
            "status": self.status.value,
            "is_running": self.is_running,
            "telemetry_rate": self.telemetry_rate,
            "fault_active": self._fault_active,
            "fault_params": self._fault_params
        }
    
    async def get_recent_telemetry(self, count: int = 10) -> List[TelemetryData]:
        """Get recent telemetry data from this agent.
        
        Args:
            count: Number of recent data points to return
            
        Returns:
            List of recent telemetry data
        """
        return self._telemetry_history[-count:] if self._telemetry_history else []
