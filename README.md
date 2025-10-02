# 🚁 UAV Mission Control & Anomaly Detection Simulator

A comprehensive Python-based multi-agent system for simulating UAV operations with real-time anomaly detection and fault injection capabilities.

## 🌟 Features

- **Multi-Agent Architecture**: 11+ UAV subsystems with independent agents
- **Real-Time Anomaly Detection**: ML-powered detection using Isolation Forest, One-Class SVM, and Local Outlier Factor
- **Fault Injection System**: 50+ simulated failure scenarios for testing and validation
- **Advanced Monitoring**: Comprehensive logging and metrics collection
- **Web Dashboard**: Real-time visualization and control interface
- **Automated Reporting**: Multiple report formats (HTML, PDF, JSON)
- **Production Ready**: Docker containerization with Nginx reverse proxy

## 🏗️ System Architecture

### Multi-Agent UAV Subsystem Architecture
The system implements a distributed multi-agent architecture where each UAV subsystem operates as an independent agent with specialized responsibilities:

#### Core UAV Subsystems
- **🧭 Navigation Agent**: GPS, IMU, compass systems with Kalman filtering
- **⚡ Propulsion Agent**: Motor control, ESC management, propeller optimization
- **📡 Communication Agent**: Signal processing, satellite links, mesh networking
- **🔋 Power Agent**: Battery management, voltage monitoring, power optimization
- **📷 Payload Agent**: Camera control, gimbal stabilization, sensor integration
- **🌡️ Environmental Agent**: Weather monitoring, air quality assessment
- **✈️ Flight Control Agent**: Autopilot algorithms, stabilization systems
- **🔄 Sensor Fusion Agent**: Multi-sensor data integration and processing
- **🗺️ Mission Planning Agent**: Route optimization, task scheduling, pathfinding
- **🛡️ Safety Agent**: Emergency procedures, fail-safe mechanisms
- **💾 Data Storage Agent**: Telemetry logging, data management, archival

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    UAV Mission Control System                   │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard (React)  │  API Gateway  │  Real-time Monitor    │
├─────────────────────────────────────────────────────────────────┤
│              Telemetry Manager (Central Hub)                    │
├─────────────────────────────────────────────────────────────────┤
│  Navigation │ Propulsion │ Communication │ Power │ Payload      │
│  Agent      │ Agent      │ Agent         │ Agent │ Agent        │
├─────────────────────────────────────────────────────────────────┤
│  Environmental │ Flight Control │ Sensor Fusion │ Mission       │
│  Agent         │ Agent          │ Agent         │ Planning      │
├─────────────────────────────────────────────────────────────────┤
│  Safety Agent  │ Data Storage Agent │ Anomaly Detector         │
├─────────────────────────────────────────────────────────────────┤
│              Fault Manager │ Metrics Collector │ Report Gen     │
└─────────────────────────────────────────────────────────────────┘
```

### Core System Components

#### 🎯 Telemetry Manager
- **Real-time Data Collection**: 10Hz sampling rate per subsystem
- **Data Distribution**: Pub/Sub messaging with ZeroMQ
- **Data Validation**: Multi-layer validation and quality assessment
- **Message Queuing**: Apache Kafka for reliable message delivery

#### 🔍 Anomaly Detector
- **ML Algorithms**: Isolation Forest, One-Class SVM, Local Outlier Factor
- **Real-time Processing**: Sub-100ms detection latency
- **Multi-dimensional Analysis**: Complex pattern recognition across 50+ metrics
- **Adaptive Thresholds**: Dynamic sensitivity adjustment based on mission phase

#### ⚠️ Fault Manager
- **Fault Injection**: 50+ pre-configured failure scenarios
- **Recovery Simulation**: Automatic and manual fault clearance procedures
- **Scenario Testing**: Configurable fault characteristics and duration
- **Impact Assessment**: System-wide failure impact analysis

#### 📊 Metrics Collector
- **Performance Monitoring**: CPU, memory, disk, network utilization
- **System Health**: Component status and operational metrics
- **Alert System**: Threshold-based notifications and escalation
- **Historical Analysis**: Long-term trend analysis and reporting

#### 📋 Report Generator
- **Automated Reports**: HTML, PDF, JSON format generation
- **Custom Templates**: Configurable report layouts and content
- **Scheduled Generation**: Time-based and event-triggered reports
- **Data Export**: CSV, JSON, and database export capabilities

#### 🖥️ Web Dashboard
- **Real-time Visualization**: Live telemetry data display
- **Interactive Controls**: Mission control and system configuration
- **Multi-user Support**: Role-based access control and permissions
- **Responsive Design**: Mobile and desktop compatibility

## 🛠️ Technology Stack

### Backend Technologies
- **Core Language**: Python 3.9+ with asyncio for concurrent processing
- **Web Framework**: FastAPI for high-performance API endpoints
- **Message Queue**: Apache Kafka for reliable telemetry distribution
- **Real-time Communication**: ZeroMQ for low-latency inter-agent communication
- **Database**: PostgreSQL for persistent data, Redis for caching
- **ML Libraries**: scikit-learn, pandas, numpy for anomaly detection
- **Data Processing**: Apache Spark for large-scale telemetry analysis

### Frontend Technologies
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit for complex state handling
- **Real-time Updates**: WebSocket connections for live data streaming
- **Visualization**: D3.js and Chart.js for interactive dashboards
- **UI Components**: Material-UI for consistent design system
- **Build Tools**: Vite for fast development and optimized builds

### Infrastructure & DevOps
- **Containerization**: Docker and Docker Compose for deployment
- **Reverse Proxy**: Nginx for load balancing and SSL termination
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Monitoring**: Prometheus and Grafana for system metrics
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Security**: OAuth 2.0, JWT tokens, HTTPS encryption

### Development Tools
- **Testing**: pytest, Jest, Cypress for comprehensive testing
- **Code Quality**: Black, flake8, ESLint, Prettier
- **Documentation**: Sphinx for API docs, MkDocs for user guides
- **Version Control**: Git with conventional commit messages
- **Package Management**: Poetry for Python dependencies, npm for frontend

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.9+ with pip and virtual environment support
- **Node.js**: 16+ with npm for frontend development
- **Docker**: 20+ with Docker Compose for containerized deployment
- **Git**: Latest version for version control
- **Memory**: Minimum 8GB RAM for full system operation
- **Storage**: 10GB free space for dependencies and data

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

## 📊 System Capabilities

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

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite
The system includes a multi-layered testing approach ensuring reliability and performance:

```bash
# Run complete test suite
python -m pytest tests/ -v --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/unit/ -v                    # Unit tests
python -m pytest tests/integration/ -v              # Integration tests
python -m pytest tests/test_fault_scenarios.py -v   # Fault injection tests
python -m pytest tests/test_anomaly_detection.py -v # ML algorithm tests
python -m pytest tests/test_performance.py -v      # Performance benchmarks

