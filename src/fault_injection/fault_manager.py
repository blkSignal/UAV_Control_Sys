"""Fault injection and failure simulation manager."""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from loguru import logger

from ..utils.models import FaultScenario, Alert, SeverityLevel
from ..utils.config import config


class FaultType(str, Enum):
    """Types of faults that can be injected."""
    # Navigation faults
    GPS_DRIFT = "gps_drift"
    IMU_FAILURE = "imu_failure"
    COMPASS_ERROR = "compass_error"
    
    # Propulsion faults
    MOTOR_FAILURE = "motor_failure"
    ESC_FAILURE = "esc_failure"
    PROPELLER_DAMAGE = "propeller_damage"
    THRUST_REDUCTION = "thrust_reduction"
    
    # Communication faults
    SIGNAL_LOSS = "signal_loss"
    SATELLITE_LOSS = "satellite_loss"
    INTERFERENCE = "interference"
    ENCRYPTION_FAILURE = "encryption_failure"
    BANDWIDTH_REDUCTION = "bandwidth_reduction"
    
    # Power faults
    VOLTAGE_DROP = "voltage_drop"
    BATTERY_FAILURE = "battery_failure"
    OVERCURRENT = "overcurrent"
    THERMAL_RUNAWAY = "thermal_runaway"
    POWER_DISTRIBUTION_FAILURE = "power_distribution_failure"
    SOLAR_FAILURE = "solar_failure"
    
    # Payload faults
    CAMERA_FAILURE = "camera_failure"
    GIMBAL_FAILURE = "gimbal_failure"
    SENSOR_FAILURE = "sensor_failure"
    STORAGE_FAILURE = "storage_failure"
    DELIVERY_FAILURE = "delivery_failure"
    DATA_CORRUPTION = "data_corruption"
    
    # Environmental faults
    SENSOR_FAILURE_ENV = "sensor_failure_env"
    SEVERE_WEATHER = "severe_weather"
    AIR_POLLUTION = "air_pollution"
    RADIATION_SPIKE = "radiation_spike"
    ICING_CONDITIONS = "icing_conditions"
    
    # Flight control faults
    SERVO_FAILURE = "servo_failure"
    CONTROL_SURFACE_JAM = "control_surface_jam"
    AUTOPILOT_FAILURE = "autopilot_failure"
    FLY_BY_WIRE_FAILURE = "fly_by_wire_failure"
    CONTROL_AUTHORITY_LOSS = "control_authority_loss"
    TRIM_FAILURE = "trim_failure"
    
    # Sensor fusion faults
    IMU_FAILURE_SF = "imu_failure_sf"
    GPS_FAILURE_SF = "gps_failure_sf"
    BAROMETER_FAILURE = "barometer_failure"
    MAGNETOMETER_FAILURE = "magnetometer_failure"
    FUSION_ALGORITHM_FAILURE = "fusion_algorithm_failure"
    KALMAN_FILTER_DIVERGENCE = "kalman_filter_divergence"
    
    # Mission planning faults
    WAYPOINT_CORRUPTION = "waypoint_corruption"
    MISSION_ABORT = "mission_abort"
    CONSTRAINT_VIOLATION = "constraint_violation"
    REPLANNING_FAILURE = "replanning_failure"
    PROGRESS_CALCULATION_ERROR = "progress_calculation_error"
    
    # Safety systems faults
    PARACHUTE_FAILURE = "parachute_failure"
    COLLISION_AVOIDANCE_FAILURE = "collision_avoidance_failure"
    GEOFENCE_FAILURE = "geofence_failure"
    BACKUP_SYSTEM_FAILURE = "backup_system_failure"
    SAFETY_LIMIT_VIOLATION = "safety_limit_violation"
    EMERGENCY_RESPONSE_FAILURE = "emergency_response_failure"
    
    # Data storage faults
    STORAGE_FAILURE_DS = "storage_failure_ds"
    DATA_CORRUPTION_DS = "data_corruption_ds"
    TRANSMISSION_FAILURE = "transmission_failure"
    ENCRYPTION_FAILURE_DS = "encryption_failure_ds"
    BACKUP_FAILURE = "backup_failure"
    CAPACITY_EXHAUSTION = "capacity_exhaustion"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class FaultManager:
    """Manages fault injection and failure simulation."""
    
    def __init__(self):
        """Initialize fault manager."""
        self.enabled = config.get("fault_injection.enabled", True)
        self.max_concurrent_faults = config.get("fault_injection.max_concurrent_faults", 3)
        
        # Active faults
        self.active_faults: Dict[str, Dict[str, Any]] = {}
        
        # Fault scenarios from configuration
        self.fault_scenarios = self._load_fault_scenarios()
        
        # Statistics
        self.stats = {
            "total_faults_injected": 0,
            "total_faults_cleared": 0,
            "active_faults": 0,
            "faults_by_type": {},
            "faults_by_subsystem": {},
            "average_fault_duration": 0.0,
            "fault_success_rate": 0.0
        }
        
        # Callbacks
        self.fault_callbacks: List[Callable] = []
        
        # Fault injection task
        self._fault_task: Optional[asyncio.Task] = None
        
        logger.info("FaultManager initialized")
    
    def _load_fault_scenarios(self) -> List[FaultScenario]:
        """Load fault scenarios from configuration.
        
        Returns:
            List of fault scenarios
        """
        scenarios = []
        config_scenarios = config.get("fault_injection.scenarios", [])
        
        for scenario_config in config_scenarios:
            scenario = FaultScenario(
                name=scenario_config["name"],
                subsystem=scenario_config["subsystem"],
                probability=scenario_config["probability"],
                duration=scenario_config["duration"],
                severity=SeverityLevel(scenario_config["severity"]),
                parameters=scenario_config.get("parameters", {}),
                enabled=scenario_config.get("enabled", True)
            )
            scenarios.append(scenario)
        
        return scenarios
    
    async def start(self) -> None:
        """Start the fault injection system."""
        if not self.enabled:
            logger.info("Fault injection is disabled")
            return
        
        self._fault_task = asyncio.create_task(self._fault_injection_loop())
        logger.info("Fault injection system started")
    
    async def stop(self) -> None:
        """Stop the fault injection system."""
        if self._fault_task:
            self._fault_task.cancel()
            try:
                await self._fault_task
            except asyncio.CancelledError:
                pass
        
        # Clear all active faults
        await self.clear_all_faults()
        logger.info("Fault injection system stopped")
    
    async def inject_fault(self, uav_id: str, subsystem: str, fault_type: str, 
                          parameters: Optional[Dict[str, Any]] = None,
                          duration: Optional[int] = None) -> bool:
        """Inject a specific fault.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystem: Name of the subsystem
            fault_type: Type of fault to inject
            parameters: Fault parameters
            duration: Fault duration in seconds (None for default)
            
        Returns:
            True if fault was successfully injected
        """
        if not self.enabled:
            logger.warning("Fault injection is disabled")
            return False
        
        fault_key = f"{uav_id}_{subsystem}_{fault_type}"
        
        if fault_key in self.active_faults:
            logger.warning(f"Fault {fault_key} is already active")
            return False
        
        if len(self.active_faults) >= self.max_concurrent_faults:
            logger.warning(f"Maximum concurrent faults ({self.max_concurrent_faults}) reached")
            return False
        
        # Create fault data
        fault_data = {
            "uav_id": uav_id,
            "subsystem": subsystem,
            "fault_type": fault_type,
            "parameters": parameters or {},
            "duration": duration or 30,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(seconds=duration or 30),
            "severity": self._get_fault_severity(fault_type)
        }
        
        # Store active fault
        self.active_faults[fault_key] = fault_data
        
        # Update statistics
        self.stats["total_faults_injected"] += 1
        self.stats["active_faults"] = len(self.active_faults)
        
        if fault_type not in self.stats["faults_by_type"]:
            self.stats["faults_by_type"][fault_type] = 0
        self.stats["faults_by_type"][fault_type] += 1
        
        if subsystem not in self.stats["faults_by_subsystem"]:
            self.stats["faults_by_subsystem"][subsystem] = 0
        self.stats["faults_by_subsystem"][subsystem] += 1
        
        # Create alert
        alert = Alert(
            uav_id=uav_id,
            subsystem=subsystem,
            severity=fault_data["severity"],
            message=f"Fault injected: {fault_type}",
            data=fault_data
        )
        
        # Send to callbacks
        await self._send_fault_alert(alert)
        
        logger.info(f"Injected fault {fault_type} in {subsystem} for UAV {uav_id}")
        return True
    
    async def clear_fault(self, uav_id: str, subsystem: str, fault_type: str) -> bool:
        """Clear a specific fault.
        
        Args:
            uav_id: Unique identifier for the UAV
            subsystem: Name of the subsystem
            fault_type: Type of fault to clear
            
        Returns:
            True if fault was successfully cleared
        """
        fault_key = f"{uav_id}_{subsystem}_{fault_type}"
        
        if fault_key not in self.active_faults:
            logger.warning(f"Fault {fault_key} is not active")
            return False
        
        fault_data = self.active_faults[fault_key]
        del self.active_faults[fault_key]
        
        # Update statistics
        self.stats["total_faults_cleared"] += 1
        self.stats["active_faults"] = len(self.active_faults)
        
        # Calculate duration
        duration = (datetime.now() - fault_data["start_time"]).total_seconds()
        self._update_average_duration(duration)
        
        # Create alert
        alert = Alert(
            uav_id=uav_id,
            subsystem=subsystem,
            severity=SeverityLevel.LOW,
            message=f"Fault cleared: {fault_type}",
            data={"cleared": True, "duration": duration}
        )
        
        # Send to callbacks
        await self._send_fault_alert(alert)
        
        logger.info(f"Cleared fault {fault_type} in {subsystem} for UAV {uav_id}")
        return True
    
    async def clear_all_faults(self) -> None:
        """Clear all active faults."""
        fault_keys = list(self.active_faults.keys())
        
        for fault_key in fault_keys:
            fault_data = self.active_faults[fault_key]
            await self.clear_fault(
                fault_data["uav_id"],
                fault_data["subsystem"],
                fault_data["fault_type"]
            )
        
        logger.info("Cleared all active faults")
    
    async def _fault_injection_loop(self) -> None:
        """Main fault injection loop."""
        while True:
            try:
                # Check for expired faults
                await self._check_expired_faults()
                
                # Inject random faults based on scenarios
                await self._inject_random_faults()
                
                # Wait before next iteration
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in fault injection loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _check_expired_faults(self) -> None:
        """Check for and clear expired faults."""
        now = datetime.now()
        expired_faults = []
        
        for fault_key, fault_data in self.active_faults.items():
            if now >= fault_data["end_time"]:
                expired_faults.append(fault_key)
        
        for fault_key in expired_faults:
            fault_data = self.active_faults[fault_key]
            await self.clear_fault(
                fault_data["uav_id"],
                fault_data["subsystem"],
                fault_data["fault_type"]
            )
    
    async def _inject_random_faults(self) -> None:
        """Inject random faults based on configured scenarios."""
        if len(self.active_faults) >= self.max_concurrent_faults:
            return
        
        for scenario in self.fault_scenarios:
            if not scenario.enabled:
                continue
            
            # Check probability
            if random.random() < scenario.probability / 1000:  # Convert to per-second probability
                # Select random UAV (assuming we have UAVs available)
                uav_id = f"UAV_{random.randint(1, 5)}"  # This should be dynamic
                
                # Inject fault
                await self.inject_fault(
                    uav_id=uav_id,
                    subsystem=scenario.subsystem,
                    fault_type=self._get_fault_type_for_scenario(scenario),
                    parameters=scenario.parameters,
                    duration=scenario.duration
                )
    
    def _get_fault_type_for_scenario(self, scenario: FaultScenario) -> str:
        """Get fault type for a scenario.
        
        Args:
            scenario: Fault scenario
            
        Returns:
            Fault type string
        """
        # Map scenario names to fault types
        scenario_mapping = {
            "Power_Failure": FaultType.BATTERY_FAILURE,
            "Communication_Loss": FaultType.SIGNAL_LOSS,
            "Navigation_Drift": FaultType.GPS_DRIFT,
            "Sensor_Malfunction": FaultType.SENSOR_FAILURE,
            "Propulsion_Reduction": FaultType.THRUST_REDUCTION
        }
        
        return scenario_mapping.get(scenario.name, FaultType.SENSOR_FAILURE)
    
    def _get_fault_severity(self, fault_type: str) -> SeverityLevel:
        """Get severity level for a fault type.
        
        Args:
            fault_type: Type of fault
            
        Returns:
            Severity level
        """
        # Map fault types to severity levels
        severity_mapping = {
            # Critical faults
            FaultType.BATTERY_FAILURE: SeverityLevel.CRITICAL,
            FaultType.MOTOR_FAILURE: SeverityLevel.CRITICAL,
            FaultType.AUTOPILOT_FAILURE: SeverityLevel.CRITICAL,
            FaultType.PARACHUTE_FAILURE: SeverityLevel.CRITICAL,
            
            # High severity faults
            FaultType.SIGNAL_LOSS: SeverityLevel.HIGH,
            FaultType.GPS_FAILURE_SF: SeverityLevel.HIGH,
            FaultType.THRUST_REDUCTION: SeverityLevel.HIGH,
            FaultType.CONTROL_AUTHORITY_LOSS: SeverityLevel.HIGH,
            
            # Medium severity faults
            FaultType.GPS_DRIFT: SeverityLevel.MEDIUM,
            FaultType.SENSOR_FAILURE: SeverityLevel.MEDIUM,
            FaultType.CAMERA_FAILURE: SeverityLevel.MEDIUM,
            FaultType.INTERFERENCE: SeverityLevel.MEDIUM,
            
            # Low severity faults
            FaultType.DATA_CORRUPTION: SeverityLevel.LOW,
            FaultType.PERFORMANCE_DEGRADATION: SeverityLevel.LOW
        }
        
        return severity_mapping.get(fault_type, SeverityLevel.MEDIUM)
    
    def _update_average_duration(self, duration: float) -> None:
        """Update average fault duration.
        
        Args:
            duration: Fault duration in seconds
        """
        if self.stats["total_faults_cleared"] == 1:
            self.stats["average_fault_duration"] = duration
        else:
            # Calculate running average
            current_avg = self.stats["average_fault_duration"]
            count = self.stats["total_faults_cleared"]
            self.stats["average_fault_duration"] = (current_avg * (count - 1) + duration) / count
    
    async def _send_fault_alert(self, alert: Alert) -> None:
        """Send fault alert to callbacks.
        
        Args:
            alert: Alert to send
        """
        for callback in self.fault_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in fault callback: {e}")
    
    def register_fault_callback(self, callback: Callable) -> None:
        """Register a callback for fault events.
        
        Args:
            callback: Async callback function that receives Alert
        """
        self.fault_callbacks.append(callback)
        logger.debug("Registered fault callback")
    
    def get_active_faults(self, uav_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get all active faults.
        
        Args:
            uav_id: Optional UAV ID to filter faults
            
        Returns:
            Dictionary of active faults
        """
        if uav_id is None:
            return self.active_faults.copy()
        else:
            # Filter faults for specific UAV
            filtered_faults = {}
            for fault_id, fault_data in self.active_faults.items():
                if fault_data.get('uav_id') == uav_id:
                    filtered_faults[fault_id] = fault_data
            return filtered_faults
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fault injection statistics.
        
        Returns:
            Dictionary containing statistics
        """
        stats = self.stats.copy()
        stats["enabled"] = self.enabled
        stats["max_concurrent_faults"] = self.max_concurrent_faults
        stats["fault_scenarios"] = len(self.fault_scenarios)
        
        # Calculate success rate
        total_attempts = stats["total_faults_injected"] + stats["total_faults_cleared"]
        if total_attempts > 0:
            stats["fault_success_rate"] = stats["total_faults_injected"] / total_attempts
        else:
            stats["fault_success_rate"] = 0.0
        
        return stats
    
    def get_fault_scenarios(self) -> List[FaultScenario]:
        """Get all fault scenarios.
        
        Returns:
            List of fault scenarios
        """
        return self.fault_scenarios.copy()
    
    def add_fault_scenario(self, scenario: FaultScenario) -> None:
        """Add a new fault scenario.
        
        Args:
            scenario: Fault scenario to add
        """
        self.fault_scenarios.append(scenario)
        logger.info(f"Added fault scenario: {scenario.name}")
    
    def remove_fault_scenario(self, scenario_name: str) -> bool:
        """Remove a fault scenario.
        
        Args:
            scenario_name: Name of the scenario to remove
            
        Returns:
            True if scenario was removed
        """
        for i, scenario in enumerate(self.fault_scenarios):
            if scenario.name == scenario_name:
                del self.fault_scenarios[i]
                logger.info(f"Removed fault scenario: {scenario_name}")
                return True
        
        logger.warning(f"Fault scenario not found: {scenario_name}")
        return False
    
    async def get_fault_statistics(self, uav_id: str) -> Dict[str, Any]:
        """Get fault statistics for a specific UAV.
        
        Args:
            uav_id: UAV identifier
            
        Returns:
            Dictionary containing fault statistics for the UAV
        """
        uav_faults = self.get_active_faults(uav_id)
        return {
            "uav_id": uav_id,
            "active_faults": len(uav_faults),
            "faults": uav_faults,
            "total_injected": self.stats.get("total_faults_injected", 0),
            "total_cleared": self.stats.get("total_faults_cleared", 0)
        }
