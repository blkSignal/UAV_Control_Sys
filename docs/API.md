# UAV Mission Control & Anomaly Detection Simulator API Documentation

## Overview

The UAV Mission Control & Anomaly Detection Simulator provides a comprehensive API for managing UAV subsystems, monitoring telemetry data, detecting anomalies, and injecting faults for testing purposes.

## Core Components

### 1. TelemetryManager

Manages multiple UAV agents and their telemetry data.

#### Methods

- `add_uav(uav_id: str, subsystems: Optional[List[str]] = None) -> None`
  - Add a UAV with its agents to the telemetry system
  - Parameters:
    - `uav_id`: Unique identifier for the UAV
    - `subsystems`: List of subsystem names to create (None for all)

- `remove_uav(uav_id: str) -> None`
  - Remove a UAV and its agents from the telemetry system

- `start() -> None`
  - Start the telemetry system

- `stop() -> None`
  - Stop the telemetry system

- `inject_fault(uav_id: str, subsystem: str, fault_params: Dict[str, Any]) -> None`
  - Inject a fault into a specific subsystem

- `clear_fault(uav_id: str, subsystem: str) -> None`
  - Clear a fault from a specific subsystem

### 2. AnomalyDetector

Real-time anomaly detection engine for UAV telemetry data.

#### Methods

- `process_telemetry(telemetry_data: TelemetryData) -> AnomalyDetectionResult`
  - Process telemetry data for anomaly detection

- `register_anomaly_callback(callback: Callable) -> None`
  - Register a callback for anomaly alerts

- `get_statistics() -> Dict[str, Any]`
  - Get anomaly detection statistics

- `update_configuration(config_updates: Dict[str, Any]) -> None`
  - Update anomaly detection configuration

### 3. FaultManager

Manages fault injection and failure simulation.

#### Methods

- `inject_fault(uav_id: str, subsystem: str, fault_type: str, parameters: Optional[Dict[str, Any]] = None, duration: Optional[int] = None) -> bool`
  - Inject a specific fault

- `clear_fault(uav_id: str, subsystem: str, fault_type: str) -> bool`
  - Clear a specific fault

- `clear_all_faults() -> None`
  - Clear all active faults

- `get_active_faults() -> Dict[str, Dict[str, Any]]`
  - Get all active faults

- `get_statistics() -> Dict[str, Any]`
  - Get fault injection statistics

### 4. MetricsCollector

Collects and monitors system performance metrics.

#### Methods

- `start() -> None`
  - Start metrics collection

- `stop() -> None`
  - Stop metrics collection

- `get_current_metrics() -> Optional[PerformanceMetrics]`
  - Get the most recent metrics

- `get_metrics_history(limit: Optional[int] = None) -> List[PerformanceMetrics]`
  - Get metrics history

- `get_statistics() -> Dict[str, Any]`
  - Get metrics collection statistics

### 5. ReportGenerator

Automated report generator for the UAV simulator.

#### Methods

- `generate_system_status_report(format: str = None) -> str`
  - Generate system status report

- `generate_anomaly_report(format: str = None) -> str`
  - Generate anomaly detection report

- `generate_fault_report(format: str = None) -> str`
  - Generate fault injection report

- `generate_performance_report(format: str = None) -> str`
  - Generate performance metrics report

- `generate_comprehensive_report(format: str = None) -> str`
  - Generate comprehensive system report

## Data Models

### TelemetryData

```python
class TelemetryData(BaseModel):
    timestamp: datetime
    subsystem: str
    uav_id: str
    data: Dict[str, Any]
    status: SystemStatus
    anomaly_score: Optional[float] = None
```

### Alert

```python
class Alert(BaseModel):
    id: str
    timestamp: datetime
    uav_id: str
    subsystem: str
    severity: SeverityLevel
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
```

### AnomalyDetectionResult

```python
class AnomalyDetectionResult(BaseModel):
    timestamp: datetime
    uav_id: str
    subsystem: str
    anomaly_score: float
    is_anomaly: bool
    features: Dict[str, float]
    algorithm: str
    confidence: float
```

