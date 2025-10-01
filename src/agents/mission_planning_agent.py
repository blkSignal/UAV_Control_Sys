"""Mission planning subsystem agent."""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class MissionPlanningAgent(BaseAgent):
    """Agent for UAV mission planning subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 2.0):
        super().__init__(uav_id, "Mission_Planning", telemetry_rate)
        
        # Mission data
        self.mission_data = {
            "mission_id": "MISSION_001",
            "mission_name": "Surveillance_Patrol",
            "mission_type": "surveillance",
            "status": "active",  # planned, active, paused, completed, failed
            "priority": "medium",  # low, medium, high, critical
            "start_time": datetime.now(),
            "estimated_duration": 120,  # minutes
            "current_phase": "execution"
        }
        
        # Waypoint data
        self.waypoint_data = {
            "total_waypoints": 8,
            "current_waypoint": 3,
            "waypoints": [
                {"id": 1, "lat": 34.0522, "lon": -118.2437, "alt": 100, "action": "takeoff", "completed": True},
                {"id": 2, "lat": 34.0622, "lon": -118.2537, "alt": 150, "action": "fly_to", "completed": True},
                {"id": 3, "lat": 34.0722, "lon": -118.2637, "alt": 200, "action": "survey", "completed": False},
                {"id": 4, "lat": 34.0822, "lon": -118.2737, "alt": 200, "action": "survey", "completed": False},
                {"id": 5, "lat": 34.0922, "lon": -118.2837, "alt": 200, "action": "survey", "completed": False},
                {"id": 6, "lat": 34.1022, "lon": -118.2937, "alt": 200, "action": "survey", "completed": False},
                {"id": 7, "lat": 34.1122, "lon": -118.3037, "alt": 150, "action": "return", "completed": False},
                {"id": 8, "lat": 34.0522, "lon": -118.2437, "alt": 0, "action": "land", "completed": False}
            ]
        }
        
        # Mission progress
        self.mission_progress = {
            "completion_percentage": 25.0,  # %
            "distance_traveled": 5.2,  # km
            "distance_remaining": 15.8,  # km
            "time_elapsed": 30,  # minutes
            "time_remaining": 90,  # minutes
            "fuel_consumed": 25.0,  # %
            "fuel_remaining": 75.0,  # %
            "battery_consumed": 20.0,  # %
            "battery_remaining": 80.0  # %
        }
        
        # Mission constraints
        self.mission_constraints = {
            "max_altitude": 400,  # meters
            "min_altitude": 50,  # meters
            "max_speed": 30,  # m/s
            "min_speed": 5,  # m/s
            "no_fly_zones": [
                {"lat": 34.1000, "lon": -118.3000, "radius": 1000}
            ],
            "weather_limits": {
                "max_wind_speed": 15,  # m/s
                "max_precipitation": 5,  # mm/h
                "min_visibility": 2  # km
            },
            "time_constraints": {
                "max_flight_time": 180,  # minutes
                "daylight_only": True,
                "curfew_start": "22:00",
                "curfew_end": "06:00"
            }
        }
        
        # Mission performance
        self.mission_performance = {
            "waypoint_accuracy": 2.5,  # meters
            "altitude_accuracy": 1.2,  # meters
            "speed_accuracy": 0.8,  # m/s
            "mission_efficiency": 0.85,  # 0-1 scale
            "constraint_violations": 0,
            "replanning_events": 0,
            "abort_events": 0
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate mission planning telemetry data."""
        self._update_mission_data()
        self._update_waypoint_data()
        self._update_mission_progress()
        self._update_mission_performance()
        
        data = {
            "mission": self.mission_data,
            "waypoints": self.waypoint_data,
            "progress": self.mission_progress,
            "constraints": self.mission_constraints,
            "performance": self.mission_performance,
            "status": {
                "mission_healthy": self._is_mission_healthy(),
                "constraint_compliance": self._get_constraint_compliance(),
                "mission_risk": self._get_mission_risk(),
                "replanning_needed": self._needs_replanning()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply mission planning fault."""
        fault_type = fault_params.get("type", "waypoint_corruption")
        
        if fault_type == "waypoint_corruption":
            # Simulate waypoint corruption
            wp_id = fault_params.get("waypoint_id", 3)
            for wp in telemetry_data.data["waypoints"]["waypoints"]:
                if wp["id"] == wp_id:
                    wp["lat"] += random.uniform(-0.01, 0.01)
                    wp["lon"] += random.uniform(-0.01, 0.01)
                    wp["alt"] += random.uniform(-50, 50)
                    break
                    
        elif fault_type == "mission_abort":
            # Simulate mission abort
            telemetry_data.data["mission"]["status"] = "failed"
            telemetry_data.data["mission"]["current_phase"] = "aborted"
            telemetry_data.data["performance"]["abort_events"] += 1
            
        elif fault_type == "constraint_violation":
            # Simulate constraint violation
            constraint_type = fault_params.get("constraint_type", "altitude")
            if constraint_type == "altitude":
                telemetry_data.data["constraints"]["max_altitude"] = 200
            elif constraint_type == "speed":
                telemetry_data.data["constraints"]["max_speed"] = 15
            elif constraint_type == "weather":
                telemetry_data.data["constraints"]["weather_limits"]["max_wind_speed"] = 5
            
            telemetry_data.data["performance"]["constraint_violations"] += 1
            
        elif fault_type == "replanning_failure":
            # Simulate replanning failure
            telemetry_data.data["performance"]["replanning_events"] += 1
            telemetry_data.data["status"]["replanning_needed"] = True
            
        elif fault_type == "progress_calculation_error":
            # Simulate progress calculation error
            telemetry_data.data["progress"]["completion_percentage"] = 0.0
            telemetry_data.data["progress"]["distance_remaining"] = 999.0
            telemetry_data.data["progress"]["time_remaining"] = 999
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_mission_data(self) -> None:
        """Update mission data."""
        # Simulate mission status changes
        if random.random() < 0.001:  # 0.1% chance
            statuses = ["active", "paused", "completed"]
            self.mission_data["status"] = random.choice(statuses)
        
        # Update current phase based on progress
        completion = self.mission_progress["completion_percentage"]
        if completion < 10:
            self.mission_data["current_phase"] = "takeoff"
        elif completion < 90:
            self.mission_data["current_phase"] = "execution"
        elif completion < 100:
            self.mission_data["current_phase"] = "return"
        else:
            self.mission_data["current_phase"] = "landing"
        
        # Update estimated duration based on progress
        elapsed = self.mission_progress["time_elapsed"]
        remaining = self.mission_progress["time_remaining"]
        self.mission_data["estimated_duration"] = elapsed + remaining
    
    def _update_waypoint_data(self) -> None:
        """Update waypoint data."""
        # Simulate waypoint completion
        current_wp = self.waypoint_data["current_waypoint"]
        if current_wp < len(self.waypoint_data["waypoints"]):
            wp = self.waypoint_data["waypoints"][current_wp - 1]
            if not wp["completed"] and random.random() < 0.01:  # 1% chance per cycle
                wp["completed"] = True
                self.waypoint_data["current_waypoint"] += 1
        
        # Update waypoint accuracy
        for wp in self.waypoint_data["waypoints"]:
            if not wp["completed"]:
                wp["lat"] += random.uniform(-0.0001, 0.0001)
                wp["lon"] += random.uniform(-0.0001, 0.0001)
                wp["alt"] += random.uniform(-1, 1)
                wp["alt"] = max(0, min(500, wp["alt"]))
    
    def _update_mission_progress(self) -> None:
        """Update mission progress."""
        # Calculate completion percentage
        completed_waypoints = sum(1 for wp in self.waypoint_data["waypoints"] if wp["completed"])
        self.mission_progress["completion_percentage"] = (
            completed_waypoints / self.waypoint_data["total_waypoints"]
        ) * 100
        
        # Update distance traveled
        self.mission_progress["distance_traveled"] += random.uniform(0.01, 0.05)
        
        # Update distance remaining
        total_distance = 20.0  # km
        self.mission_progress["distance_remaining"] = max(0, 
            total_distance - self.mission_progress["distance_traveled"])
        
        # Update time elapsed
        self.mission_progress["time_elapsed"] += 1.0 / self.telemetry_rate / 60  # minutes
        
        # Update time remaining
        self.mission_progress["time_remaining"] = max(0,
            self.mission_data["estimated_duration"] - self.mission_progress["time_elapsed"])
        
        # Update fuel consumption
        fuel_rate = 0.5  # % per minute
        self.mission_progress["fuel_consumed"] += fuel_rate / self.telemetry_rate / 60
        self.mission_progress["fuel_remaining"] = max(0, 100 - self.mission_progress["fuel_consumed"])
        
        # Update battery consumption
        battery_rate = 0.3  # % per minute
        self.mission_progress["battery_consumed"] += battery_rate / self.telemetry_rate / 60
        self.mission_progress["battery_remaining"] = max(0, 100 - self.mission_progress["battery_consumed"])
    
    def _update_mission_performance(self) -> None:
        """Update mission performance metrics."""
        # Update waypoint accuracy
        self.mission_performance["waypoint_accuracy"] += random.uniform(-0.1, 0.1)
        self.mission_performance["waypoint_accuracy"] = max(0.5, min(10, 
            self.mission_performance["waypoint_accuracy"]))
        
        # Update altitude accuracy
        self.mission_performance["altitude_accuracy"] += random.uniform(-0.05, 0.05)
        self.mission_performance["altitude_accuracy"] = max(0.1, min(5, 
            self.mission_performance["altitude_accuracy"]))
        
        # Update speed accuracy
        self.mission_performance["speed_accuracy"] += random.uniform(-0.05, 0.05)
        self.mission_performance["speed_accuracy"] = max(0.1, min(3, 
            self.mission_performance["speed_accuracy"]))
        
        # Update mission efficiency
        self.mission_performance["mission_efficiency"] += random.uniform(-0.01, 0.01)
        self.mission_performance["mission_efficiency"] = max(0.5, min(1.0, 
            self.mission_performance["mission_efficiency"]))
        
        # Simulate occasional constraint violations
        if random.random() < 0.001:  # 0.1% chance
            self.mission_performance["constraint_violations"] += 1
        
        # Simulate occasional replanning events
        if random.random() < 0.0005:  # 0.05% chance
            self.mission_performance["replanning_events"] += 1
    
    def _is_mission_healthy(self) -> bool:
        """Check if mission planning is healthy."""
        return (
            self.mission_data["status"] in ["active", "paused"] and
            self.mission_performance["constraint_violations"] < 5 and
            self.mission_performance["abort_events"] == 0 and
            self.mission_progress["fuel_remaining"] > 20 and
            self.mission_progress["battery_remaining"] > 20
        )
    
    def _get_constraint_compliance(self) -> str:
        """Get constraint compliance status."""
        violations = self.mission_performance["constraint_violations"]
        if violations == 0:
            return "compliant"
        elif violations < 3:
            return "minor_violations"
        else:
            return "major_violations"
    
    def _get_mission_risk(self) -> str:
        """Get mission risk level."""
        risk_factors = [
            self.mission_progress["fuel_remaining"] < 30,
            self.mission_progress["battery_remaining"] < 30,
            self.mission_performance["constraint_violations"] > 2,
            self.mission_performance["replanning_events"] > 1
        ]
        
        risk_score = sum(risk_factors)
        if risk_score >= 3:
            return "high"
        elif risk_score >= 2:
            return "medium"
        elif risk_score >= 1:
            return "low"
        else:
            return "minimal"
    
    def _needs_replanning(self) -> bool:
        """Check if mission needs replanning."""
        return (
            self.mission_performance["constraint_violations"] > 2 or
            self.mission_performance["replanning_events"] > 0 or
            self.mission_progress["fuel_remaining"] < 25 or
            self.mission_progress["battery_remaining"] < 25
        )
