"""Safety systems subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class SafetySystemsAgent(BaseAgent):
    """Agent for UAV safety systems subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 5.0):
        super().__init__(uav_id, "Safety_Systems", telemetry_rate)
        
        # Emergency systems
        self.emergency_systems = {
            "parachute_deployed": False,
            "parachute_status": "ready",  # ready, deployed, failed
            "emergency_landing_active": False,
            "rtl_active": False,  # Return to Launch
            "geofence_active": True,
            "geofence_violation": False,
            "emergency_stop": False
        }
        
        # Collision avoidance
        self.collision_avoidance = {
            "obstacle_detected": False,
            "obstacle_distance": 100.0,  # meters
            "obstacle_direction": 0.0,  # degrees
            "avoidance_maneuver": "none",  # none, climb, descend, turn_left, turn_right
            "safety_margin": 50.0,  # meters
            "detection_range": 200.0,  # meters
            "last_detection_time": None
        }
        
        # System health monitoring
        self.system_health = {
            "critical_systems_ok": True,
            "redundant_systems_active": True,
            "backup_power_available": True,
            "communication_backup_active": True,
            "navigation_backup_active": True,
            "propulsion_backup_active": True,
            "health_check_interval": 10,  # seconds
            "last_health_check": datetime.now()
        }
        
        # Safety limits and thresholds
        self.safety_limits = {
            "max_altitude": 400,  # meters
            "min_altitude": 10,  # meters
            "max_speed": 30,  # m/s
            "max_bank_angle": 45,  # degrees
            "max_pitch_angle": 30,  # degrees
            "min_battery_level": 20,  # %
            "min_fuel_level": 15,  # %
            "max_temperature": 60,  # °C
            "max_g_force": 3.0,  # g
            "min_signal_strength": -80  # dBm
        }
        
        # Safety events and alerts
        self.safety_events = {
            "total_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "last_alert_time": None,
            "alert_cooldown": 5,  # seconds
            "auto_responses": 0,
            "manual_interventions": 0
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate safety systems telemetry data."""
        self._update_emergency_systems()
        self._update_collision_avoidance()
        self._update_system_health()
        self._update_safety_events()
        
        data = {
            "emergency_systems": self.emergency_systems,
            "collision_avoidance": self.collision_avoidance,
            "system_health": self.system_health,
            "safety_limits": self.safety_limits,
            "safety_events": self.safety_events,
            "status": {
                "safety_systems_healthy": self._is_safety_systems_healthy(),
                "emergency_status": self._get_emergency_status(),
                "collision_risk": self._get_collision_risk(),
                "safety_margin": self._get_safety_margin()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply safety systems fault."""
        fault_type = fault_params.get("type", "parachute_failure")
        
        if fault_type == "parachute_failure":
            # Simulate parachute failure
            telemetry_data.data["emergency_systems"]["parachute_status"] = "failed"
            telemetry_data.data["emergency_systems"]["parachute_deployed"] = False
            
        elif fault_type == "collision_avoidance_failure":
            # Simulate collision avoidance failure
            telemetry_data.data["collision_avoidance"]["detection_range"] = 0.0
            telemetry_data.data["collision_avoidance"]["obstacle_detected"] = False
            
        elif fault_type == "geofence_failure":
            # Simulate geofence failure
            telemetry_data.data["emergency_systems"]["geofence_active"] = False
            telemetry_data.data["emergency_systems"]["geofence_violation"] = True
            
        elif fault_type == "backup_system_failure":
            # Simulate backup system failure
            backup_type = fault_params.get("backup_type", "power")
            if backup_type == "power":
                telemetry_data.data["system_health"]["backup_power_available"] = False
            elif backup_type == "communication":
                telemetry_data.data["system_health"]["communication_backup_active"] = False
            elif backup_type == "navigation":
                telemetry_data.data["system_health"]["navigation_backup_active"] = False
            elif backup_type == "propulsion":
                telemetry_data.data["system_health"]["propulsion_backup_active"] = False
                
        elif fault_type == "safety_limit_violation":
            # Simulate safety limit violation
            limit_type = fault_params.get("limit_type", "altitude")
            if limit_type == "altitude":
                telemetry_data.data["safety_limits"]["max_altitude"] = 100
            elif limit_type == "speed":
                telemetry_data.data["safety_limits"]["max_speed"] = 10
            elif limit_type == "battery":
                telemetry_data.data["safety_limits"]["min_battery_level"] = 50
                
        elif fault_type == "emergency_response_failure":
            # Simulate emergency response failure
            telemetry_data.data["emergency_systems"]["emergency_landing_active"] = False
            telemetry_data.data["emergency_systems"]["rtl_active"] = False
            telemetry_data.data["emergency_systems"]["emergency_stop"] = False
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_emergency_systems(self) -> None:
        """Update emergency systems status."""
        # Simulate parachute status changes
        if random.random() < 0.001:  # 0.1% chance
            if self.emergency_systems["parachute_status"] == "ready":
                self.emergency_systems["parachute_deployed"] = True
                self.emergency_systems["parachute_status"] = "deployed"
        
        # Simulate emergency landing activation
        if random.random() < 0.0005:  # 0.05% chance
            self.emergency_systems["emergency_landing_active"] = True
        
        # Simulate RTL activation
        if random.random() < 0.001:  # 0.1% chance
            self.emergency_systems["rtl_active"] = True
        
        # Simulate geofence violations
        if random.random() < 0.0001:  # 0.01% chance
            self.emergency_systems["geofence_violation"] = True
        
        # Simulate emergency stop
        if random.random() < 0.0001:  # 0.01% chance
            self.emergency_systems["emergency_stop"] = True
    
    def _update_collision_avoidance(self) -> None:
        """Update collision avoidance data."""
        # Simulate obstacle detection
        if random.random() < 0.01:  # 1% chance
            self.collision_avoidance["obstacle_detected"] = True
            self.collision_avoidance["obstacle_distance"] = random.uniform(10, 200)
            self.collision_avoidance["obstacle_direction"] = random.uniform(0, 360)
            self.collision_avoidance["last_detection_time"] = datetime.now()
        else:
            self.collision_avoidance["obstacle_detected"] = False
        
        # Update avoidance maneuver based on obstacle detection
        if self.collision_avoidance["obstacle_detected"]:
            maneuvers = ["climb", "descend", "turn_left", "turn_right"]
            self.collision_avoidance["avoidance_maneuver"] = random.choice(maneuvers)
        else:
            self.collision_avoidance["avoidance_maneuver"] = "none"
        
        # Simulate safety margin changes
        self.collision_avoidance["safety_margin"] += random.uniform(-2, 2)
        self.collision_avoidance["safety_margin"] = max(10, min(100, 
            self.collision_avoidance["safety_margin"]))
        
        # Simulate detection range changes
        self.collision_avoidance["detection_range"] += random.uniform(-5, 5)
        self.collision_avoidance["detection_range"] = max(50, min(500, 
            self.collision_avoidance["detection_range"]))
    
    def _update_system_health(self) -> None:
        """Update system health monitoring."""
        # Simulate critical systems status
        if random.random() < 0.001:  # 0.1% chance
            self.system_health["critical_systems_ok"] = not self.system_health["critical_systems_ok"]
        
        # Simulate redundant systems status
        if random.random() < 0.0005:  # 0.05% chance
            self.system_health["redundant_systems_active"] = not self.system_health["redundant_systems_active"]
        
        # Simulate backup system status changes
        backup_systems = [
            "backup_power_available",
            "communication_backup_active",
            "navigation_backup_active",
            "propulsion_backup_active"
        ]
        
        for system in backup_systems:
            if random.random() < 0.0001:  # 0.01% chance
                self.system_health[system] = not self.system_health[system]
        
        # Update health check interval
        self.system_health["health_check_interval"] += random.uniform(-1, 1)
        self.system_health["health_check_interval"] = max(5, min(30, 
            self.system_health["health_check_interval"]))
        
        # Update last health check time
        if random.random() < 0.1:  # 10% chance
            self.system_health["last_health_check"] = datetime.now()
    
    def _update_safety_events(self) -> None:
        """Update safety events and alerts."""
        # Simulate alert generation
        if random.random() < 0.001:  # 0.1% chance
            self.safety_events["total_alerts"] += 1
            
            # Determine alert severity
            if random.random() < 0.1:  # 10% chance of critical alert
                self.safety_events["critical_alerts"] += 1
            else:
                self.safety_events["warning_alerts"] += 1
            
            self.safety_events["last_alert_time"] = datetime.now()
        
        # Simulate auto responses
        if random.random() < 0.0005:  # 0.05% chance
            self.safety_events["auto_responses"] += 1
        
        # Simulate manual interventions
        if random.random() < 0.0001:  # 0.01% chance
            self.safety_events["manual_interventions"] += 1
        
        # Update alert cooldown
        self.safety_events["alert_cooldown"] += random.uniform(-0.5, 0.5)
        self.safety_events["alert_cooldown"] = max(1, min(10, 
            self.safety_events["alert_cooldown"]))
    
    def _is_safety_systems_healthy(self) -> bool:
        """Check if safety systems are healthy."""
        return (
            self.system_health["critical_systems_ok"] and
            self.system_health["redundant_systems_active"] and
            self.emergency_systems["parachute_status"] != "failed" and
            self.collision_avoidance["detection_range"] > 50 and
            not self.emergency_systems["geofence_violation"]
        )
    
    def _get_emergency_status(self) -> str:
        """Get emergency status."""
        if self.emergency_systems["emergency_stop"]:
            return "emergency_stop"
        elif self.emergency_systems["emergency_landing_active"]:
            return "emergency_landing"
        elif self.emergency_systems["rtl_active"]:
            return "return_to_launch"
        elif self.emergency_systems["parachute_deployed"]:
            return "parachute_deployed"
        else:
            return "normal"
    
    def _get_collision_risk(self) -> str:
        """Get collision risk level."""
        if self.collision_avoidance["obstacle_detected"]:
            distance = self.collision_avoidance["obstacle_distance"]
            if distance < 20:
                return "critical"
            elif distance < 50:
                return "high"
            elif distance < 100:
                return "medium"
            else:
                return "low"
        else:
            return "none"
    
    def _get_safety_margin(self) -> str:
        """Get safety margin status."""
        margin = self.collision_avoidance["safety_margin"]
        if margin > 80:
            return "excellent"
        elif margin > 60:
            return "good"
        elif margin > 40:
            return "adequate"
        else:
            return "poor"