### FaultScenario

```python
class FaultScenario(BaseModel):
    id: str
    name: str
    subsystem: str
    probability: float
    duration: int
    severity: SeverityLevel
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
```

## Configuration

The system uses YAML configuration files located in the `config/` directory.

### Main Configuration (`config/settings.yaml`)

```yaml
system:
  name: "UAV Mission Control Simulator"
  version: "1.0.0"
  debug: false
  simulation_speed: 1.0

uav:
  count: 5
  subsystems:
    - name: "Navigation"
      agent_class: "NavigationAgent"
      telemetry_rate: 10
      critical: true

anomaly_detection:
  enabled: true
  algorithm: "isolation_forest"
  threshold: 0.8
  window_size: 100

fault_injection:
  enabled: true
  max_concurrent_faults: 3
  scenarios:
    - name: "Power_Failure"
      subsystem: "Power"
      probability: 0.1
      duration: 30
      severity: "critical"

monitoring:
  log_level: "INFO"
  log_file: "logs/uav_simulator.log"
  metrics_retention: 86400
```

## Usage Examples

### Basic Usage

```python
import asyncio
from main import UAVSimulator

async def main():
    # Create simulator
    simulator = UAVSimulator()
    
    # Start simulator
    await simulator.start()
    
    # Inject a fault
    await simulator.inject_fault("UAV_001", "Navigation", "gps_drift", {"drift_factor": 0.1})
    
    # Get status
    status = simulator.get_status()
    print(f"Active UAVs: {status['uav_count']}")
    
    # Stop simulator
    await simulator.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Anomaly Detection

```python
from src.anomaly.anomaly_detector import AnomalyDetector
from src.utils.models import TelemetryData

async def detect_anomalies():
    detector = AnomalyDetector()
    
    # Process telemetry data
    telemetry = TelemetryData(
        uav_id="UAV_001",
        subsystem="Navigation",
        data={"altitude": 100, "speed": 15},
        status="nominal"
    )
    
    result = await detector.process_telemetry(telemetry)
    
    if result.is_anomaly:
        print(f"Anomaly detected! Score: {result.anomaly_score}")
```

### Fault Injection

```python
from src.fault_injection.fault_manager import FaultManager, FaultType

async def inject_faults():
    manager = FaultManager()
    await manager.start()
    
    # Inject various faults
    await manager.inject_fault("UAV_001", "Power", FaultType.BATTERY_FAILURE)
    await manager.inject_fault("UAV_001", "Propulsion", FaultType.MOTOR_FAILURE)
    
    # Get active faults
    active_faults = manager.get_active_faults()
    print(f"Active faults: {len(active_faults)}")
    
    await manager.stop()
```

### Report Generation

```python
from src.reporting.report_generator import ReportGenerator

async def generate_reports():
    generator = ReportGenerator()
    
    # Generate different types of reports
    system_report = await generator.generate_system_status_report("html")
    anomaly_report = await generator.generate_anomaly_report("json")
    fault_report = await generator.generate_fault_report("csv")
    
    print(f"Reports generated: {system_report}, {anomaly_report}, {fault_report}")
```

## Error Handling

The API uses standard Python exceptions and async error handling:

- `ValueError`: Invalid parameters or configuration
- `RuntimeError`: System state errors
- `asyncio.CancelledError`: Operation cancellation
- `Exception`: General errors with detailed logging

## Logging

The system uses structured logging with different levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors

Logs are written to:
- Console (colored output)
- `logs/uav_simulator.log` (main log)
- `logs/errors.log` (error log)
- `logs/performance.log` (performance metrics)

## Performance Considerations

- Telemetry data is processed asynchronously
- Anomaly detection uses efficient ML algorithms
- Fault injection has configurable limits
- Metrics collection has minimal overhead
- Reports are generated on-demand

## Security

- All data is processed locally
- No external network dependencies
- Configurable encryption for sensitive data
- Audit logging for all operations
