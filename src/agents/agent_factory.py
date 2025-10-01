"""Agent factory for creating UAV subsystem agents."""

from typing import Dict, Type, List
from .base_agent import BaseAgent
from .navigation_agent import NavigationAgent
from .propulsion_agent import PropulsionAgent
from .communication_agent import CommunicationAgent
from .power_agent import PowerAgent
from .payload_agent import PayloadAgent
from .environmental_agent import EnvironmentalAgent
from .flight_control_agent import FlightControlAgent
from .sensor_fusion_agent import SensorFusionAgent
from .mission_planning_agent import MissionPlanningAgent
from .safety_systems_agent import SafetySystemsAgent
from .data_storage_agent import DataStorageAgent

from ..utils.config import config


class AgentFactory:
    """Factory for creating UAV subsystem agents."""
    
    # Registry of available agent classes
    AGENT_CLASSES: Dict[str, Type[BaseAgent]] = {
        "Navigation": NavigationAgent,
        "Propulsion": PropulsionAgent,
        "Communication": CommunicationAgent,
        "Power": PowerAgent,
        "Payload": PayloadAgent,
        "Environmental": EnvironmentalAgent,
        "Flight_Control": FlightControlAgent,
        "Sensor_Fusion": SensorFusionAgent,
        "Mission_Planning": MissionPlanningAgent,
        "Safety_Systems": SafetySystemsAgent,
        "Data_Storage": DataStorageAgent
    }
    
    @classmethod
    def create_agent(cls, uav_id: str, subsystem_name: str, telemetry_rate: float = None) -> BaseAgent:
        """Create an agent for a specific subsystem.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystem_name: Name of the subsystem
            telemetry_rate: Telemetry rate in Hz (optional)
            
        Returns:
            BaseAgent instance for the specified subsystem
            
        Raises:
            ValueError: If subsystem name is not recognized
        """
        if subsystem_name not in cls.AGENT_CLASSES:
            raise ValueError(f"Unknown subsystem: {subsystem_name}")
        
        agent_class = cls.AGENT_CLASSES[subsystem_name]
        
        # Get telemetry rate from config if not provided
        if telemetry_rate is None:
            telemetry_rate = cls._get_telemetry_rate_from_config(subsystem_name)
        
        return agent_class(uav_id, telemetry_rate)
    
    @classmethod
    def create_all_agents(cls, uav_id: str) -> Dict[str, BaseAgent]:
        """Create all available agents for a UAV.
        
        Args:
            uav_id: Unique identifier for the UAV
            
        Returns:
            Dictionary mapping subsystem names to agent instances
        """
        agents = {}
        
        for subsystem_name in cls.AGENT_CLASSES.keys():
            try:
                agent = cls.create_agent(uav_id, subsystem_name)
                agents[subsystem_name] = agent
            except Exception as e:
                print(f"Failed to create agent for {subsystem_name}: {e}")
        
        return agents
    
    @classmethod
    def get_available_subsystems(cls) -> List[str]:
        """Get list of available subsystem names.
        
        Returns:
            List of subsystem names
        """
        return list(cls.AGENT_CLASSES.keys())
    
    @classmethod
    def register_agent(cls, subsystem_name: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent class.
        
        Args:
            subsystem_name: Name of the subsystem
            agent_class: Agent class to register
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError("Agent class must inherit from BaseAgent")
        
        cls.AGENT_CLASSES[subsystem_name] = agent_class
    
    @classmethod
    def _get_telemetry_rate_from_config(cls, subsystem_name: str) -> float:
        """Get telemetry rate from configuration.
        
        Args:
            subsystem_name: Name of the subsystem
            
        Returns:
            Telemetry rate in Hz
        """
        # Get subsystem configuration
        subsystems = config.get("uav.subsystems", [])
        
        for subsystem in subsystems:
            if subsystem.get("name") == subsystem_name:
                return subsystem.get("telemetry_rate", 10.0)
        
        # Default telemetry rate if not found in config
        return 10.0