# Frontend testing
npm test                                             # Jest unit tests
npm run test:e2e                                     # Cypress end-to-end tests
npm run test:coverage                                # Coverage reports
```

### Test Categories

#### 🔬 Unit Tests
- **Agent Testing**: Individual subsystem agent functionality
- **Algorithm Testing**: ML anomaly detection algorithm validation
- **Data Processing**: Telemetry data validation and transformation
- **API Endpoints**: REST API endpoint functionality and error handling

#### 🔗 Integration Tests
- **Multi-Agent Communication**: Inter-agent message passing and coordination
- **Database Integration**: Data persistence and retrieval operations
- **Real-time Processing**: End-to-end telemetry processing pipeline
- **Fault Recovery**: System behavior during fault injection scenarios

#### ⚡ Performance Tests
- **Latency Benchmarks**: Sub-100ms anomaly detection validation
- **Throughput Testing**: 10Hz telemetry processing capacity
- **Memory Usage**: Resource consumption under various load conditions
- **Scalability**: System performance with increasing agent count

#### 🛡️ Security Tests
- **Authentication**: User authentication and authorization
- **Data Encryption**: Secure data transmission and storage
- **Input Validation**: Malicious input handling and sanitization
- **Access Control**: Role-based permission enforcement

### Test Coverage Requirements
- **Minimum Coverage**: 90% code coverage across all modules
- **Critical Paths**: 100% coverage for fault detection and recovery
- **Performance Baselines**: All performance metrics must meet specifications
- **Security Validation**: Complete security test suite execution

## 📈 Performance Metrics

- **Telemetry Rate**: 10Hz per subsystem
- **Anomaly Detection**: <100ms latency
- **Fault Injection**: 50+ scenarios supported
- **Manual Oversight Reduction**: 80% automation
- **System Uptime**: 99.9% availability target

## 🔧 Configuration

Edit `config/settings.yaml` to customize:
- UAV subsystem parameters
- Anomaly detection thresholds
- Fault injection scenarios
- Monitoring intervals
- Dashboard settings

## 📚 Documentation & API Reference

### Core API Endpoints

#### Telemetry Management
```http
GET    /api/v1/telemetry/streams          # Get active telemetry streams
POST   /api/v1/telemetry/start            # Start telemetry collection
POST   /api/v1/telemetry/stop             # Stop telemetry collection
GET    /api/v1/telemetry/data/{agent_id}  # Get agent-specific telemetry data
```

#### Anomaly Detection
```http
GET    /api/v1/anomalies/detected         # Get detected anomalies
POST   /api/v1/anomalies/configure        # Configure detection parameters
GET    /api/v1/anomalies/history          # Get anomaly history
POST   /api/v1/anomalies/acknowledge      # Acknowledge anomaly
```

#### Fault Management
```http
GET    /api/v1/faults/scenarios           # Get available fault scenarios
POST   /api/v1/faults/inject             # Inject fault scenario
POST   /api/v1/faults/clear              # Clear active faults
GET    /api/v1/faults/status             # Get fault injection status
```

#### System Control
```http
GET    /api/v1/system/status             # Get system health status
POST   /api/v1/system/agents/start       # Start specific agent
POST   /api/v1/system/agents/stop        # Stop specific agent
GET    /api/v1/system/metrics            # Get system performance metrics
```

#### Mission Management
```http
GET    /api/v1/missions/active           # Get active missions
POST   /api/v1/missions/create          # Create new mission
POST   /api/v1/missions/update          # Update mission parameters
POST   /api/v1/missions/execute         # Execute mission plan
```

### WebSocket Real-time Updates
```javascript
// Connect to real-time telemetry stream
const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Handle real-time telemetry data
    updateDashboard(data);
};

