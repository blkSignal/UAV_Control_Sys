# Contributing to UAV Mission Control & Anomaly Detection Simulator

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the UAV simulator.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature
4. Make your changes
5. Test your changes
6. Submit a pull request

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/UAV_Control_Sys.git
cd UAV_Control_Sys

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v
```

## 🧪 Testing

- All new features must include tests
- Run the full test suite before submitting
- Ensure all tests pass
- Add tests for new fault scenarios

## 📝 Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions focused and small

## 🔧 Areas for Contribution

- **New UAV Subsystems**: Add additional subsystem agents
- **Fault Scenarios**: Implement new fault injection scenarios
- **Anomaly Detection**: Improve ML algorithms and detection
- **Dashboard Features**: Enhance the web interface
- **Documentation**: Improve docs and examples
- **Performance**: Optimize system performance
- **Testing**: Add more comprehensive tests

## 📤 Submitting Changes

1. Ensure your code follows the style guidelines
2. Add tests for new functionality
3. Update documentation if needed
4. Commit with clear, descriptive messages
5. Push to your fork
6. Create a pull request with a detailed description

## 🐛 Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

## 📞 Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing! 🚁
