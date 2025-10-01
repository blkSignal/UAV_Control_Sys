"""Navigation subsystem agent."""

import random
import math
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class NavigationAgent(BaseAgent):
    """Agent for UAV navigation subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 10.0):
        super().__init__(uav_id, "Navigation", telemetry_rate)
        
        # Navigation state
        self.latitude = 34.0522 + random.uniform(-0.1, 0.1)  # Los Angeles area
        self.longitude = -118.2437 + random.uniform(-0.1, 0.1)
        self.altitude = random.uniform(100, 500)  # meters
        self.heading = random.uniform(0, 360)  # degrees
        self.speed = random.uniform(10, 30)  # m/s
        self.gps_accuracy = random.uniform(1, 5)  # meters
        
        # IMU data
        self.roll = random.uniform(-5, 5)  # degrees
        self.pitch = random.uniform(-5, 5)  # degrees
        self.yaw_rate = random.uniform(-10, 10)  # degrees/s
        
        # Accelerometer data
        self.accel_x = random.uniform(-2, 2)  # m/s²
        self.accel_y = random.uniform(-2, 2)  # m/s²
        self.accel_z = random.uniform(-2, 2)  # m/s²
        
        # Gyroscope data
        self.gyro_x = random.uniform(-50, 50)  # degrees/s
        self.gyro_y = random.uniform(-50, 50)  # degrees/s
        self.gyro_z = random.uniform(-50, 50)  # degrees/s
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate navigation telemetry data."""
        # Simulate movement
        self._update_position()
        self._update_attitude()
        self._update_sensors()
        
        data = {
            "position": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude
            },
            "attitude": {
                "heading": self.heading,
                "roll": self.roll,
                "pitch": self.pitch,
                "yaw_rate": self.yaw_rate
            },
            "velocity": {
                "speed": self.speed,
                "direction": self.heading
            },
            "sensors": {
                "gps_accuracy": self.gps_accuracy,
                "accelerometer": {
                    "x": self.accel_x,
                    "y": self.accel_y,
                    "z": self.accel_z
                },
                "gyroscope": {
                    "x": self.gyro_x,
                    "y": self.gyro_y,
                    "z": self.gyro_z
                }
            },
            "status": {
                "gps_lock": self.gps_accuracy < 3.0,
                "imu_calibrated": True,
                "compass_valid": True
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply navigation fault."""
        fault_type = fault_params.get("type", "drift")
        
        if fault_type == "drift":
            # Simulate GPS drift
            drift_factor = fault_params.get("drift_factor", 0.1)
            telemetry_data.data["position"]["latitude"] += random.uniform(-drift_factor, drift_factor)
            telemetry_data.data["position"]["longitude"] += random.uniform(-drift_factor, drift_factor)
            telemetry_data.data["sensors"]["gps_accuracy"] *= 2
            telemetry_data.data["status"]["gps_lock"] = False
            
        elif fault_type == "imu_failure":
            # Simulate IMU failure
            telemetry_data.data["sensors"]["accelerometer"] = {"x": 0, "y": 0, "z": 0}
            telemetry_data.data["sensors"]["gyroscope"] = {"x": 0, "y": 0, "z": 0}
            telemetry_data.data["status"]["imu_calibrated"] = False
            
        elif fault_type == "compass_error":
            # Simulate compass error
            error_angle = fault_params.get("error_angle", 45)
            telemetry_data.data["attitude"]["heading"] += random.uniform(-error_angle, error_angle)
            telemetry_data.data["status"]["compass_valid"] = False
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_position(self) -> None:
        """Update UAV position based on current velocity."""
        # Simple position update simulation
        dt = 1.0 / self.telemetry_rate
        distance = self.speed * dt
        
        # Convert to lat/lon changes (simplified)
        lat_change = (distance * math.cos(math.radians(self.heading))) / 111000  # rough conversion
        lon_change = (distance * math.sin(math.radians(self.heading))) / (111000 * math.cos(math.radians(self.latitude)))
        
        self.latitude += lat_change
        self.longitude += lon_change
        
        # Add some random variation
        self.latitude += random.uniform(-0.0001, 0.0001)
        self.longitude += random.uniform(-0.0001, 0.0001)
        self.altitude += random.uniform(-0.5, 0.5)
    
    def _update_attitude(self) -> None:
        """Update UAV attitude."""
        # Simulate attitude changes
        self.roll += random.uniform(-0.5, 0.5)
        self.pitch += random.uniform(-0.5, 0.5)
        self.heading += random.uniform(-1, 1)
        
        # Keep values in valid ranges
        self.roll = max(-30, min(30, self.roll))
        self.pitch = max(-30, min(30, self.pitch))
        self.heading = self.heading % 360
    
    def _update_sensors(self) -> None:
        """Update sensor readings."""
        # Simulate sensor noise
        self.accel_x += random.uniform(-0.1, 0.1)
        self.accel_y += random.uniform(-0.1, 0.1)
        self.accel_z += random.uniform(-0.1, 0.1)
        
        self.gyro_x += random.uniform(-2, 2)
        self.gyro_y += random.uniform(-2, 2)
        self.gyro_z += random.uniform(-2, 2)
        
        # Add some realistic variation to speed
        self.speed += random.uniform(-0.5, 0.5)
        self.speed = max(0, min(50, self.speed))