// Subscribe to anomaly alerts
const anomalyWs = new WebSocket('ws://localhost:8000/ws/anomalies');
anomalyWs.onmessage = function(event) {
    const anomaly = JSON.parse(event.data);
    // Handle anomaly alerts
    showAnomalyAlert(anomaly);
};
```

### Data Models

#### Telemetry Data Structure
```json
{
    "agent_id": "navigation_agent_001",
    "timestamp": "2024-01-15T10:30:45.123Z",
    "data": {
        "gps": {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "altitude": 150.5,
            "accuracy": 2.1
        },
        "imu": {
            "acceleration": [0.1, -0.2, 9.8],
            "angular_velocity": [0.05, -0.03, 0.01],
            "temperature": 25.3
        }
    },
    "quality_score": 0.95,
    "status": "healthy"
}
```

#### Anomaly Detection Result
```json
{
    "anomaly_id": "anom_20240115_103045_001",
    "timestamp": "2024-01-15T10:30:45.123Z",
    "agent_id": "navigation_agent_001",
    "anomaly_type": "position_drift",
    "severity": "medium",
    "confidence": 0.87,
    "description": "GPS position showing unexpected drift pattern",
    "recommended_action": "verify_gps_signal_quality"
}
```

### Documentation Links
- [Complete API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Configuration Reference](config/settings.yaml)
- [Agent Development Guide](docs/AGENT_DEVELOPMENT.md)
- [Fault Scenario Library](docs/FAULT_SCENARIOS.md)
- [Performance Tuning Guide](docs/PERFORMANCE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Achievements

- ✅ **Multi-agent telemetry system** with 11+ UAV subsystems
- ✅ **Real-time anomaly detection** with ML algorithms
- ✅ **Comprehensive fault injection** with 50+ scenarios
- ✅ **Advanced monitoring** with 80% manual oversight reduction
- ✅ **Web-based dashboard** for real-time visualization
- ✅ **Automated reporting** in multiple formats
- ✅ **Production-ready deployment** with Docker and Nginx

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation
- Review the test cases for examples

---

**Built with ❤️ for UAV mission control and anomaly detection**