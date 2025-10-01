"""Environmental subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class EnvironmentalAgent(BaseAgent):
    """Agent for UAV environmental subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 12.0):
        super().__init__(uav_id, "Environmental", telemetry_rate)
        
        # Weather data
        self.weather_data = {
            "temperature": 20.0,  # °C
            "humidity": 60.0,  # %
            "pressure": 1013.25,  # hPa
            "wind_speed": 5.0,  # m/s
            "wind_direction": 180.0,  # degrees
            "visibility": 10.0,  # km
            "precipitation": 0.0,  # mm/h
            "cloud_cover": 30.0  # %
        }
        
        # Air quality data
        self.air_quality_data = {
            "pm2_5": 15.0,  # μg/m³
            "pm10": 25.0,  # μg/m³
            "co2": 400.0,  # ppm
            "no2": 20.0,  # ppb
            "o3": 50.0,  # ppb
            "air_quality_index": 2  # 1-6 scale
        }
        
        # Radiation data
        self.radiation_data = {
            "uv_index": 5.0,
            "solar_radiation": 500.0,  # W/m²
            "cosmic_radiation": 0.1,  # μSv/h
            "terrestrial_radiation": 0.05  # μSv/h
        }
        
        # Environmental hazards
        self.hazard_data = {
            "turbulence_detected": False,
            "turbulence_severity": 0.0,  # 0-1 scale
            "lightning_risk": 0.1,  # 0-1 scale
            "icing_risk": 0.0,  # 0-1 scale
            "dust_storm": False,
            "smog_level": 0.2  # 0-1 scale
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate environmental telemetry data."""
        self._update_weather_data()
        self._update_air_quality_data()
        self._update_radiation_data()
        self._update_hazard_data()
        
        data = {
            "weather": self.weather_data,
            "air_quality": self.air_quality_data,
            "radiation": self.radiation_data,
            "hazards": self.hazard_data,
            "status": {
                "flight_conditions": self._get_flight_conditions(),
                "environmental_risk": self._get_environmental_risk(),
                "weather_severity": self._get_weather_severity(),
                "air_quality_status": self._get_air_quality_status()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply environmental fault."""
        fault_type = fault_params.get("type", "sensor_failure")
        
        if fault_type == "sensor_failure":
            # Simulate sensor failure
            sensor_type = fault_params.get("sensor_type", "temperature")
            if sensor_type == "temperature":
                telemetry_data.data["weather"]["temperature"] = -999.0
            elif sensor_type == "pressure":
                telemetry_data.data["weather"]["pressure"] = 0.0
            elif sensor_type == "wind":
                telemetry_data.data["weather"]["wind_speed"] = 0.0
                
        elif fault_type == "severe_weather":
            # Simulate severe weather conditions
            telemetry_data.data["weather"]["wind_speed"] = 25.0
            telemetry_data.data["weather"]["precipitation"] = 50.0
            telemetry_data.data["weather"]["visibility"] = 1.0
            telemetry_data.data["hazards"]["turbulence_detected"] = True
            telemetry_data.data["hazards"]["turbulence_severity"] = 0.8
            
        elif fault_type == "air_pollution":
            # Simulate air pollution
            telemetry_data.data["air_quality"]["pm2_5"] = 100.0
            telemetry_data.data["air_quality"]["pm10"] = 150.0
            telemetry_data.data["air_quality"]["air_quality_index"] = 6
            telemetry_data.data["hazards"]["smog_level"] = 0.9
            
        elif fault_type == "radiation_spike":
            # Simulate radiation spike
            telemetry_data.data["radiation"]["uv_index"] = 15.0
            telemetry_data.data["radiation"]["cosmic_radiation"] = 1.0
            
        elif fault_type == "icing_conditions":
            # Simulate icing conditions
            telemetry_data.data["weather"]["temperature"] = -5.0
            telemetry_data.data["weather"]["humidity"] = 90.0
            telemetry_data.data["hazards"]["icing_risk"] = 0.9
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_weather_data(self) -> None:
        """Update weather telemetry data."""
        # Simulate temperature changes
        self.weather_data["temperature"] += random.uniform(-1, 1)
        self.weather_data["temperature"] = max(-40, min(50, self.weather_data["temperature"]))
        
        # Simulate humidity changes
        self.weather_data["humidity"] += random.uniform(-2, 2)
        self.weather_data["humidity"] = max(0, min(100, self.weather_data["humidity"]))
        
        # Simulate pressure changes
        self.weather_data["pressure"] += random.uniform(-2, 2)
        self.weather_data["pressure"] = max(950, min(1050, self.weather_data["pressure"]))
        
        # Simulate wind changes
        self.weather_data["wind_speed"] += random.uniform(-1, 1)
        self.weather_data["wind_speed"] = max(0, min(30, self.weather_data["wind_speed"]))
        
        self.weather_data["wind_direction"] += random.uniform(-5, 5)
        self.weather_data["wind_direction"] = self.weather_data["wind_direction"] % 360
        
        # Simulate visibility changes
        self.weather_data["visibility"] += random.uniform(-0.5, 0.5)
        self.weather_data["visibility"] = max(0.1, min(50, self.weather_data["visibility"]))
        
        # Simulate precipitation
        self.weather_data["precipitation"] += random.uniform(-0.5, 0.5)
        self.weather_data["precipitation"] = max(0, min(100, self.weather_data["precipitation"]))
        
        # Simulate cloud cover
        self.weather_data["cloud_cover"] += random.uniform(-2, 2)
        self.weather_data["cloud_cover"] = max(0, min(100, self.weather_data["cloud_cover"]))
    
    def _update_air_quality_data(self) -> None:
        """Update air quality telemetry data."""
        # Simulate PM2.5 changes
        self.air_quality_data["pm2_5"] += random.uniform(-2, 2)
        self.air_quality_data["pm2_5"] = max(0, min(200, self.air_quality_data["pm2_5"]))
        
        # Simulate PM10 changes
        self.air_quality_data["pm10"] += random.uniform(-3, 3)
        self.air_quality_data["pm10"] = max(0, min(300, self.air_quality_data["pm10"]))
        
        # Simulate CO2 changes
        self.air_quality_data["co2"] += random.uniform(-5, 5)
        self.air_quality_data["co2"] = max(300, min(1000, self.air_quality_data["co2"]))
        
        # Simulate NO2 changes
        self.air_quality_data["no2"] += random.uniform(-1, 1)
        self.air_quality_data["no2"] = max(0, min(100, self.air_quality_data["no2"]))
        
        # Simulate O3 changes
        self.air_quality_data["o3"] += random.uniform(-2, 2)
        self.air_quality_data["o3"] = max(0, min(200, self.air_quality_data["o3"]))
        
        # Update air quality index based on PM2.5
        if self.air_quality_data["pm2_5"] < 12:
            self.air_quality_data["air_quality_index"] = 1
        elif self.air_quality_data["pm2_5"] < 35:
            self.air_quality_data["air_quality_index"] = 2
        elif self.air_quality_data["pm2_5"] < 55:
            self.air_quality_data["air_quality_index"] = 3
        elif self.air_quality_data["pm2_5"] < 75:
            self.air_quality_data["air_quality_index"] = 4
        elif self.air_quality_data["pm2_5"] < 110:
            self.air_quality_data["air_quality_index"] = 5
        else:
            self.air_quality_data["air_quality_index"] = 6
    
    def _update_radiation_data(self) -> None:
        """Update radiation telemetry data."""
        # Simulate UV index changes
        self.radiation_data["uv_index"] += random.uniform(-0.5, 0.5)
        self.radiation_data["uv_index"] = max(0, min(15, self.radiation_data["uv_index"]))
        
        # Simulate solar radiation changes
        self.radiation_data["solar_radiation"] += random.uniform(-20, 20)
        self.radiation_data["solar_radiation"] = max(0, min(1000, self.radiation_data["solar_radiation"]))
        
        # Simulate cosmic radiation changes
        self.radiation_data["cosmic_radiation"] += random.uniform(-0.01, 0.01)
        self.radiation_data["cosmic_radiation"] = max(0, min(1, self.radiation_data["cosmic_radiation"]))
        
        # Simulate terrestrial radiation changes
        self.radiation_data["terrestrial_radiation"] += random.uniform(-0.005, 0.005)
        self.radiation_data["terrestrial_radiation"] = max(0, min(0.5, self.radiation_data["terrestrial_radiation"]))
    
    def _update_hazard_data(self) -> None:
        """Update environmental hazard data."""
        # Simulate turbulence detection
        if self.weather_data["wind_speed"] > 15:
            self.hazard_data["turbulence_detected"] = random.random() < 0.3
            self.hazard_data["turbulence_severity"] = min(1.0, self.weather_data["wind_speed"] / 30)
        else:
            self.hazard_data["turbulence_detected"] = False
            self.hazard_data["turbulence_severity"] = 0
        
        # Simulate lightning risk
        if self.weather_data["precipitation"] > 10 and self.weather_data["cloud_cover"] > 70:
            self.hazard_data["lightning_risk"] = min(1.0, self.weather_data["precipitation"] / 50)
        else:
            self.hazard_data["lightning_risk"] = max(0, self.hazard_data["lightning_risk"] - 0.01)
        
        # Simulate icing risk
        if self.weather_data["temperature"] < 2 and self.weather_data["humidity"] > 80:
            self.hazard_data["icing_risk"] = min(1.0, (2 - self.weather_data["temperature"]) / 10)
        else:
            self.hazard_data["icing_risk"] = max(0, self.hazard_data["icing_risk"] - 0.01)
        
        # Simulate dust storm
        if self.weather_data["wind_speed"] > 20 and self.air_quality_data["pm10"] > 100:
            self.hazard_data["dust_storm"] = random.random() < 0.1
        else:
            self.hazard_data["dust_storm"] = False
        
        # Simulate smog level
        if self.air_quality_data["air_quality_index"] > 4:
            self.hazard_data["smog_level"] = min(1.0, self.air_quality_data["air_quality_index"] / 6)
        else:
            self.hazard_data["smog_level"] = max(0, self.hazard_data["smog_level"] - 0.01)
    
    def _get_flight_conditions(self) -> str:
        """Get flight conditions rating."""
        if (self.weather_data["wind_speed"] > 20 or 
            self.weather_data["visibility"] < 2 or 
            self.hazard_data["turbulence_detected"]):
            return "poor"
        elif (self.weather_data["wind_speed"] > 15 or 
              self.weather_data["visibility"] < 5 or 
              self.weather_data["precipitation"] > 5):
            return "fair"
        else:
            return "good"
    
    def _get_environmental_risk(self) -> str:
        """Get environmental risk level."""
        risk_score = (
            self.hazard_data["turbulence_severity"] +
            self.hazard_data["lightning_risk"] +
            self.hazard_data["icing_risk"] +
            self.hazard_data["smog_level"]
        ) / 4
        
        if risk_score > 0.7:
            return "high"
        elif risk_score > 0.3:
            return "medium"
        else:
            return "low"
    
    def _get_weather_severity(self) -> str:
        """Get weather severity rating."""
        if (self.weather_data["wind_speed"] > 25 or 
            self.weather_data["precipitation"] > 20 or 
            self.hazard_data["turbulence_severity"] > 0.8):
            return "severe"
        elif (self.weather_data["wind_speed"] > 15 or 
              self.weather_data["precipitation"] > 10 or 
              self.hazard_data["turbulence_severity"] > 0.5):
            return "moderate"
        else:
            return "mild"
    
    def _get_air_quality_status(self) -> str:
        """Get air quality status."""
        aqi = self.air_quality_data["air_quality_index"]
        if aqi <= 2:
            return "good"
        elif aqi <= 4:
            return "moderate"
        else:
            return "unhealthy"
