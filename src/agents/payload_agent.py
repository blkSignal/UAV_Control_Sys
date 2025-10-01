"""Payload subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class PayloadAgent(BaseAgent):
    """Agent for UAV payload subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 8.0):
        super().__init__(uav_id, "Payload", telemetry_rate)
        
        # Camera payload
        self.camera_data = {
            "gimbal_pitch": 0.0,  # degrees
            "gimbal_roll": 0.0,  # degrees
            "gimbal_yaw": 0.0,  # degrees
            "zoom_level": 1.0,
            "focus_distance": 10.0,  # meters
            "aperture": 2.8,
            "shutter_speed": 1.0/60.0,  # seconds
            "iso": 100,
            "recording": False,
            "storage_used": 25.0,  # GB
            "storage_total": 128.0,  # GB
            "temperature": 35.0  # °C
        }
        
        # Sensor payload
        self.sensor_data = {
            "lidar_active": True,
            "lidar_range": 100.0,  # meters
            "lidar_points_per_second": 100000,
            "thermal_active": True,
            "thermal_temperature_range": [-20, 100],  # °C
            "multispectral_active": False,
            "spectral_bands": 4,
            "data_collection_rate": 1.0  # Hz
        }
        
        # Delivery mechanism
        self.delivery_data = {
            "cargo_weight": 0.0,  # kg
            "cargo_volume": 0.0,  # liters
            "release_mechanism": "ready",
            "delivery_accuracy": 1.0,  # meters
            "payload_bay_status": "closed"
        }
        
        # Data transmission
        self.data_transmission = {
            "data_rate": 5.0,  # Mbps
            "compression_ratio": 0.3,
            "encryption_enabled": True,
            "transmission_queue": 150,  # MB
            "failed_transmissions": 0
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate payload telemetry data."""
        self._update_camera_data()
        self._update_sensor_data()
        self._update_delivery_data()
        self._update_data_transmission()
        
        data = {
            "camera": self.camera_data,
            "sensors": self.sensor_data,
            "delivery": self.delivery_data,
            "data_transmission": self.data_transmission,
            "status": {
                "payload_operational": self._is_payload_operational(),
                "data_integrity": self._get_data_integrity(),
                "storage_available": self._get_storage_available(),
                "mission_readiness": self._get_mission_readiness()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply payload fault."""
        fault_type = fault_params.get("type", "camera_failure")
        
        if fault_type == "camera_failure":
            # Simulate camera failure
            telemetry_data.data["camera"]["recording"] = False
            telemetry_data.data["camera"]["temperature"] = 80.0
            telemetry_data.data["camera"]["focus_distance"] = 0.0
            
        elif fault_type == "gimbal_failure":
            # Simulate gimbal failure
            telemetry_data.data["camera"]["gimbal_pitch"] = 0.0
            telemetry_data.data["camera"]["gimbal_roll"] = 0.0
            telemetry_data.data["camera"]["gimbal_yaw"] = 0.0
            
        elif fault_type == "sensor_failure":
            # Simulate sensor failure
            sensor_type = fault_params.get("sensor_type", "lidar")
            if sensor_type == "lidar":
                telemetry_data.data["sensors"]["lidar_active"] = False
                telemetry_data.data["sensors"]["lidar_range"] = 0.0
            elif sensor_type == "thermal":
                telemetry_data.data["sensors"]["thermal_active"] = False
                
        elif fault_type == "storage_failure":
            # Simulate storage failure
            telemetry_data.data["camera"]["storage_used"] = 0.0
            telemetry_data.data["camera"]["storage_total"] = 0.0
            
        elif fault_type == "delivery_failure":
            # Simulate delivery mechanism failure
            telemetry_data.data["delivery"]["release_mechanism"] = "failed"
            telemetry_data.data["delivery"]["payload_bay_status"] = "stuck"
            
        elif fault_type == "data_corruption":
            # Simulate data corruption
            telemetry_data.data["data_transmission"]["failed_transmissions"] += 10
            telemetry_data.data["data_transmission"]["compression_ratio"] = 1.0
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_camera_data(self) -> None:
        """Update camera telemetry data."""
        # Simulate gimbal movement
        self.camera_data["gimbal_pitch"] += random.uniform(-1, 1)
        self.camera_data["gimbal_pitch"] = max(-90, min(90, self.camera_data["gimbal_pitch"]))
        
        self.camera_data["gimbal_roll"] += random.uniform(-0.5, 0.5)
        self.camera_data["gimbal_roll"] = max(-45, min(45, self.camera_data["gimbal_roll"]))
        
        self.camera_data["gimbal_yaw"] += random.uniform(-2, 2)
        self.camera_data["gimbal_yaw"] = self.camera_data["gimbal_yaw"] % 360
        
        # Simulate camera settings changes
        self.camera_data["focus_distance"] += random.uniform(-0.5, 0.5)
        self.camera_data["focus_distance"] = max(1, min(100, self.camera_data["focus_distance"]))
        
        # Simulate storage usage increase when recording
        if self.camera_data["recording"]:
            self.camera_data["storage_used"] += random.uniform(0.01, 0.05)
            self.camera_data["storage_used"] = min(
                self.camera_data["storage_total"], 
                self.camera_data["storage_used"]
            )
        
        # Simulate temperature changes
        self.camera_data["temperature"] += random.uniform(-1, 1)
        self.camera_data["temperature"] = max(20, min(60, self.camera_data["temperature"]))
        
        # Simulate occasional recording start/stop
        if random.random() < 0.01:  # 1% chance
            self.camera_data["recording"] = not self.camera_data["recording"]
    
    def _update_sensor_data(self) -> None:
        """Update sensor telemetry data."""
        # Simulate LiDAR variations
        if self.sensor_data["lidar_active"]:
            self.sensor_data["lidar_range"] += random.uniform(-2, 2)
            self.sensor_data["lidar_range"] = max(10, min(200, self.sensor_data["lidar_range"]))
            
            self.sensor_data["lidar_points_per_second"] += random.randint(-1000, 1000)
            self.sensor_data["lidar_points_per_second"] = max(50000, min(200000, 
                self.sensor_data["lidar_points_per_second"]))
        
        # Simulate thermal sensor variations
        if self.sensor_data["thermal_active"]:
            temp_min, temp_max = self.sensor_data["thermal_temperature_range"]
            self.sensor_data["thermal_temperature_range"] = [
                temp_min + random.uniform(-2, 2),
                temp_max + random.uniform(-2, 2)
            ]
        
        # Simulate data collection rate changes
        self.sensor_data["data_collection_rate"] += random.uniform(-0.1, 0.1)
        self.sensor_data["data_collection_rate"] = max(0.1, min(10, 
            self.sensor_data["data_collection_rate"]))
    
    def _update_delivery_data(self) -> None:
        """Update delivery mechanism data."""
        # Simulate cargo weight changes
        self.delivery_data["cargo_weight"] += random.uniform(-0.1, 0.1)
        self.delivery_data["cargo_weight"] = max(0, min(5, self.delivery_data["cargo_weight"]))
        
        # Simulate cargo volume changes
        self.delivery_data["cargo_volume"] += random.uniform(-0.05, 0.05)
        self.delivery_data["cargo_volume"] = max(0, min(10, self.delivery_data["cargo_volume"]))
        
        # Simulate delivery accuracy variations
        self.delivery_data["delivery_accuracy"] += random.uniform(-0.1, 0.1)
        self.delivery_data["delivery_accuracy"] = max(0.1, min(5, 
            self.delivery_data["delivery_accuracy"]))
        
        # Simulate payload bay status changes
        if random.random() < 0.005:  # 0.5% chance
            self.delivery_data["payload_bay_status"] = random.choice(["closed", "open", "stuck"])
    
    def _update_data_transmission(self) -> None:
        """Update data transmission data."""
        # Simulate data rate variations
        self.data_transmission["data_rate"] += random.uniform(-0.5, 0.5)
        self.data_transmission["data_rate"] = max(1, min(20, 
            self.data_transmission["data_rate"]))
        
        # Simulate compression ratio changes
        self.data_transmission["compression_ratio"] += random.uniform(-0.05, 0.05)
        self.data_transmission["compression_ratio"] = max(0.1, min(0.8, 
            self.data_transmission["compression_ratio"]))
        
        # Simulate transmission queue changes
        self.data_transmission["transmission_queue"] += random.uniform(-5, 5)
        self.data_transmission["transmission_queue"] = max(0, min(1000, 
            self.data_transmission["transmission_queue"]))
        
        # Simulate occasional transmission failures
        if random.random() < 0.001:  # 0.1% chance
            self.data_transmission["failed_transmissions"] += 1
    
    def _is_payload_operational(self) -> bool:
        """Check if payload is operational."""
        return (
            self.camera_data["temperature"] < 50 and
            self.camera_data["storage_used"] < self.camera_data["storage_total"] and
            self.delivery_data["release_mechanism"] == "ready" and
            self.data_transmission["failed_transmissions"] < 5
        )
    
    def _get_data_integrity(self) -> float:
        """Calculate data integrity score."""
        failed_transmissions = self.data_transmission["failed_transmissions"]
        total_transmissions = max(1, failed_transmissions + 100)  # Assume 100 successful
        return max(0, 1 - (failed_transmissions / total_transmissions))
    
    def _get_storage_available(self) -> float:
        """Calculate available storage percentage."""
        if self.camera_data["storage_total"] > 0:
            return (self.camera_data["storage_total"] - self.camera_data["storage_used"]) / self.camera_data["storage_total"]
        return 0.0
    
    def _get_mission_readiness(self) -> str:
        """Get mission readiness status."""
        if not self._is_payload_operational():
            return "not_ready"
        elif self._get_storage_available() < 0.1:
            return "limited"
        else:
            return "ready"
