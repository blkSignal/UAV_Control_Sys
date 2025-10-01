"""Power subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class PowerAgent(BaseAgent):
    """Agent for UAV power subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 15.0):
        super().__init__(uav_id, "Power", telemetry_rate)
        
        # Battery data
        self.battery_data = {
            "voltage": 12.6,  # V
            "current": 8.5,  # A
            "capacity": 5000,  # mAh
            "remaining_capacity": 4500,  # mAh
            "temperature": 25.0,  # °C
            "charge_cycles": 45,
            "health": 95.0,  # %
            "state_of_charge": 90.0,  # %
            "time_to_empty": 45.0,  # minutes
            "time_to_full": 0.0  # minutes
        }
        
        # Power distribution
        self.power_distribution = {
            "total_power": 100.0,  # W
            "propulsion": 60.0,  # W
            "avionics": 15.0,  # W
            "communication": 10.0,  # W
            "payload": 10.0,  # W
            "sensors": 5.0  # W
        }
        
        # Power management
        self.power_management = {
            "charging": False,
            "discharging": True,
            "power_save_mode": False,
            "voltage_regulation": "normal",
            "current_limit": 15.0,  # A
            "overcurrent_protection": False,
            "thermal_protection": False
        }
        
        # Solar panel data (if applicable)
        self.solar_data = {
            "available": True,
            "voltage": 18.0,  # V
            "current": 2.0,  # A
            "power": 36.0,  # W
            "efficiency": 0.22,  # 22%
            "temperature": 35.0,  # °C
            "irradiance": 800.0  # W/m²
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate power telemetry data."""
        self._update_battery_data()
        self._update_power_distribution()
        self._update_power_management()
        self._update_solar_data()
        
        data = {
            "battery": self.battery_data,
            "power_distribution": self.power_distribution,
            "power_management": self.power_management,
            "solar": self.solar_data,
            "status": {
                "power_healthy": self._is_power_healthy(),
                "battery_critical": self.battery_data["state_of_charge"] < 20,
                "charging_active": self.power_management["charging"],
                "power_efficiency": self._get_power_efficiency()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply power fault."""
        fault_type = fault_params.get("type", "voltage_drop")
        
        if fault_type == "voltage_drop":
            # Simulate voltage drop
            drop_factor = fault_params.get("drop_factor", 0.3)
            telemetry_data.data["battery"]["voltage"] *= (1 - drop_factor)
            telemetry_data.data["battery"]["state_of_charge"] *= (1 - drop_factor)
            
        elif fault_type == "battery_failure":
            # Simulate battery failure
            telemetry_data.data["battery"]["voltage"] = 0.0
            telemetry_data.data["battery"]["current"] = 0.0
            telemetry_data.data["battery"]["state_of_charge"] = 0.0
            telemetry_data.data["power_management"]["discharging"] = False
            
        elif fault_type == "overcurrent":
            # Simulate overcurrent condition
            telemetry_data.data["battery"]["current"] *= 2.0
            telemetry_data.data["power_management"]["overcurrent_protection"] = True
            
        elif fault_type == "thermal_runaway":
            # Simulate thermal runaway
            telemetry_data.data["battery"]["temperature"] = 80.0
            telemetry_data.data["power_management"]["thermal_protection"] = True
            
        elif fault_type == "power_distribution_failure":
            # Simulate power distribution failure
            subsystem = fault_params.get("subsystem", "propulsion")
            if subsystem in telemetry_data.data["power_distribution"]:
                telemetry_data.data["power_distribution"][subsystem] = 0.0
                
        elif fault_type == "solar_failure":
            # Simulate solar panel failure
            telemetry_data.data["solar"]["available"] = False
            telemetry_data.data["solar"]["power"] = 0.0
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_battery_data(self) -> None:
        """Update battery telemetry data."""
        # Simulate battery discharge
        discharge_rate = self.power_distribution["total_power"] / self.battery_data["voltage"]
        self.battery_data["current"] = discharge_rate + random.uniform(-0.5, 0.5)
        self.battery_data["current"] = max(0, min(20, self.battery_data["current"]))
        
        # Update voltage based on current and SOC
        soc_factor = self.battery_data["state_of_charge"] / 100.0
        self.battery_data["voltage"] = 10.5 + (soc_factor * 2.1) + random.uniform(-0.1, 0.1)
        self.battery_data["voltage"] = max(10.0, min(12.8, self.battery_data["voltage"]))
        
        # Update remaining capacity
        capacity_loss = (self.battery_data["current"] / 1000) * (1.0 / self.telemetry_rate)  # Ah per cycle
        self.battery_data["remaining_capacity"] -= capacity_loss * 1000  # Convert to mAh
        self.battery_data["remaining_capacity"] = max(0, min(
            self.battery_data["capacity"], 
            self.battery_data["remaining_capacity"]
        ))
        
        # Update state of charge
        self.battery_data["state_of_charge"] = (
            self.battery_data["remaining_capacity"] / self.battery_data["capacity"]
        ) * 100
        
        # Update temperature
        self.battery_data["temperature"] += random.uniform(-0.5, 0.5)
        self.battery_data["temperature"] = max(15, min(60, self.battery_data["temperature"]))
        
        # Update time to empty
        if self.battery_data["current"] > 0:
            self.battery_data["time_to_empty"] = (
                self.battery_data["remaining_capacity"] / 1000
            ) / (self.battery_data["current"] / 1000) * 60  # minutes
        else:
            self.battery_data["time_to_empty"] = float('inf')
    
    def _update_power_distribution(self) -> None:
        """Update power distribution data."""
        # Simulate power consumption variations
        self.power_distribution["propulsion"] += random.uniform(-2, 2)
        self.power_distribution["propulsion"] = max(0, min(80, self.power_distribution["propulsion"]))
        
        self.power_distribution["avionics"] += random.uniform(-0.5, 0.5)
        self.power_distribution["avionics"] = max(5, min(25, self.power_distribution["avionics"]))
        
        self.power_distribution["communication"] += random.uniform(-0.5, 0.5)
        self.power_distribution["communication"] = max(5, min(20, self.power_distribution["communication"]))
        
        self.power_distribution["payload"] += random.uniform(-1, 1)
        self.power_distribution["payload"] = max(0, min(20, self.power_distribution["payload"]))
        
        self.power_distribution["sensors"] += random.uniform(-0.2, 0.2)
        self.power_distribution["sensors"] = max(2, min(10, self.power_distribution["sensors"]))
        
        # Update total power
        self.power_distribution["total_power"] = sum([
            self.power_distribution["propulsion"],
            self.power_distribution["avionics"],
            self.power_distribution["communication"],
            self.power_distribution["payload"],
            self.power_distribution["sensors"]
        ])
    
    def _update_power_management(self) -> None:
        """Update power management data."""
        # Update charging status based on voltage
        if self.battery_data["voltage"] > 12.4 and self.battery_data["state_of_charge"] < 95:
            self.power_management["charging"] = True
            self.power_management["discharging"] = False
        else:
            self.power_management["charging"] = False
            self.power_management["discharging"] = True
        
        # Update power save mode based on battery level
        if self.battery_data["state_of_charge"] < 30:
            self.power_management["power_save_mode"] = True
        else:
            self.power_management["power_save_mode"] = False
        
        # Update voltage regulation
        if self.battery_data["voltage"] < 11.0:
            self.power_management["voltage_regulation"] = "low"
        elif self.battery_data["voltage"] > 12.5:
            self.power_management["voltage_regulation"] = "high"
        else:
            self.power_management["voltage_regulation"] = "normal"
    
    def _update_solar_data(self) -> None:
        """Update solar panel data."""
        if not self.solar_data["available"]:
            return
        
        # Simulate solar panel variations
        self.solar_data["irradiance"] += random.uniform(-50, 50)
        self.solar_data["irradiance"] = max(0, min(1000, self.solar_data["irradiance"]))
        
        # Update power based on irradiance
        self.solar_data["power"] = (
            self.solar_data["irradiance"] * 0.05 * self.solar_data["efficiency"]
        ) + random.uniform(-2, 2)
        self.solar_data["power"] = max(0, min(50, self.solar_data["power"]))
        
        # Update voltage and current
        self.solar_data["voltage"] = 18.0 + random.uniform(-1, 1)
        self.solar_data["current"] = self.solar_data["power"] / self.solar_data["voltage"]
        
        # Update temperature
        self.solar_data["temperature"] += random.uniform(-1, 1)
        self.solar_data["temperature"] = max(20, min(60, self.solar_data["temperature"]))
    
    def _is_power_healthy(self) -> bool:
        """Check if power system is healthy."""
        return (
            self.battery_data["voltage"] > 11.0 and
            self.battery_data["state_of_charge"] > 20 and
            self.battery_data["temperature"] < 50 and
            not self.power_management["overcurrent_protection"] and
            not self.power_management["thermal_protection"]
        )
    
    def _get_power_efficiency(self) -> float:
        """Calculate power efficiency."""
        if self.power_distribution["total_power"] > 0:
            return min(1.0, self.solar_data["power"] / self.power_distribution["total_power"])
        return 0.0
