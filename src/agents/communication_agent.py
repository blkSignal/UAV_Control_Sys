"""Communication subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class CommunicationAgent(BaseAgent):
    """Agent for UAV communication subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 5.0):
        super().__init__(uav_id, "Communication", telemetry_rate)
        
        # Radio communication data
        self.radio_data = {
            "frequency": 2.4,  # GHz
            "power": 20.0,  # dBm
            "rssi": -45.0,  # dBm
            "snr": 25.0,  # dB
            "bandwidth": 20.0,  # MHz
            "modulation": "QPSK",
            "data_rate": 54.0,  # Mbps
            "packet_loss": 0.001,
            "latency": 15.0  # ms
        }
        
        # Satellite communication
        self.satellite_data = {
            "connected": True,
            "signal_strength": 75.0,  # %
            "satellite_id": "SAT-001",
            "elevation": 45.0,  # degrees
            "azimuth": 180.0,  # degrees
            "data_rate": 1.0,  # Mbps
            "latency": 250.0  # ms
        }
        
        # Ground station communication
        self.ground_station_data = {
            "connected": True,
            "distance": 5.0,  # km
            "rssi": -50.0,  # dBm
            "data_rate": 10.0,  # Mbps
            "latency": 5.0,  # ms
            "encryption": "AES-256",
            "authentication": "valid"
        }
        
        # Network status
        self.network_status = {
            "primary_link": "ground_station",
            "backup_link": "satellite",
            "failover_active": False,
            "total_bandwidth": 10.0,  # Mbps
            "used_bandwidth": 3.5,  # Mbps
            "packets_sent": 1250,
            "packets_received": 1180,
            "errors": 2
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate communication telemetry data."""
        self._update_radio_data()
        self._update_satellite_data()
        self._update_ground_station_data()
        self._update_network_status()
        
        data = {
            "radio": self.radio_data,
            "satellite": self.satellite_data,
            "ground_station": self.ground_station_data,
            "network": self.network_status,
            "status": {
                "communication_healthy": self._is_communication_healthy(),
                "signal_quality": self._get_signal_quality(),
                "data_integrity": self._get_data_integrity()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply communication fault."""
        fault_type = fault_params.get("type", "signal_loss")
        
        if fault_type == "signal_loss":
            # Simulate signal loss
            telemetry_data.data["radio"]["rssi"] = -100.0
            telemetry_data.data["radio"]["snr"] = 0.0
            telemetry_data.data["ground_station"]["connected"] = False
            telemetry_data.data["network"]["failover_active"] = True
            
        elif fault_type == "satellite_loss":
            # Simulate satellite communication loss
            telemetry_data.data["satellite"]["connected"] = False
            telemetry_data.data["satellite"]["signal_strength"] = 0.0
            
        elif fault_type == "interference":
            # Simulate radio interference
            interference_level = fault_params.get("interference_level", 0.5)
            telemetry_data.data["radio"]["snr"] *= (1 - interference_level)
            telemetry_data.data["radio"]["packet_loss"] *= (1 + interference_level * 10)
            
        elif fault_type == "encryption_failure":
            # Simulate encryption failure
            telemetry_data.data["ground_station"]["encryption"] = "failed"
            telemetry_data.data["ground_station"]["authentication"] = "invalid"
            
        elif fault_type == "bandwidth_reduction":
            # Simulate bandwidth reduction
            reduction_factor = fault_params.get("reduction_factor", 0.5)
            telemetry_data.data["radio"]["data_rate"] *= (1 - reduction_factor)
            telemetry_data.data["network"]["total_bandwidth"] *= (1 - reduction_factor)
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_radio_data(self) -> None:
        """Update radio communication data."""
        self.radio_data["rssi"] += random.uniform(-2, 2)
        self.radio_data["rssi"] = max(-100, min(-20, self.radio_data["rssi"]))
        
        self.radio_data["snr"] += random.uniform(-1, 1)
        self.radio_data["snr"] = max(0, min(40, self.radio_data["snr"]))
        
        self.radio_data["packet_loss"] += random.uniform(-0.0001, 0.0001)
        self.radio_data["packet_loss"] = max(0, min(0.1, self.radio_data["packet_loss"]))
        
        self.radio_data["latency"] += random.uniform(-1, 1)
        self.radio_data["latency"] = max(1, min(100, self.radio_data["latency"]))
        
        # Simulate occasional frequency changes
        if random.random() < 0.01:  # 1% chance
            self.radio_data["frequency"] += random.uniform(-0.1, 0.1)
            self.radio_data["frequency"] = max(2.0, min(6.0, self.radio_data["frequency"]))
    
    def _update_satellite_data(self) -> None:
        """Update satellite communication data."""
        self.satellite_data["signal_strength"] += random.uniform(-2, 2)
        self.satellite_data["signal_strength"] = max(0, min(100, self.satellite_data["signal_strength"]))
        
        self.satellite_data["elevation"] += random.uniform(-1, 1)
        self.satellite_data["elevation"] = max(0, min(90, self.satellite_data["elevation"]))
        
        self.satellite_data["azimuth"] += random.uniform(-2, 2)
        self.satellite_data["azimuth"] = self.satellite_data["azimuth"] % 360
        
        self.satellite_data["latency"] += random.uniform(-5, 5)
        self.satellite_data["latency"] = max(200, min(300, self.satellite_data["latency"]))
    
    def _update_ground_station_data(self) -> None:
        """Update ground station communication data."""
        self.ground_station_data["distance"] += random.uniform(-0.1, 0.1)
        self.ground_station_data["distance"] = max(0.1, min(50, self.ground_station_data["distance"]))
        
        self.ground_station_data["rssi"] += random.uniform(-2, 2)
        self.ground_station_data["rssi"] = max(-100, min(-20, self.ground_station_data["rssi"]))
        
        self.ground_station_data["latency"] += random.uniform(-0.5, 0.5)
        self.ground_station_data["latency"] = max(1, min(50, self.ground_station_data["latency"]))
    
    def _update_network_status(self) -> None:
        """Update network status."""
        self.network_status["used_bandwidth"] += random.uniform(-0.1, 0.1)
        self.network_status["used_bandwidth"] = max(0, min(
            self.network_status["total_bandwidth"], 
            self.network_status["used_bandwidth"]
        ))
        
        self.network_status["packets_sent"] += random.randint(0, 5)
        self.network_status["packets_received"] += random.randint(0, 5)
        
        # Simulate occasional errors
        if random.random() < 0.001:  # 0.1% chance
            self.network_status["errors"] += 1
    
    def _is_communication_healthy(self) -> bool:
        """Check if communication is healthy."""
        return (
            self.radio_data["rssi"] > -80 and
            self.radio_data["snr"] > 10 and
            self.ground_station_data["connected"] and
            self.network_status["errors"] < 10
        )
    
    def _get_signal_quality(self) -> str:
        """Get signal quality rating."""
        if self.radio_data["snr"] > 25:
            return "excellent"
        elif self.radio_data["snr"] > 15:
            return "good"
        elif self.radio_data["snr"] > 5:
            return "fair"
        else:
            return "poor"
    
    def _get_data_integrity(self) -> float:
        """Calculate data integrity score."""
        packet_loss = self.radio_data["packet_loss"]
        error_rate = self.network_status["errors"] / max(1, self.network_status["packets_sent"])
        return max(0, 1 - packet_loss - error_rate)
