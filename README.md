# UAV Mission Control & Anomaly Detection Simulator

A comprehensive Python-based multi-agent telemetry dashboard simulating 10+ UAV subsystems with real-time anomaly detection, fault injection, and automated monitoring capabilities.

## Features

- **Multi-Agent Architecture**: Simulates 10+ UAV subsystems with independent telemetry agents
- **Real-Time Anomaly Detection**: Advanced ML-based anomaly detection with configurable thresholds
- **Fault Injection System**: Validates 50+ simulated failure scenarios for system reliability testing
- **Automated Monitoring**: Reduces manual oversight by 80% with comprehensive logging and reporting
- **Web Dashboard**: Real-time visualization of UAV status, telemetry data, and alerts
- **Performance Metrics**: End-to-end system verification with automated reporting

## Project Structure

```
UAV_Control_Sys/
├── src/
│   ├── agents/           # UAV subsystem agents
│   ├── anomaly/          # Anomaly detection engine
│   ├── dashboard/        # Web dashboard components
│   ├── fault_injection/  # Fault simulation system
│   ├── monitoring/       # Logging and monitoring
│   └── utils/           # Shared utilities
├── tests/               # Test suite for failure scenarios
├── config/              # Configuration files
├── data/               # Sample data and logs
└── docs/               # Documentation
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulator:
```bash
python main.py
```

3. Access the dashboard at: http://localhost:8000

## Configuration

Edit `config/settings.yaml` to customize:
- UAV subsystem parameters
- Anomaly detection thresholds
- Fault injection scenarios
- Monitoring intervals

## Testing

Run the comprehensive test suite:
```bash
pytest tests/ -v
```

## License

MIT License - See LICENSE file for details
