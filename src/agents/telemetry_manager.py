"""Multi-agent telemetry management system."""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from loguru import logger

from .agent_factory import AgentFactory
from .base_agent import BaseAgent
from ..utils.models import TelemetryData, Alert, UAVState
from ..utils.config import config


class TelemetryManager:
    """Manages multiple UAV agents and their telemetry data."""
    
    def __init__(self):
        """Initialize telemetry manager."""
        self.uavs: Dict[str, Dict[str, BaseAgent]] = {}
        self.telemetry_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        self.is_running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info("TelemetryManager initialized")
    
    async def add_uav(self, uav_id: str, subsystems: Optional[List[str]] = None) -> None:
        """Add a UAV with its agents to the telemetry system.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystems: List of subsystem names to create (None for all)
        """
        if uav_id in self.uavs:
            logger.warning(f"UAV {uav_id} already exists")
            return
        
        # Create agents for the UAV
        if subsystems is None:
            agents = AgentFactory.create_all_agents(uav_id)
        else:
            agents = {}
            for subsystem_name in subsystems:
                try:
                    agent = AgentFactory.create_agent(uav_id, subsystem_name)
                    agents[subsystem_name] = agent
                except Exception as e:
                    logger.error(f"Failed to create agent {subsystem_name} for UAV {uav_id}: {e}")
        
        # Register callbacks for each agent
        for agent_name, agent in agents.items():
            agent.register_callback("telemetry", self._handle_telemetry)
            agent.register_callback("alert", self._handle_alert)
        
        self.uavs[uav_id] = agents
        logger.info(f"Added UAV {uav_id} with {len(agents)} agents")
    
    async def remove_uav(self, uav_id: str) -> None:
        """Remove a UAV and its agents from the telemetry system.
        
        Args:
            uav_id: Unique identifier for the UAV
        """
        if uav_id not in self.uavs:
            logger.warning(f"UAV {uav_id} not found")
            return
        
        # Stop all agents for this UAV
        agents = self.uavs[uav_id]
        for agent_name, agent in agents.items():
            await agent.stop()
        
        del self.uavs[uav_id]
        logger.info(f"Removed UAV {uav_id}")
    
    async def start(self) -> None:
        """Start the telemetry system."""
        if self.is_running:
            logger.warning("TelemetryManager is already running")
            return
        
        self.is_running = True
        
        # Start all agents for all UAVs
        for uav_id, agents in self.uavs.items():
            for agent_name, agent in agents.items():
                await agent.start()
                logger.debug(f"Started {agent_name} agent for UAV {uav_id}")
        
        logger.info("TelemetryManager started")
    
    async def stop(self) -> None:
        """Stop the telemetry system."""
        if not self.is_running:
            logger.warning("TelemetryManager is not running")
            return
        
        self.is_running = False
        
        # Stop all agents for all UAVs
        for uav_id, agents in self.uavs.items():
            for agent_name, agent in agents.items():
                await agent.stop()
                logger.debug(f"Stopped {agent_name} agent for UAV {uav_id}")
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        self._tasks.clear()
        logger.info("TelemetryManager stopped")
    
    async def inject_fault(self, uav_id: str, subsystem: str, fault_params: Dict[str, Any]) -> None:
        """Inject a fault into a specific subsystem.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystem: Name of the subsystem
            fault_params: Fault injection parameters
        """
        if uav_id not in self.uavs:
            logger.error(f"UAV {uav_id} not found")
            return
        
        if subsystem not in self.uavs[uav_id]:
            logger.error(f"Subsystem {subsystem} not found for UAV {uav_id}")
            return
        
        agent = self.uavs[uav_id][subsystem]
        await agent.inject_fault(fault_params)
        logger.info(f"Injected fault in {subsystem} for UAV {uav_id}")
    
    async def clear_fault(self, uav_id: str, subsystem: str) -> None:
        """Clear a fault from a specific subsystem.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystem: Name of the subsystem
        """
        if uav_id not in self.uavs:
            logger.error(f"UAV {uav_id} not found")
            return
        
        if subsystem not in self.uavs[uav_id]:
            logger.error(f"Subsystem {subsystem} not found for UAV {uav_id}")
            return
        
        agent = self.uavs[uav_id][subsystem]
        await agent.clear_fault()
        logger.info(f"Cleared fault in {subsystem} for UAV {uav_id}")
    
    def register_telemetry_callback(self, callback: Callable) -> None:
        """Register a callback for telemetry data.
        
        Args:
            callback: Async callback function that receives TelemetryData
        """
        self.telemetry_callbacks.append(callback)
        logger.debug("Registered telemetry callback")
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register a callback for alerts.
        
        Args:
            callback: Async callback function that receives Alert
        """
        self.alert_callbacks.append(callback)
        logger.debug("Registered alert callback")
    
    async def _handle_telemetry(self, telemetry_data: TelemetryData) -> None:
        """Handle incoming telemetry data.
        
        Args:
            telemetry_data: Telemetry data from an agent
        """
        # Send to registered callbacks
        for callback in self.telemetry_callbacks:
            try:
                await callback(telemetry_data)
            except Exception as e:
                logger.error(f"Error in telemetry callback: {e}")
    
    async def _handle_alert(self, alert: Alert) -> None:
        """Handle incoming alerts.
        
        Args:
            alert: Alert from an agent
        """
        # Send to registered callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def get_uav_status(self, uav_id: str) -> Optional[Dict[str, Any]]:
        """Get status of all agents for a UAV.
        
        Args:
            uav_id: Unique identifier for the UAV
            
        Returns:
            Dictionary containing agent statuses or None if UAV not found
        """
        if uav_id not in self.uavs:
            return None
        
        status = {}
        for agent_name, agent in self.uavs[uav_id].items():
            status[agent_name] = agent.get_status()
        
        return status
    
    def get_all_uav_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all UAVs and their agents.
        
        Returns:
            Dictionary mapping UAV IDs to their agent statuses
        """
        status = {}
        for uav_id in self.uavs.keys():
            status[uav_id] = self.get_uav_status(uav_id)
        
        return status
    
    def get_uav_count(self) -> int:
        """Get the number of UAVs in the system.
        
        Returns:
            Number of UAVs
        """
        return len(self.uavs)
    
    def get_agent_count(self) -> int:
        """Get the total number of agents in the system.
        
        Returns:
            Total number of agents across all UAVs
        """
        return sum(len(agents) for agents in self.uavs.values())
    
    def get_subsystem_count(self, uav_id: str) -> int:
        """Get the number of subsystems for a specific UAV.
        
        Args:
            uav_id: Unique identifier for the UAV
            
        Returns:
            Number of subsystems or 0 if UAV not found
        """
        if uav_id not in self.uavs:
            return 0
        
        return len(self.uavs[uav_id])
    
    async def get_uav_state(self, uav_id: str) -> Optional[UAVState]:
        """Get complete state of a UAV.
        
        Args:
            uav_id: Unique identifier for the UAV
            
        Returns:
            UAVState object or None if UAV not found
        """
        if uav_id not in self.uavs:
            return None
        
        # Collect data from all subsystems
        subsystems_data = {}
        overall_status = "nominal"
        
        for agent_name, agent in self.uavs[uav_id].items():
            agent_status = agent.get_status()
            subsystems_data[agent_name] = {
                "status": agent_status["status"],
                "is_running": agent_status["is_running"],
                "fault_active": agent_status["fault_active"]
            }
            
            # Determine overall status
            if agent_status["fault_active"]:
                overall_status = "error"
            elif agent_status["status"] == "warning" and overall_status == "nominal":
                overall_status = "warning"
        
        # Create UAV state
        uav_state = UAVState(
            uav_id=uav_id,
            subsystems=subsystems_data,
            overall_status=overall_status,
            position={"lat": 34.0522, "lon": -118.2437, "alt": 100},  # Default position
            mission_status="active",
            battery_level=75.0,
            flight_time=30.0
        )
        
        return uav_state
    
    async def get_all_uav_states(self) -> Dict[str, UAVState]:
        """Get complete state of all UAVs.
        
        Returns:
            Dictionary mapping UAV IDs to their states
        """
        states = {}
        for uav_id in self.uavs.keys():
            state = await self.get_uav_state(uav_id)
            if state:
                states[uav_id] = state
        
        return states
    
    async def get_telemetry(self, uav_id: str, subsystem: Optional[str] = None) -> List[TelemetryData]:
        """Get telemetry data for a UAV.
        
        Args:
            uav_id: UAV identifier
            subsystem: Optional subsystem filter
            
        Returns:
            List of telemetry data points
        """
        if uav_id not in self.uavs:
            return []
        
        telemetry_data = []
        for agent_name, agent in self.uavs[uav_id].items():
            if subsystem is None or agent_name == subsystem:
                # Get recent telemetry from agent
                if hasattr(agent, 'get_recent_telemetry'):
                    data = await agent.get_recent_telemetry()
                    telemetry_data.extend(data)
        
        return telemetry_data
