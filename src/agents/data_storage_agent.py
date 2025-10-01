"""Data storage subsystem agent."""

import random
from datetime import datetime
from typing import Dict, Any

from .base_agent import BaseAgent
from ..utils.models import TelemetryData, SystemStatus


class DataStorageAgent(BaseAgent):
    """Agent for UAV data storage subsystem."""
    
    def __init__(self, uav_id: str, telemetry_rate: float = 3.0):
        super().__init__(uav_id, "Data_Storage", telemetry_rate)
        
        # Storage devices
        self.storage_devices = {
            "primary_ssd": {
                "capacity": 1000,  # GB
                "used": 250,  # GB
                "available": 750,  # GB
                "temperature": 35.0,  # °C
                "health": 95.0,  # %
                "read_speed": 500,  # MB/s
                "write_speed": 450,  # MB/s
                "status": "healthy"
            },
            "secondary_ssd": {
                "capacity": 500,  # GB
                "used": 100,  # GB
                "available": 400,  # GB
                "temperature": 32.0,  # °C
                "health": 98.0,  # %
                "read_speed": 480,  # MB/s
                "write_speed": 420,  # MB/s
                "status": "healthy"
            },
            "external_storage": {
                "capacity": 2000,  # GB
                "used": 800,  # GB
                "available": 1200,  # GB
                "temperature": 28.0,  # °C
                "health": 92.0,  # %
                "read_speed": 100,  # MB/s
                "write_speed": 80,  # MB/s
                "status": "healthy",
                "connected": True
            }
        }
        
        # Data management
        self.data_management = {
            "total_data_stored": 1150,  # GB
            "data_compression_ratio": 0.3,  # 30% compression
            "encryption_enabled": True,
            "encryption_algorithm": "AES-256",
            "backup_enabled": True,
            "backup_frequency": 3600,  # seconds
            "last_backup": datetime.now(),
            "data_integrity_check": True,
            "last_integrity_check": datetime.now()
        }
        
        # Data transmission
        self.data_transmission = {
            "transmission_queue_size": 50,  # MB
            "transmission_rate": 10.0,  # Mbps
            "failed_transmissions": 2,
            "successful_transmissions": 150,
            "compression_enabled": True,
            "encryption_enabled": True,
            "transmission_protocol": "TCP",
            "retry_attempts": 3
        }
        
        # Storage performance
        self.storage_performance = {
            "average_read_speed": 360,  # MB/s
            "average_write_speed": 320,  # MB/s
            "io_operations_per_second": 1500,
            "queue_depth": 8,
            "latency": 0.5,  # ms
            "throughput": 25.0,  # MB/s
            "error_rate": 0.001,  # 0.1%
            "wear_leveling": 85.0  # %
        }
        
        # Data retention
        self.data_retention = {
            "retention_policy": "30_days",
            "auto_cleanup_enabled": True,
            "critical_data_protected": True,
            "archived_data_size": 200,  # GB
            "deleted_data_size": 50,  # GB
            "data_age_distribution": {
                "recent": 60,  # %
                "old": 30,  # %
                "archived": 10  # %
            }
        }
    
    async def generate_telemetry(self) -> TelemetryData:
        """Generate data storage telemetry data."""
        self._update_storage_devices()
        self._update_data_management()
        self._update_data_transmission()
        self._update_storage_performance()
        self._update_data_retention()
        
        data = {
            "storage_devices": self.storage_devices,
            "data_management": self.data_management,
            "data_transmission": self.data_transmission,
            "storage_performance": self.storage_performance,
            "data_retention": self.data_retention,
            "status": {
                "storage_healthy": self._is_storage_healthy(),
                "storage_capacity": self._get_storage_capacity(),
                "data_integrity": self._get_data_integrity(),
                "transmission_status": self._get_transmission_status()
            }
        }
        
        return TelemetryData(
            subsystem=self.subsystem_name,
            uav_id=self.uav_id,
            data=data,
            status=self.status
        )
    
    async def apply_fault(self, telemetry_data: TelemetryData, fault_params: Dict[str, Any]) -> TelemetryData:
        """Apply data storage fault."""
        fault_type = fault_params.get("type", "storage_failure")
        
        if fault_type == "storage_failure":
            # Simulate storage device failure
            device = fault_params.get("device", "primary_ssd")
            if device in telemetry_data.data["storage_devices"]:
                telemetry_data.data["storage_devices"][device]["status"] = "failed"
                telemetry_data.data["storage_devices"][device]["health"] = 0.0
                telemetry_data.data["storage_devices"][device]["read_speed"] = 0
                telemetry_data.data["storage_devices"][device]["write_speed"] = 0
                
        elif fault_type == "data_corruption":
            # Simulate data corruption
            telemetry_data.data["data_management"]["data_integrity_check"] = False
            telemetry_data.data["storage_performance"]["error_rate"] = 0.1
            
        elif fault_type == "transmission_failure":
            # Simulate transmission failure
            telemetry_data.data["data_transmission"]["failed_transmissions"] += 10
            telemetry_data.data["data_transmission"]["transmission_rate"] = 0.0
            
        elif fault_type == "encryption_failure":
            # Simulate encryption failure
            telemetry_data.data["data_management"]["encryption_enabled"] = False
            telemetry_data.data["data_transmission"]["encryption_enabled"] = False
            
        elif fault_type == "backup_failure":
            # Simulate backup failure
            telemetry_data.data["data_management"]["backup_enabled"] = False
            telemetry_data.data["data_management"]["last_backup"] = None
            
        elif fault_type == "capacity_exhaustion":
            # Simulate capacity exhaustion
            for device in telemetry_data.data["storage_devices"].values():
                device["available"] = 0.1
                device["used"] = device["capacity"] - 0.1
                
        elif fault_type == "performance_degradation":
            # Simulate performance degradation
            degradation_factor = fault_params.get("degradation_factor", 0.5)
            telemetry_data.data["storage_performance"]["average_read_speed"] *= (1 - degradation_factor)
            telemetry_data.data["storage_performance"]["average_write_speed"] *= (1 - degradation_factor)
            telemetry_data.data["storage_performance"]["latency"] *= (1 + degradation_factor)
        
        telemetry_data.status = SystemStatus.ERROR
        return telemetry_data
    
    def _update_storage_devices(self) -> None:
        """Update storage device data."""
        for device_name, device in self.storage_devices.items():
            # Simulate data usage changes
            device["used"] += random.uniform(-0.1, 0.5)
            device["used"] = max(0, min(device["capacity"], device["used"]))
            device["available"] = device["capacity"] - device["used"]
            
            # Simulate temperature changes
            device["temperature"] += random.uniform(-1, 1)
            device["temperature"] = max(20, min(70, device["temperature"]))
            
            # Simulate health changes
            device["health"] += random.uniform(-0.1, 0.1)
            device["health"] = max(0, min(100, device["health"]))
            
            # Simulate speed variations
            device["read_speed"] += random.uniform(-10, 10)
            device["read_speed"] = max(0, min(600, device["read_speed"]))
            
            device["write_speed"] += random.uniform(-10, 10)
            device["write_speed"] = max(0, min(550, device["write_speed"]))
            
            # Update status based on health
            if device["health"] < 80:
                device["status"] = "warning"
            elif device["health"] < 50:
                device["status"] = "critical"
            else:
                device["status"] = "healthy"
            
            # Simulate external storage connection changes
            if device_name == "external_storage":
                if random.random() < 0.001:  # 0.1% chance
                    device["connected"] = not device["connected"]
    
    def _update_data_management(self) -> None:
        """Update data management data."""
        # Update total data stored
        total_used = sum(device["used"] for device in self.storage_devices.values())
        self.data_management["total_data_stored"] = total_used
        
        # Simulate compression ratio changes
        self.data_management["data_compression_ratio"] += random.uniform(-0.01, 0.01)
        self.data_management["data_compression_ratio"] = max(0.1, min(0.8, 
            self.data_management["data_compression_ratio"]))
        
        # Simulate backup frequency changes
        self.data_management["backup_frequency"] += random.uniform(-60, 60)
        self.data_management["backup_frequency"] = max(1800, min(7200, 
            self.data_management["backup_frequency"]))
        
        # Simulate occasional backup completion
        if random.random() < 0.01:  # 1% chance
            self.data_management["last_backup"] = datetime.now()
        
        # Simulate occasional integrity check completion
        if random.random() < 0.005:  # 0.5% chance
            self.data_management["last_integrity_check"] = datetime.now()
    
    def _update_data_transmission(self) -> None:
        """Update data transmission data."""
        # Simulate transmission queue changes
        self.data_transmission["transmission_queue_size"] += random.uniform(-2, 5)
        self.data_transmission["transmission_queue_size"] = max(0, min(200, 
            self.data_transmission["transmission_queue_size"]))
        
        # Simulate transmission rate changes
        self.data_transmission["transmission_rate"] += random.uniform(-1, 1)
        self.data_transmission["transmission_rate"] = max(0, min(50, 
            self.data_transmission["transmission_rate"]))
        
        # Simulate transmission success/failure
        if random.random() < 0.01:  # 1% chance
            if random.random() < 0.9:  # 90% success rate
                self.data_transmission["successful_transmissions"] += 1
            else:
                self.data_transmission["failed_transmissions"] += 1
        
        # Simulate retry attempts
        if random.random() < 0.001:  # 0.1% chance
            self.data_transmission["retry_attempts"] += 1
            self.data_transmission["retry_attempts"] = min(5, 
                self.data_transmission["retry_attempts"])
    
    def _update_storage_performance(self) -> None:
        """Update storage performance data."""
        # Calculate average speeds from devices
        healthy_devices = [d for d in self.storage_devices.values() if d["status"] == "healthy"]
        if healthy_devices:
            self.storage_performance["average_read_speed"] = sum(
                d["read_speed"] for d in healthy_devices
            ) / len(healthy_devices)
            self.storage_performance["average_write_speed"] = sum(
                d["write_speed"] for d in healthy_devices
            ) / len(healthy_devices)
        
        # Simulate IO operations per second
        self.storage_performance["io_operations_per_second"] += random.uniform(-50, 50)
        self.storage_performance["io_operations_per_second"] = max(500, min(3000, 
            self.storage_performance["io_operations_per_second"]))
        
        # Simulate queue depth
        self.storage_performance["queue_depth"] += random.uniform(-1, 1)
        self.storage_performance["queue_depth"] = max(1, min(16, 
            self.storage_performance["queue_depth"]))
        
        # Simulate latency
        self.storage_performance["latency"] += random.uniform(-0.1, 0.1)
        self.storage_performance["latency"] = max(0.1, min(10, 
            self.storage_performance["latency"]))
        
        # Simulate throughput
        self.storage_performance["throughput"] += random.uniform(-2, 2)
        self.storage_performance["throughput"] = max(5, min(100, 
            self.storage_performance["throughput"]))
        
        # Simulate error rate
        self.storage_performance["error_rate"] += random.uniform(-0.0001, 0.0001)
        self.storage_performance["error_rate"] = max(0, min(0.1, 
            self.storage_performance["error_rate"]))
        
        # Simulate wear leveling
        self.storage_performance["wear_leveling"] += random.uniform(-0.5, 0.5)
        self.storage_performance["wear_leveling"] = max(0, min(100, 
            self.storage_performance["wear_leveling"]))
    
    def _update_data_retention(self) -> None:
        """Update data retention data."""
        # Simulate archived data size changes
        self.data_retention["archived_data_size"] += random.uniform(-1, 2)
        self.data_retention["archived_data_size"] = max(0, min(500, 
            self.data_retention["archived_data_size"]))
        
        # Simulate deleted data size changes
        self.data_retention["deleted_data_size"] += random.uniform(-0.5, 1)
        self.data_retention["deleted_data_size"] = max(0, min(100, 
            self.data_retention["deleted_data_size"]))
        
        # Simulate data age distribution changes
        for age_group in self.data_retention["data_age_distribution"]:
            self.data_retention["data_age_distribution"][age_group] += random.uniform(-1, 1)
            self.data_retention["data_age_distribution"][age_group] = max(0, min(100, 
                self.data_retention["data_age_distribution"][age_group]))
        
        # Normalize age distribution to sum to 100
        total = sum(self.data_retention["data_age_distribution"].values())
        if total > 0:
            for age_group in self.data_retention["data_age_distribution"]:
                self.data_retention["data_age_distribution"][age_group] = (
                    self.data_retention["data_age_distribution"][age_group] / total * 100
                )
    
    def _is_storage_healthy(self) -> bool:
        """Check if storage system is healthy."""
        return (
            all(device["status"] == "healthy" for device in self.storage_devices.values()) and
            self.data_management["data_integrity_check"] and
            self.storage_performance["error_rate"] < 0.01 and
            self.data_transmission["failed_transmissions"] < 10
        )
    
    def _get_storage_capacity(self) -> str:
        """Get storage capacity status."""
        total_capacity = sum(device["capacity"] for device in self.storage_devices.values())
        total_used = sum(device["used"] for device in self.storage_devices.values())
        usage_percentage = (total_used / total_capacity) * 100
        
        if usage_percentage > 90:
            return "critical"
        elif usage_percentage > 80:
            return "warning"
        elif usage_percentage > 60:
            return "moderate"
        else:
            return "good"
    
    def _get_data_integrity(self) -> str:
        """Get data integrity status."""
        if self.data_management["data_integrity_check"] and self.storage_performance["error_rate"] < 0.001:
            return "excellent"
        elif self.data_management["data_integrity_check"] and self.storage_performance["error_rate"] < 0.01:
            return "good"
        elif self.storage_performance["error_rate"] < 0.05:
            return "fair"
        else:
            return "poor"
    
    def _get_transmission_status(self) -> str:
        """Get transmission status."""
        success_rate = self.data_transmission["successful_transmissions"] / max(1, 
            self.data_transmission["successful_transmissions"] + self.data_transmission["failed_transmissions"])
        
        if success_rate > 0.95:
            return "excellent"
        elif success_rate > 0.90:
            return "good"
        elif success_rate > 0.80:
            return "fair"
        else:
            return "poor"
