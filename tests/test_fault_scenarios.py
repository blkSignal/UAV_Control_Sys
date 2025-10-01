"""Comprehensive test suite for 50+ failure scenarios."""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.telemetry_manager import TelemetryManager
from src.fault_injection.fault_manager import FaultManager, FaultType
from src.anomaly.anomaly_detector import AnomalyDetector
from src.utils.models import TelemetryData, Alert, SeverityLevel


class TestFaultScenarios:
    """Test suite for fault injection scenarios."""
    
    async def setUp(self):
        """Setup simulator components for testing."""
        self.telemetry_manager = TelemetryManager()
        self.fault_manager = FaultManager()
        self.anomaly_detector = AnomalyDetector()
        
        # Add test UAV
        await self.telemetry_manager.add_uav("TEST_UAV_001")
        await self.telemetry_manager.start()
        await self.fault_manager.start()
    
    async def tearDown(self):
        """Cleanup after tests."""
        await self.telemetry_manager.stop()
        await self.fault_manager.stop()
    
    # Navigation Fault Scenarios (5 scenarios)
    
    @pytest.mark.asyncio
    async def test_gps_drift_fault(self):
        """Test GPS drift fault injection."""
        await self.setUp()
        try:
            await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.GPS_DRIFT,
            {"drift_factor": 0.1, "duration": 30}
        )
        
        # Verify fault is active
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
        assert "TEST_UAV_001_Navigation_gps_drift" in active_faults
    
    @pytest.mark.asyncio
    async def test_imu_failure_fault(self, setup_simulator):
        """Test IMU failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.IMU_FAILURE,
            {"duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_compass_error_fault(self, setup_simulator):
        """Test compass error fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.COMPASS_ERROR,
            {"error_angle": 45, "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_navigation_sensor_degradation(self, setup_simulator):
        """Test navigation sensor degradation."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.GPS_DRIFT,
            {"drift_factor": 0.05, "duration": 120}
        )
        
        # Test anomaly detection
        await asyncio.sleep(1)  # Allow time for telemetry generation
        
        stats = self.anomaly_detector.get_statistics()
        assert stats["total_predictions"] > 0
    
    @pytest.mark.asyncio
    async def test_navigation_calibration_loss(self, setup_simulator):
        """Test navigation calibration loss."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.IMU_FAILURE,
            {"calibration_loss": True, "duration": 90}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Propulsion Fault Scenarios (8 scenarios)
    
    @pytest.mark.asyncio
    async def test_motor_failure_fault(self, setup_simulator):
        """Test motor failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.MOTOR_FAILURE,
            {"motor_id": "motor_1", "duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_esc_failure_fault(self, setup_simulator):
        """Test ESC failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.ESC_FAILURE,
            {"esc_id": "esc_1", "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_propeller_damage_fault(self, setup_simulator):
        """Test propeller damage fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.PROPELLER_DAMAGE,
            {"prop_id": "prop_1", "damage_level": 0.5, "duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_thrust_reduction_fault(self, setup_simulator):
        """Test thrust reduction fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.THRUST_REDUCTION,
            {"reduction_factor": 0.3, "duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_motor_overheating(self, setup_simulator):
        """Test motor overheating scenario."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.MOTOR_FAILURE,
            {"motor_id": "motor_2", "overheating": True, "temperature": 100, "duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_propeller_imbalance(self, setup_simulator):
        """Test propeller imbalance scenario."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.PROPELLER_DAMAGE,
            {"prop_id": "prop_2", "imbalance": True, "balance_factor": 0.3, "duration": 75}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_esc_thermal_protection(self, setup_simulator):
        """Test ESC thermal protection activation."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.ESC_FAILURE,
            {"esc_id": "esc_2", "thermal_protection": True, "duration": 35}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_propulsion_power_surge(self, setup_simulator):
        """Test propulsion power surge scenario."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.THRUST_REDUCTION,
            {"power_surge": True, "surge_factor": 1.5, "duration": 15}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Communication Fault Scenarios (6 scenarios)
    
    @pytest.mark.asyncio
    async def test_signal_loss_fault(self, setup_simulator):
        """Test signal loss fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.SIGNAL_LOSS,
            {"duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_satellite_loss_fault(self, setup_simulator):
        """Test satellite communication loss fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.SATELLITE_LOSS,
            {"duration": 90}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_radio_interference_fault(self, setup_simulator):
        """Test radio interference fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.INTERFERENCE,
            {"interference_level": 0.5, "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_encryption_failure_fault(self, setup_simulator):
        """Test encryption failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.ENCRYPTION_FAILURE,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_bandwidth_reduction_fault(self, setup_simulator):
        """Test bandwidth reduction fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.BANDWIDTH_REDUCTION,
            {"reduction_factor": 0.5, "duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_communication_jamming(self, setup_simulator):
        """Test communication jamming scenario."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.INTERFERENCE,
            {"jamming": True, "jamming_power": 0.8, "duration": 120}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Power Fault Scenarios (7 scenarios)
    
    @pytest.mark.asyncio
    async def test_voltage_drop_fault(self, setup_simulator):
        """Test voltage drop fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.VOLTAGE_DROP,
            {"drop_factor": 0.3, "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_battery_failure_fault(self, setup_simulator):
        """Test battery failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.BATTERY_FAILURE,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_overcurrent_fault(self, setup_simulator):
        """Test overcurrent fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.OVERCURRENT,
            {"duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_thermal_runaway_fault(self, setup_simulator):
        """Test thermal runaway fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.THERMAL_RUNAWAY,
            {"duration": 15}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_power_distribution_failure(self, setup_simulator):
        """Test power distribution failure."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.POWER_DISTRIBUTION_FAILURE,
            {"subsystem": "propulsion", "duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_solar_panel_failure(self, setup_simulator):
        """Test solar panel failure."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.SOLAR_FAILURE,
            {"duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_battery_cell_failure(self, setup_simulator):
        """Test battery cell failure scenario."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.BATTERY_FAILURE,
            {"cell_failure": True, "failed_cells": 2, "duration": 50}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Payload Fault Scenarios (6 scenarios)
    
    @pytest.mark.asyncio
    async def test_camera_failure_fault(self, setup_simulator):
        """Test camera failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Payload", FaultType.CAMERA_FAILURE,
            {"duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_gimbal_failure_fault(self, setup_simulator):
        """Test gimbal failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Payload", FaultType.GIMBAL_FAILURE,
            {"duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_sensor_failure_fault(self, setup_simulator):
        """Test sensor failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Payload", FaultType.SENSOR_FAILURE,
            {"sensor_type": "lidar", "duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_storage_failure_fault(self, setup_simulator):
        """Test storage failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Payload", FaultType.STORAGE_FAILURE,
            {"duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_delivery_failure_fault(self, setup_simulator):
        """Test delivery mechanism failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Payload", FaultType.DELIVERY_FAILURE,
            {"duration": 25}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_data_corruption_fault(self, setup_simulator):
        """Test data corruption fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Payload", FaultType.DATA_CORRUPTION,
            {"duration": 35}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Environmental Fault Scenarios (5 scenarios)
    
    @pytest.mark.asyncio
    async def test_severe_weather_fault(self, setup_simulator):
        """Test severe weather conditions."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Environmental", FaultType.SEVERE_WEATHER,
            {"wind_speed": 25, "precipitation": 50, "duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_air_pollution_fault(self, setup_simulator):
        """Test air pollution conditions."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Environmental", FaultType.AIR_POLLUTION,
            {"pm2_5": 100, "pm10": 150, "duration": 90}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_radiation_spike_fault(self, setup_simulator):
        """Test radiation spike conditions."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Environmental", FaultType.RADIATION_SPIKE,
            {"uv_index": 15, "duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_icing_conditions_fault(self, setup_simulator):
        """Test icing conditions."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Environmental", FaultType.ICING_CONDITIONS,
            {"temperature": -5, "humidity": 90, "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_environmental_sensor_failure(self, setup_simulator):
        """Test environmental sensor failure."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Environmental", FaultType.SENSOR_FAILURE_ENV,
            {"sensor_type": "temperature", "duration": 60}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Flight Control Fault Scenarios (6 scenarios)
    
    @pytest.mark.asyncio
    async def test_servo_failure_fault(self, setup_simulator):
        """Test servo failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Flight_Control", FaultType.SERVO_FAILURE,
            {"servo_id": 0, "duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_control_surface_jam_fault(self, setup_simulator):
        """Test control surface jam fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Flight_Control", FaultType.CONTROL_SURFACE_JAM,
            {"surface": "aileron_left", "duration": 50}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_autopilot_failure_fault(self, setup_simulator):
        """Test autopilot failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Flight_Control", FaultType.AUTOPILOT_FAILURE,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_fly_by_wire_failure_fault(self, setup_simulator):
        """Test fly-by-wire failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Flight_Control", FaultType.FLY_BY_WIRE_FAILURE,
            {"duration": 35}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_control_authority_loss_fault(self, setup_simulator):
        """Test control authority loss fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Flight_Control", FaultType.CONTROL_AUTHORITY_LOSS,
            {"reduction_factor": 0.5, "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_trim_failure_fault(self, setup_simulator):
        """Test trim system failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Flight_Control", FaultType.TRIM_FAILURE,
            {"duration": 25}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Sensor Fusion Fault Scenarios (6 scenarios)
    
    @pytest.mark.asyncio
    async def test_imu_failure_sensor_fusion(self, setup_simulator):
        """Test IMU failure in sensor fusion."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Sensor_Fusion", FaultType.IMU_FAILURE_SF,
            {"duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_gps_failure_sensor_fusion(self, setup_simulator):
        """Test GPS failure in sensor fusion."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Sensor_Fusion", FaultType.GPS_FAILURE_SF,
            {"duration": 50}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_barometer_failure_fault(self, setup_simulator):
        """Test barometer failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Sensor_Fusion", FaultType.BAROMETER_FAILURE,
            {"duration": 35}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_magnetometer_failure_fault(self, setup_simulator):
        """Test magnetometer failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Sensor_Fusion", FaultType.MAGNETOMETER_FAILURE,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_fusion_algorithm_failure_fault(self, setup_simulator):
        """Test fusion algorithm failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Sensor_Fusion", FaultType.FUSION_ALGORITHM_FAILURE,
            {"duration": 25}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_kalman_filter_divergence_fault(self, setup_simulator):
        """Test Kalman filter divergence fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Sensor_Fusion", FaultType.KALMAN_FILTER_DIVERGENCE,
            {"duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Mission Planning Fault Scenarios (5 scenarios)
    
    @pytest.mark.asyncio
    async def test_waypoint_corruption_fault(self, setup_simulator):
        """Test waypoint corruption fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Mission_Planning", FaultType.WAYPOINT_CORRUPTION,
            {"waypoint_id": 3, "duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_mission_abort_fault(self, setup_simulator):
        """Test mission abort fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Mission_Planning", FaultType.MISSION_ABORT,
            {"duration": 10}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_constraint_violation_fault(self, setup_simulator):
        """Test constraint violation fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Mission_Planning", FaultType.CONSTRAINT_VIOLATION,
            {"constraint_type": "altitude", "duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_replanning_failure_fault(self, setup_simulator):
        """Test replanning failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Mission_Planning", FaultType.REPLANNING_FAILURE,
            {"duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_progress_calculation_error_fault(self, setup_simulator):
        """Test progress calculation error fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Mission_Planning", FaultType.PROGRESS_CALCULATION_ERROR,
            {"duration": 15}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Safety Systems Fault Scenarios (6 scenarios)
    
    @pytest.mark.asyncio
    async def test_parachute_failure_fault(self, setup_simulator):
        """Test parachute failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.PARACHUTE_FAILURE,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_collision_avoidance_failure_fault(self, setup_simulator):
        """Test collision avoidance failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.COLLISION_AVOIDANCE_FAILURE,
            {"duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_geofence_failure_fault(self, setup_simulator):
        """Test geofence failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.GEOFENCE_FAILURE,
            {"duration": 35}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_backup_system_failure_fault(self, setup_simulator):
        """Test backup system failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.BACKUP_SYSTEM_FAILURE,
            {"backup_type": "power", "duration": 25}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_safety_limit_violation_fault(self, setup_simulator):
        """Test safety limit violation fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.SAFETY_LIMIT_VIOLATION,
            {"limit_type": "altitude", "duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_emergency_response_failure_fault(self, setup_simulator):
        """Test emergency response failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.EMERGENCY_RESPONSE_FAILURE,
            {"duration": 15}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Data Storage Fault Scenarios (7 scenarios)
    
    @pytest.mark.asyncio
    async def test_storage_failure_data_storage(self, setup_simulator):
        """Test storage failure in data storage subsystem."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.STORAGE_FAILURE_DS,
            {"device": "primary_ssd", "duration": 45}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_data_corruption_data_storage(self, setup_simulator):
        """Test data corruption in data storage subsystem."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.DATA_CORRUPTION_DS,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_transmission_failure_fault(self, setup_simulator):
        """Test transmission failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.TRANSMISSION_FAILURE,
            {"duration": 40}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_encryption_failure_data_storage(self, setup_simulator):
        """Test encryption failure in data storage subsystem."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.ENCRYPTION_FAILURE_DS,
            {"duration": 35}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_backup_failure_fault(self, setup_simulator):
        """Test backup failure fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.BACKUP_FAILURE,
            {"duration": 25}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_capacity_exhaustion_fault(self, setup_simulator):
        """Test capacity exhaustion fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.CAPACITY_EXHAUSTION,
            {"duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    @pytest.mark.asyncio
    async def test_performance_degradation_fault(self, setup_simulator):
        """Test performance degradation fault injection."""
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Data_Storage", FaultType.PERFORMANCE_DEGRADATION,
            {"degradation_factor": 0.5, "duration": 50}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
    
    # Multi-fault Scenarios (3 scenarios)
    
    @pytest.mark.asyncio
    async def test_cascading_failures(self, setup_simulator):
        """Test cascading failure scenario."""
        # Inject multiple related faults
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.VOLTAGE_DROP,
            {"drop_factor": 0.4, "duration": 60}
        )
        
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.THRUST_REDUCTION,
            {"reduction_factor": 0.3, "duration": 45}
        )
        
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.SIGNAL_LOSS,
            {"duration": 30}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 3
    
    @pytest.mark.asyncio
    async def test_simultaneous_subsystem_failures(self, setup_simulator):
        """Test simultaneous subsystem failures."""
        subsystems = ["Navigation", "Propulsion", "Communication", "Power"]
        
        for subsystem in subsystems:
            await self.fault_manager.inject_fault(
                "TEST_UAV_001", subsystem, FaultType.SENSOR_FAILURE,
                {"duration": 40}
            )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 4
    
    @pytest.mark.asyncio
    async def test_critical_system_failure(self, setup_simulator):
        """Test critical system failure scenario."""
        # Inject critical faults
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Power", FaultType.BATTERY_FAILURE,
            {"duration": 30}
        )
        
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.MOTOR_FAILURE,
            {"motor_id": "motor_1", "duration": 25}
        )
        
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Safety_Systems", FaultType.PARACHUTE_FAILURE,
            {"duration": 20}
        )
        
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 3
    
    # Fault Recovery Tests (3 scenarios)
    
    @pytest.mark.asyncio
    async def test_fault_clearance(self, setup_simulator):
        """Test fault clearance functionality."""
        # Inject fault
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.GPS_DRIFT,
            {"drift_factor": 0.1, "duration": 60}
        )
        
        # Verify fault is active
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
        
        # Clear fault
        await self.fault_manager.clear_fault(
            "TEST_UAV_001", "Navigation", FaultType.GPS_DRIFT
        )
        
        # Verify fault is cleared
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 0
    
    @pytest.mark.asyncio
    async def test_automatic_fault_expiry(self, setup_simulator):
        """Test automatic fault expiry."""
        # Inject fault with short duration
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Communication", FaultType.SIGNAL_LOSS,
            {"duration": 2}  # 2 seconds
        )
        
        # Verify fault is active
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 1
        
        # Wait for fault to expire
        await asyncio.sleep(3)
        
        # Verify fault is automatically cleared
        active_faults = self.fault_manager.get_active_faults()
        assert len(active_faults) == 0
    
    @pytest.mark.asyncio
    async def test_fault_statistics_tracking(self, setup_simulator):
        """Test fault statistics tracking."""
        # Inject multiple faults
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Navigation", FaultType.GPS_DRIFT,
            {"duration": 30}
        )
        
        await self.fault_manager.inject_fault(
            "TEST_UAV_001", "Propulsion", FaultType.MOTOR_FAILURE,
            {"duration": 25}
        )
        
        # Check statistics
        stats = self.fault_manager.get_statistics()
        assert stats["total_faults_injected"] >= 2
        assert stats["active_faults"] == 2
        assert "gps_drift" in stats["faults_by_type"]
        assert "motor_failure" in stats["faults_by_type"]
        assert "Navigation" in stats["faults_by_subsystem"]
        assert "Propulsion" in stats["faults_by_subsystem"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
