"""Sensor fusion subsystem agent."""

import random
import math
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class SensorFusionAgent(BaseAgent):
    """Agent for UAV sensor fusion subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 30.0):
        super().__init__(uav_id, "Sensor_Fusion", telemetry_rate)
        
        # IMU data
        self.imu_data = {
            "accelerometer": {"x": 0.0, "y": 0.0, "z": -9.81},  # m/s²
            "gyroscope": {"x": 0.0, "y": 0.0, "z": 0.0},  # rad/s
            "magnetometer": {"x": 0.0, "y": 0.0, "z": 0.0},  # μT
            "temperature": 25.0,  # °C
            "calibration_status": "calibrated"
        }
        
        # GPS data
        self.gps_data = {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "altitude": 100.0,  # meters
            "accuracy": 2.5,  # meters
            "satellites": 8,
            "fix_type": "3D",
            "hdop": 1.2,  # horizontal dilution of precision
            "vdop": 1.5,  # vertical dilution of precision
            "speed": 15.0,  # m/s
            "heading": 45.0  # degrees
        }
        
        # Barometer data
        self.barometer_data = {
            "pressure": 1013.25,  # hPa
            "altitude": 100.0,  # meters
            "temperature": 20.0,  # °C
            "calibration_offset": 0.0  # hPa
        }
        
        # Sensor fusion output
        self.fusion_output = {
            "position": {"x": 0.0, "y": 0.0, "z": 100.0},  # meters
            "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},  # m/s
            "attitude": {"roll": 0.0, "pitch": 0.0, "yaw": 45.0},  # degrees
            "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.0},  # rad/s
            "linear_acceleration": {"x": 0.0, "y": 0.0, "z": -9.81},  # m/s²
            "confidence": 0.95,  # 0-1 scale
            "fusion_mode": "gps_imu_baro"
        }
        
        # Sensor health
        self.sensor_health = {
            "imu_healthy": True,
            "gps_healthy": True,
            "barometer_healthy": True,
            "magnetometer_healthy": True,
            "fusion_algorithm_active": True,
            "kalman_filter_converged": True
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate sensor fusion telemetry data."""
        self._update_imu_data()
        self._update_gps_data()
        self._update_barometer_data()
        self._update_fusion_output()
        self._update_sensor_health()
        
        data = {
            "imu": self.imu_data,
            "gps": self.gps_data,
            "barometer": self.barometer_data,
            "fusion_output": self.fusion_output,
            "sensor_health": self.sensor_health,
            "status": {
                "fusion_healthy": self._is_fusion_healthy(),
                "position_accuracy": self._get_position_accuracy(),
                "attitude_accuracy": self._get_attitude_accuracy(),
                "sensor_redundancy": self._get_sensor_redundancy()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply sensor fusion fault."""
        fault_type = fault_params.get("type", "imu_failure")
        
        if fault_type == "imu_failure":
            # Simulate IMU failure
            telemetry_data.data["imu"]["accelerometer"] = {"x": 0, "y": 0, "z": 0}
            telemetry_data.data["imu"]["gyroscope"] = {"x": 0, "y": 0, "z": 0}
            telemetry_data.data["imu"]["calibration_status"] = "failed"
            telemetry_data.data["sensor_health"]["imu_healthy"] = False
            
        elif fault_type == "gps_failure":
            # Simulate GPS failure
            telemetry_data.data["gps"]["satellites"] = 0
            telemetry_data.data["gps"]["fix_type"] = "none"
            telemetry_data.data["gps"]["accuracy"] = 999.0
            telemetry_data.data["sensor_health"]["gps_healthy"] = False
            
        elif fault_type == "barometer_failure":
            # Simulate barometer failure
            telemetry_data.data["barometer"]["pressure"] = 0.0
            telemetry_data.data["barometer"]["altitude"] = 0.0
            telemetry_data.data["sensor_health"]["barometer_healthy"] = False
            
        elif fault_type == "magnetometer_failure":
            # Simulate magnetometer failure
            telemetry_data.data["imu"]["magnetometer"] = {"x": 0, "y": 0, "z": 0}
            telemetry_data.data["sensor_health"]["magnetometer_healthy"] = False
            
        elif fault_type == "fusion_algorithm_failure":
            # Simulate fusion algorithm failure
            telemetry_data.data["fusion_output"]["confidence"] = 0.0
            telemetry_data.data["fusion_output"]["fusion_mode"] = "failed"
            telemetry_data.data["sensor_health"]["fusion_algorithm_active"] = False
            
        elif fault_type == "kalman_filter_divergence":
            # Simulate Kalman filter divergence
            telemetry_data.data["sensor_health"]["kalman_filter_converged"] = False
            telemetry_data.data["fusion_output"]["confidence"] = 0.1
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_imu_data(self) -> None:
        """Update IMU telemetry data."""
        # Simulate accelerometer noise
        self.imu_data["accelerometer"]["x"] += random.uniform(-0.1, 0.1)
        self.imu_data["accelerometer"]["y"] += random.uniform(-0.1, 0.1)
        self.imu_data["accelerometer"]["z"] += random.uniform(-0.1, 0.1)
        
        # Simulate gyroscope noise
        self.imu_data["gyroscope"]["x"] += random.uniform(-0.01, 0.01)
        self.imu_data["gyroscope"]["y"] += random.uniform(-0.01, 0.01)
        self.imu_data["gyroscope"]["z"] += random.uniform(-0.01, 0.01)
        
        # Simulate magnetometer noise
        self.imu_data["magnetometer"]["x"] += random.uniform(-1, 1)
        self.imu_data["magnetometer"]["y"] += random.uniform(-1, 1)
        self.imu_data["magnetometer"]["z"] += random.uniform(-1, 1)
        
        # Simulate temperature changes
        self.imu_data["temperature"] += random.uniform(-0.5, 0.5)
        self.imu_data["temperature"] = max(15, min(60, self.imu_data["temperature"]))
        
        # Simulate occasional calibration status changes
        if random.random() < 0.001:  # 0.1% chance
            self.imu_data["calibration_status"] = random.choice(["calibrated", "calibrating", "failed"])
    
    def _update_gps_data(self) -> None:
        """Update GPS telemetry data."""
        # Simulate GPS position changes
        self.gps_data["latitude"] += random.uniform(-0.0001, 0.0001)
        self.gps_data["longitude"] += random.uniform(-0.0001, 0.0001)
        self.gps_data["altitude"] += random.uniform(-0.5, 0.5)
        
        # Simulate accuracy changes
        self.gps_data["accuracy"] += random.uniform(-0.2, 0.2)
        self.gps_data["accuracy"] = max(1.0, min(10.0, self.gps_data["accuracy"]))
        
        # Simulate satellite count changes
        self.gps_data["satellites"] += random.randint(-1, 1)
        self.gps_data["satellites"] = max(0, min(20, self.gps_data["satellites"]))
        
        # Simulate DOP changes
        self.gps_data["hdop"] += random.uniform(-0.1, 0.1)
        self.gps_data["hdop"] = max(0.5, min(5.0, self.gps_data["hdop"]))
        
        self.gps_data["vdop"] += random.uniform(-0.1, 0.1)
        self.gps_data["vdop"] = max(0.5, min(5.0, self.gps_data["vdop"]))
        
        # Simulate speed and heading changes
        self.gps_data["speed"] += random.uniform(-1, 1)
        self.gps_data["speed"] = max(0, min(50, self.gps_data["speed"]))
        
        self.gps_data["heading"] += random.uniform(-2, 2)
        self.gps_data["heading"] = self.gps_data["heading"] % 360
        
        # Update fix type based on satellite count
        if self.gps_data["satellites"] >= 4:
            self.gps_data["fix_type"] = "3D"
        elif self.gps_data["satellites"] >= 3:
            self.gps_data["fix_type"] = "2D"
        else:
            self.gps_data["fix_type"] = "none"
    
    def _update_barometer_data(self) -> None:
        """Update barometer telemetry data."""
        # Simulate pressure changes
        self.barometer_data["pressure"] += random.uniform(-1, 1)
        self.barometer_data["pressure"] = max(950, min(1050, self.barometer_data["pressure"]))
        
        # Calculate altitude from pressure
        self.barometer_data["altitude"] = 44330 * (1 - (self.barometer_data["pressure"] / 1013.25) ** 0.1903)
        
        # Simulate temperature changes
        self.barometer_data["temperature"] += random.uniform(-0.5, 0.5)
        self.barometer_data["temperature"] = max(15, min(40, self.barometer_data["temperature"]))
        
        # Simulate calibration offset changes
        self.barometer_data["calibration_offset"] += random.uniform(-0.1, 0.1)
        self.barometer_data["calibration_offset"] = max(-5, min(5, self.barometer_data["calibration_offset"]))
    
    def _update_fusion_output(self) -> None:
        """Update sensor fusion output."""
        # Update position based on GPS and barometer
        self.fusion_output["position"]["x"] = self.gps_data["longitude"] * 111000  # rough conversion
        self.fusion_output["position"]["y"] = self.gps_data["latitude"] * 111000
        self.fusion_output["position"]["z"] = (self.gps_data["altitude"] + self.barometer_data["altitude"]) / 2
        
        # Update velocity based on GPS
        self.fusion_output["velocity"]["x"] = self.gps_data["speed"] * math.cos(math.radians(self.gps_data["heading"]))
        self.fusion_output["velocity"]["y"] = self.gps_data["speed"] * math.sin(math.radians(self.gps_data["heading"]))
        self.fusion_output["velocity"]["z"] = random.uniform(-2, 2)
        
        # Update attitude based on IMU
        self.fusion_output["attitude"]["roll"] = random.uniform(-5, 5)
        self.fusion_output["attitude"]["pitch"] = random.uniform(-5, 5)
        self.fusion_output["attitude"]["yaw"] = self.gps_data["heading"]
        
        # Update angular velocity
        self.fusion_output["angular_velocity"]["x"] = self.imu_data["gyroscope"]["x"]
        self.fusion_output["angular_velocity"]["y"] = self.imu_data["gyroscope"]["y"]
        self.fusion_output["angular_velocity"]["z"] = self.imu_data["gyroscope"]["z"]
        
        # Update linear acceleration
        self.fusion_output["linear_acceleration"]["x"] = self.imu_data["accelerometer"]["x"]
        self.fusion_output["linear_acceleration"]["y"] = self.imu_data["accelerometer"]["y"]
        self.fusion_output["linear_acceleration"]["z"] = self.imu_data["accelerometer"]["z"]
        
        # Update confidence based on sensor health
        healthy_sensors = sum([
            self.sensor_health["imu_healthy"],
            self.sensor_health["gps_healthy"],
            self.sensor_health["barometer_healthy"],
            self.sensor_health["magnetometer_healthy"]
        ])
        
        self.fusion_output["confidence"] = healthy_sensors / 4.0
        
        # Update fusion mode
        if self.sensor_health["gps_healthy"] and self.sensor_health["imu_healthy"]:
            self.fusion_output["fusion_mode"] = "gps_imu_baro"
        elif self.sensor_health["imu_healthy"] and self.sensor_health["barometer_healthy"]:
            self.fusion_output["fusion_mode"] = "imu_baro"
        elif self.sensor_health["imu_healthy"]:
            self.fusion_output["fusion_mode"] = "imu_only"
        else:
            self.fusion_output["fusion_mode"] = "failed"
    
    def _update_sensor_health(self) -> None:
        """Update sensor health status."""
        # Update IMU health based on data quality
        self.sensor_health["imu_healthy"] = (
            self.imu_data["calibration_status"] == "calibrated" and
            self.imu_data["temperature"] < 50
        )
        
        # Update GPS health based on satellite count and accuracy
        self.sensor_health["gps_healthy"] = (
            self.gps_data["satellites"] >= 4 and
            self.gps_data["accuracy"] < 5.0 and
            self.gps_data["fix_type"] == "3D"
        )
        
        # Update barometer health based on pressure range
        self.sensor_health["barometer_healthy"] = (
            950 < self.barometer_data["pressure"] < 1050 and
            abs(self.barometer_data["calibration_offset"]) < 2.0
        )
        
        # Update magnetometer health based on data quality
        mag_strength = math.sqrt(
            self.imu_data["magnetometer"]["x"]**2 +
            self.imu_data["magnetometer"]["y"]**2 +
            self.imu_data["magnetometer"]["z"]**2
        )
        self.sensor_health["magnetometer_healthy"] = (20 < mag_strength < 60)
        
        # Update fusion algorithm status
        self.sensor_health["fusion_algorithm_active"] = (
            self.sensor_health["imu_healthy"] and
            (self.sensor_health["gps_healthy"] or self.sensor_health["barometer_healthy"])
        )
        
        # Update Kalman filter convergence
        self.sensor_health["kalman_filter_converged"] = (
            self.fusion_output["confidence"] > 0.8 and
            self.sensor_health["fusion_algorithm_active"]
        )
    
    def _is_fusion_healthy(self) -> bool:
        """Check if sensor fusion is healthy."""
        return (
            self.sensor_health["fusion_algorithm_active"] and
            self.sensor_health["kalman_filter_converged"] and
            self.fusion_output["confidence"] > 0.7
        )
    
    def _get_position_accuracy(self) -> str:
        """Get position accuracy rating."""
        accuracy = self.gps_data["accuracy"]
        if accuracy < 2.0:
            return "high"
        elif accuracy < 5.0:
            return "medium"
        else:
            return "low"
    
    def _get_attitude_accuracy(self) -> str:
        """Get attitude accuracy rating."""
        if self.sensor_health["magnetometer_healthy"] and self.sensor_health["imu_healthy"]:
            return "high"
        elif self.sensor_health["imu_healthy"]:
            return "medium"
        else:
            return "low"
    
    def _get_sensor_redundancy(self) -> str:
        """Get sensor redundancy level."""
        healthy_count = sum([
            self.sensor_health["imu_healthy"],
            self.sensor_health["gps_healthy"],
            self.sensor_health["barometer_healthy"],
            self.sensor_health["magnetometer_healthy"]
        ])
        
        if healthy_count >= 4:
            return "full"
        elif healthy_count >= 3:
            return "good"
        elif healthy_count >= 2:
            return "limited"
        else:
            return "critical"
