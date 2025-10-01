"""Flight control subsystem agent."""

import random
import math
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class FlightControlAgent(BaseAgent):
    """Agent for UAV flight control subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 25.0):
        super().__init__(uav_id, "Flight_Control", telemetry_rate)
        
        # Flight control surfaces
        self.control_surfaces = {
            "aileron_left": 0.0,  # degrees
            "aileron_right": 0.0,  # degrees
            "elevator": 0.0,  # degrees
            "rudder": 0.0,  # degrees
            "flaps": 0.0,  # degrees
            "spoilers": 0.0  # degrees
        }
        
        # Autopilot data
        self.autopilot_data = {
            "mode": "manual",  # manual, auto, guided, rtl
            "altitude_hold": False,
            "heading_hold": False,
            "speed_hold": False,
            "waypoint_active": 0,
            "total_waypoints": 5,
            "distance_to_target": 1000.0,  # meters
            "bearing_to_target": 45.0,  # degrees
            "cross_track_error": 5.0  # meters
        }
        
        # Flight dynamics
        self.flight_dynamics = {
            "vertical_speed": 0.0,  # m/s
            "turn_rate": 0.0,  # degrees/s
            "bank_angle": 0.0,  # degrees
            "pitch_angle": 0.0,  # degrees
            "load_factor": 1.0,  # g
            "stall_warning": False,
            "overspeed_warning": False
        }
        
        # Control system status
        self.control_status = {
            "servo_health": [100, 100, 100, 100],  # % health for each servo
            "control_authority": 100.0,  # %
            "trim_position": 0.0,  # degrees
            "control_sensitivity": 1.0,
            "stability_augmentation": True,
            "fly_by_wire_active": True
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate flight control telemetry data."""
        self._update_control_surfaces()
        self._update_autopilot_data()
        self._update_flight_dynamics()
        self._update_control_status()
        
        data = {
            "control_surfaces": self.control_surfaces,
            "autopilot": self.autopilot_data,
            "flight_dynamics": self.flight_dynamics,
            "control_status": self.control_status,
            "status": {
                "flight_control_healthy": self._is_flight_control_healthy(),
                "autopilot_status": self._get_autopilot_status(),
                "control_authority": self._get_control_authority(),
                "flight_mode": self._get_flight_mode()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply flight control fault."""
        fault_type = fault_params.get("type", "servo_failure")
        
        if fault_type == "servo_failure":
            # Simulate servo failure
            servo_id = fault_params.get("servo_id", 0)
            if servo_id < len(telemetry_data.data["control_status"]["servo_health"]):
                telemetry_data.data["control_status"]["servo_health"][servo_id] = 0
                
        elif fault_type == "control_surface_jam":
            # Simulate control surface jam
            surface = fault_params.get("surface", "aileron_left")
            if surface in telemetry_data.data["control_surfaces"]:
                telemetry_data.data["control_surfaces"][surface] = random.uniform(-10, 10)
                
        elif fault_type == "autopilot_failure":
            # Simulate autopilot failure
            telemetry_data.data["autopilot"]["mode"] = "manual"
            telemetry_data.data["autopilot"]["altitude_hold"] = False
            telemetry_data.data["autopilot"]["heading_hold"] = False
            telemetry_data.data["autopilot"]["speed_hold"] = False
            
        elif fault_type == "fly_by_wire_failure":
            # Simulate fly-by-wire failure
            telemetry_data.data["control_status"]["fly_by_wire_active"] = False
            telemetry_data.data["control_status"]["stability_augmentation"] = False
            
        elif fault_type == "control_authority_loss":
            # Simulate control authority loss
            reduction_factor = fault_params.get("reduction_factor", 0.5)
            telemetry_data.data["control_status"]["control_authority"] *= (1 - reduction_factor)
            
        elif fault_type == "trim_failure":
            # Simulate trim system failure
            telemetry_data.data["control_status"]["trim_position"] = random.uniform(-5, 5)
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_control_surfaces(self) -> None:
        """Update control surface positions."""
        # Simulate control surface movements
        self.control_surfaces["aileron_left"] += random.uniform(-2, 2)
        self.control_surfaces["aileron_left"] = max(-30, min(30, self.control_surfaces["aileron_left"]))
        
        self.control_surfaces["aileron_right"] += random.uniform(-2, 2)
        self.control_surfaces["aileron_right"] = max(-30, min(30, self.control_surfaces["aileron_right"]))
        
        self.control_surfaces["elevator"] += random.uniform(-1, 1)
        self.control_surfaces["elevator"] = max(-20, min(20, self.control_surfaces["elevator"]))
        
        self.control_surfaces["rudder"] += random.uniform(-1, 1)
        self.control_surfaces["rudder"] = max(-20, min(20, self.control_surfaces["rudder"]))
        
        # Simulate flap and spoiler changes
        if random.random() < 0.01:  # 1% chance
            self.control_surfaces["flaps"] = random.uniform(0, 30)
        
        if random.random() < 0.005:  # 0.5% chance
            self.control_surfaces["spoilers"] = random.uniform(0, 20)
    
    def _update_autopilot_data(self) -> None:
        """Update autopilot data."""
        # Simulate autopilot mode changes
        if random.random() < 0.005:  # 0.5% chance
            modes = ["manual", "auto", "guided", "rtl"]
            self.autopilot_data["mode"] = random.choice(modes)
        
        # Update waypoint data
        self.autopilot_data["distance_to_target"] += random.uniform(-10, 10)
        self.autopilot_data["distance_to_target"] = max(0, min(10000, 
            self.autopilot_data["distance_to_target"]))
        
        self.autopilot_data["bearing_to_target"] += random.uniform(-2, 2)
        self.autopilot_data["bearing_to_target"] = self.autopilot_data["bearing_to_target"] % 360
        
        self.autopilot_data["cross_track_error"] += random.uniform(-1, 1)
        self.autopilot_data["cross_track_error"] = max(-50, min(50, 
            self.autopilot_data["cross_track_error"]))
        
        # Update hold modes based on autopilot mode
        if self.autopilot_data["mode"] in ["auto", "guided"]:
            self.autopilot_data["altitude_hold"] = random.random() < 0.8
            self.autopilot_data["heading_hold"] = random.random() < 0.8
            self.autopilot_data["speed_hold"] = random.random() < 0.8
        else:
            self.autopilot_data["altitude_hold"] = False
            self.autopilot_data["heading_hold"] = False
            self.autopilot_data["speed_hold"] = False
    
    def _update_flight_dynamics(self) -> None:
        """Update flight dynamics data."""
        # Simulate vertical speed changes
        self.flight_dynamics["vertical_speed"] += random.uniform(-1, 1)
        self.flight_dynamics["vertical_speed"] = max(-20, min(20, 
            self.flight_dynamics["vertical_speed"]))
        
        # Simulate turn rate changes
        self.flight_dynamics["turn_rate"] += random.uniform(-2, 2)
        self.flight_dynamics["turn_rate"] = max(-30, min(30, self.flight_dynamics["turn_rate"]))
        
        # Simulate bank angle changes
        self.flight_dynamics["bank_angle"] += random.uniform(-1, 1)
        self.flight_dynamics["bank_angle"] = max(-60, min(60, self.flight_dynamics["bank_angle"]))
        
        # Simulate pitch angle changes
        self.flight_dynamics["pitch_angle"] += random.uniform(-0.5, 0.5)
        self.flight_dynamics["pitch_angle"] = max(-30, min(30, self.flight_dynamics["pitch_angle"]))
        
        # Simulate load factor changes
        self.flight_dynamics["load_factor"] += random.uniform(-0.1, 0.1)
        self.flight_dynamics["load_factor"] = max(0.5, min(3.0, self.flight_dynamics["load_factor"]))
        
        # Update warnings based on flight dynamics
        self.flight_dynamics["stall_warning"] = (
            self.flight_dynamics["pitch_angle"] > 20 or 
            self.flight_dynamics["load_factor"] < 0.8
        )
        
        self.flight_dynamics["overspeed_warning"] = (
            self.flight_dynamics["load_factor"] > 2.5 or 
            abs(self.flight_dynamics["turn_rate"]) > 25
        )
    
    def _update_control_status(self) -> None:
        """Update control system status."""
        # Simulate servo health changes
        for i in range(len(self.control_status["servo_health"])):
            self.control_status["servo_health"][i] += random.uniform(-0.5, 0.5)
            self.control_status["servo_health"][i] = max(0, min(100, 
                self.control_status["servo_health"][i]))
        
        # Simulate control authority changes
        self.control_status["control_authority"] += random.uniform(-1, 1)
        self.control_status["control_authority"] = max(0, min(100, 
            self.control_status["control_authority"]))
        
        # Simulate trim position changes
        self.control_status["trim_position"] += random.uniform(-0.1, 0.1)
        self.control_status["trim_position"] = max(-5, min(5, 
            self.control_status["trim_position"]))
        
        # Simulate control sensitivity changes
        self.control_status["control_sensitivity"] += random.uniform(-0.05, 0.05)
        self.control_status["control_sensitivity"] = max(0.5, min(2.0, 
            self.control_status["control_sensitivity"]))
        
        # Simulate occasional system status changes
        if random.random() < 0.001:  # 0.1% chance
            self.control_status["stability_augmentation"] = not self.control_status["stability_augmentation"]
        
        if random.random() < 0.001:  # 0.1% chance
            self.control_status["fly_by_wire_active"] = not self.control_status["fly_by_wire_active"]
    
    def _is_flight_control_healthy(self) -> bool:
        """Check if flight control system is healthy."""
        return (
            all(health > 80 for health in self.control_status["servo_health"]) and
            self.control_status["control_authority"] > 90 and
            not self.flight_dynamics["stall_warning"] and
            not self.flight_dynamics["overspeed_warning"]
        )
    
    def _get_autopilot_status(self) -> str:
        """Get autopilot status."""
        if self.autopilot_data["mode"] == "manual":
            return "manual"
        elif self.autopilot_data["mode"] in ["auto", "guided"]:
            return "active"
        elif self.autopilot_data["mode"] == "rtl":
            return "return_to_launch"
        else:
            return "unknown"
    
    def _get_control_authority(self) -> str:
        """Get control authority level."""
        authority = self.control_status["control_authority"]
        if authority > 95:
            return "full"
        elif authority > 80:
            return "reduced"
        elif authority > 50:
            return "limited"
        else:
            return "critical"
    
    def _get_flight_mode(self) -> str:
        """Get current flight mode."""
        mode = self.autopilot_data["mode"]
        if mode == "manual":
            return "manual_control"
        elif mode == "auto":
            return "autonomous_flight"
        elif mode == "guided":
            return "guided_flight"
        elif mode == "rtl":
            return "return_to_launch"
        else:
            return "unknown"
