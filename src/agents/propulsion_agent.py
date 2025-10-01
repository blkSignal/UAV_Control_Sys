"""Propulsion subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class PropulsionAgent(BaseAgent):
    """Agent for UAV propulsion subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 20.0):
        super().__init__(uav_id, "Propulsion", telemetry_rate)
        
        # Motor data (assuming quadcopter with 4 motors)
        self.motors = {
            "motor_1": {"rpm": 3000, "thrust": 25.0, "temperature": 45.0, "voltage": 12.0, "current": 8.5},
            "motor_2": {"rpm": 3000, "thrust": 25.0, "temperature": 45.0, "voltage": 12.0, "current": 8.5},
            "motor_3": {"rpm": 3000, "thrust": 25.0, "temperature": 45.0, "voltage": 12.0, "current": 8.5},
            "motor_4": {"rpm": 3000, "thrust": 25.0, "temperature": 45.0, "voltage": 12.0, "current": 8.5}
        }
        
        # ESC (Electronic Speed Controller) data
        self.esc_data = {
            "esc_1": {"temperature": 40.0, "voltage": 12.0, "current": 8.5, "status": "normal"},
            "esc_2": {"temperature": 40.0, "voltage": 12.0, "current": 8.5, "status": "normal"},
            "esc_3": {"temperature": 40.0, "voltage": 12.0, "current": 8.5, "status": "normal"},
            "esc_4": {"temperature": 40.0, "voltage": 12.0, "current": 8.5, "status": "normal"}
        }
        
        # Propeller data
        self.propellers = {
            "prop_1": {"efficiency": 0.85, "damage_level": 0.0, "balance": 1.0},
            "prop_2": {"efficiency": 0.85, "damage_level": 0.0, "balance": 1.0},
            "prop_3": {"efficiency": 0.85, "damage_level": 0.0, "balance": 1.0},
            "prop_4": {"efficiency": 0.85, "damage_level": 0.0, "balance": 1.0}
        }
        
        # Overall propulsion metrics
        self.total_thrust = 100.0  # Newtons
        self.power_consumption = 400.0  # Watts
        self.efficiency = 0.75
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate propulsion telemetry data."""
        self._update_motor_data()
        self._update_esc_data()
        self._update_propeller_data()
        self._update_overall_metrics()
        
        data = {
            "motors": self.motors,
            "esc": self.esc_data,
            "propellers": self.propellers,
            "overall": {
                "total_thrust": self.total_thrust,
                "power_consumption": self.power_consumption,
                "efficiency": self.efficiency,
                "thrust_to_weight_ratio": self.total_thrust / 10.0  # Assuming 10kg UAV
            },
            "status": {
                "all_motors_operational": all(m["temperature"] < 80 for m in self.motors.values()),
                "all_esc_operational": all(esc["status"] == "normal" for esc in self.esc_data.values()),
                "propeller_balance_ok": all(p["balance"] > 0.8 for p in self.propellers.values())
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply propulsion fault."""
        fault_type = fault_params.get("type", "motor_failure")
        
        if fault_type == "motor_failure":
            motor_id = fault_params.get("motor_id", "motor_1")
            if motor_id in telemetry_data.data["motors"]:
                telemetry_data.data["motors"][motor_id]["rpm"] = 0
                telemetry_data.data["motors"][motor_id]["thrust"] = 0
                telemetry_data.data["motors"][motor_id]["temperature"] = 25.0
                telemetry_data.data["motors"][motor_id]["current"] = 0
                
        elif fault_type == "esc_failure":
            esc_id = fault_params.get("esc_id", "esc_1")
            if esc_id in telemetry_data.data["esc"]:
                telemetry_data.data["esc"][esc_id]["status"] = "failed"
                telemetry_data.data["esc"][esc_id]["current"] = 0
                telemetry_data.data["esc"][esc_id]["temperature"] = 25.0
                
        elif fault_type == "propeller_damage":
            prop_id = fault_params.get("prop_id", "prop_1")
            damage_level = fault_params.get("damage_level", 0.5)
            if prop_id in telemetry_data.data["propellers"]:
                telemetry_data.data["propellers"][prop_id]["damage_level"] = damage_level
                telemetry_data.data["propellers"][prop_id]["efficiency"] *= (1 - damage_level)
                telemetry_data.data["propellers"][prop_id]["balance"] *= (1 - damage_level)
                
        elif fault_type == "thrust_reduction":
            reduction_factor = fault_params.get("reduction_factor", 0.3)
            for motor in telemetry_data.data["motors"].values():
                motor["thrust"] *= (1 - reduction_factor)
                motor["rpm"] *= (1 - reduction_factor)
        
        # Update overall metrics
        telemetry_data.data["overall"]["total_thrust"] = sum(
            m["thrust"] for m in telemetry_data.data["motors"].values()
        )
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_motor_data(self) -> None:
        """Update motor telemetry data."""
        for motor_id, motor in self.motors.items():
            # Simulate normal operation variations
            motor["rpm"] += random.uniform(-50, 50)
            motor["rpm"] = max(0, min(6000, motor["rpm"]))
            
            motor["thrust"] += random.uniform(-1, 1)
            motor["thrust"] = max(0, min(50, motor["thrust"]))
            
            motor["temperature"] += random.uniform(-2, 2)
            motor["temperature"] = max(20, min(100, motor["temperature"]))
            
            motor["voltage"] += random.uniform(-0.1, 0.1)
            motor["voltage"] = max(10, min(14, motor["voltage"]))
            
            motor["current"] += random.uniform(-0.2, 0.2)
            motor["current"] = max(0, min(15, motor["current"]))
    
    def _update_esc_data(self) -> None:
        """Update ESC telemetry data."""
        for esc_id, esc in self.esc_data.items():
            esc["temperature"] += random.uniform(-1, 1)
            esc["temperature"] = max(20, min(80, esc["temperature"]))
            
            esc["voltage"] += random.uniform(-0.1, 0.1)
            esc["voltage"] = max(10, min(14, esc["voltage"]))
            
            esc["current"] += random.uniform(-0.2, 0.2)
            esc["current"] = max(0, min(15, esc["current"]))
            
            # Simulate occasional ESC status changes
            if random.random() < 0.001:  # 0.1% chance
                esc["status"] = random.choice(["normal", "warning", "error"])
    
    def _update_propeller_data(self) -> None:
        """Update propeller telemetry data."""
        for prop_id, prop in self.propellers.items():
            prop["efficiency"] += random.uniform(-0.01, 0.01)
            prop["efficiency"] = max(0.5, min(1.0, prop["efficiency"]))
            
            prop["damage_level"] += random.uniform(-0.001, 0.001)
            prop["damage_level"] = max(0, min(1.0, prop["damage_level"]))
            
            prop["balance"] += random.uniform(-0.01, 0.01)
            prop["balance"] = max(0.5, min(1.0, prop["balance"]))
    
    def _update_overall_metrics(self) -> None:
        """Update overall propulsion metrics."""
        self.total_thrust = sum(motor["thrust"] for motor in self.motors.values())
        self.power_consumption = sum(
            motor["voltage"] * motor["current"] for motor in self.motors.values()
        )
        
        # Calculate efficiency based on thrust vs power
        if self.power_consumption > 0:
            self.efficiency = min(1.0, self.total_thrust / (self.power_consumption / 10))
        else:
            self.efficiency = 0.0
