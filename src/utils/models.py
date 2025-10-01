"""Data models for UAV telemetry and system state."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class SeverityLevel(str, Enum):
    """Severity levels for alerts and faults."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SystemStatus(str, Enum):
    """System status enumeration."""
    NOMINAL = "nominal"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    OFFLINE = "offline"


class TelemetryData(BaseModel):
    """Base telemetry data model."""
    timestamp: datetime = Field(default_factory=datetime.now)
    subsystem: str
    uav_id: str
    data: Dict[str, Any]
    status: SystemStatus = SystemStatus.NOMINAL
    anomaly_score: Optional[float] = None


class Alert(BaseModel):
    """Alert model for system notifications."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    uav_id: str
    subsystem: str
    severity: SeverityLevel
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False


class FaultScenario(BaseModel):
    """Fault injection scenario model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subsystem: str
    probability: float = Field(ge=0.0, le=1.0)
    duration: int = Field(gt=0)  # seconds
    severity: SeverityLevel
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class PerformanceMetrics(BaseModel):
    """System performance metrics model."""
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_usage: float = Field(ge=0.0, le=100.0)
    memory_usage: float = Field(ge=0.0, le=100.0)
    disk_usage: float = Field(ge=0.0, le=100.0)
    network_latency: float = Field(ge=0.0)
    active_connections: int = Field(ge=0)
    error_rate: float = Field(ge=0.0, le=1.0)


class UAVState(BaseModel):
    """Complete UAV state model."""
    uav_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    subsystems: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    overall_status: SystemStatus = SystemStatus.NOMINAL
    position: Dict[str, float] = Field(default_factory=dict)  # lat, lon, alt
    mission_status: str = "idle"
    battery_level: float = Field(ge=0.0, le=100.0)
    flight_time: float = Field(ge=0.0)  # minutes


class AnomalyDetectionResult(BaseModel):
    """Anomaly detection result model."""
    timestamp: datetime = Field(default_factory=datetime.now)
    uav_id: str
    subsystem: str
    anomaly_score: float = Field(ge=0.0, le=1.0)
    is_anomaly: bool
    features: Dict[str, float]
    algorithm: str
    confidence: float = Field(ge=0.0, le=1.0)


class MissionData(BaseModel):
    """Mission data model."""
    mission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    waypoints: List[Dict[str, float]] = Field(default_factory=list)
    status: str = "planned"  # planned, active, completed, failed
    uav_ids: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
