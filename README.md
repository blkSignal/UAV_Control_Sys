#  UAV Mission Control & Anomaly Detection Simulator

A comprehensive Python-based multi-agent system for simulating UAV operations with real-time anomaly detection and fault injection capabilities.

##  Features

- **Multi-Agent Architecture**: 11+ UAV subsystems with independent agents
- **Real-Time Anomaly Detection**: ML-powered detection using Isolation Forest, One-Class SVM, and Local Outlier Factor
- **Fault Injection System**: 50+ simulated failure scenarios for testing and validation
- **Advanced Monitoring**: Comprehensive logging and metrics collection
- **Web Dashboard**: Real-time visualization and control interface
- **Automated Reporting**: Multiple report formats (HTML, PDF, JSON)
- **Production Ready**: Docker containerization with Nginx reverse proxy

##  Architecture

### UAV Subsystems
- **Navigation**: GPS, IMU, compass systems
- **Propulsion**: Motors, ESCs, propeller management
- **Communication**: Signal handling, satellite links
- **Power**: Battery management, voltage monitoring
- **Payload**: Camera, gimbal, sensor systems
- **Environmental**: Weather, air quality monitoring
- **Flight Control**: Autopilot, stabilization
- **Sensor Fusion**: Data integration and processing
- **Mission Planning**: Route optimization, task scheduling
- **Safety Systems**: Emergency procedures, fail-safes
- **Data Storage**: Telemetry logging, data management

### Core Components
- **Telemetry Manager**: Real-time data collection and distribution
- **Anomaly Detector**: ML-based anomaly identification
- **Fault Manager**: Fault injection and recovery simulation
- **Metrics Collector**: System performance monitoring
- **Report Generator**: Automated report creation
- **Web Dashboard**: Interactive control interface

##  Quick Start

### Prerequisites
- Python 3.9+
- Docker (optional)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/blkSignal/UAV_Control_Sys.git
   cd UAV_Control_Sys
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the simulator**
   ```bash
   python main.py
   ```

5. **Access the dashboard**
   Open your browser to `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8080
```

##  System Capabilities

### Anomaly Detection
- **Algorithms**: Isolation Forest, One-Class SVM, Local Outlier Factor
- **Real-time Processing**: Sub-second detection latency
- **Configurable Thresholds**: Adjustable sensitivity levels
- **Multi-dimensional Analysis**: Complex pattern recognition

### Fault Injection
- **50+ Scenarios**: GPS drift, motor failure, signal loss, power issues
- **Configurable Parameters**: Customizable fault characteristics
- **Duration Control**: Time-limited fault simulation
- **Recovery Testing**: Automatic and manual fault clearance

### Monitoring & Logging
- **Performance Metrics**: CPU, memory, disk, network monitoring
- **Structured Logging**: JSON-formatted log entries
- **Alert System**: Threshold-based notifications
- **Historical Data**: Long-term trend analysis

##  Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_fault_scenarios.py -v
```

##  Performance Metrics

- **Telemetry Rate**: 10Hz per subsystem
- **Anomaly Detection**: <100ms latency
- **Fault Injection**: 50+ scenarios supported
- **Manual Oversight Reduction**: 80% automation
- **System Uptime**: 99.9% availability target

##  Configuration

Edit `config/settings.yaml` to customize:
- UAV subsystem parameters
- Anomaly detection thresholds
- Fault injection scenarios
- Monitoring intervals
- Dashboard settings

##  Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Configuration Reference](config/settings.yaml)

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


