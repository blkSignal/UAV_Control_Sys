#!/bin/bash

# UAV Mission Control & Anomaly Detection Simulator Setup Script

set -e

echo "🚁 Setting up UAV Mission Control & Anomaly Detection Simulator..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data reports templates config ssl

# Set up configuration
if [ ! -f "config/settings.yaml" ]; then
    echo "⚙️ Configuration file already exists"
else
    echo "⚙️ Configuration file found"
fi

# Set up environment file
if [ ! -f ".env" ]; then
    echo "🔐 Creating environment file..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Set up SSL certificates (self-signed for development)
if [ ! -f "ssl/cert.pem" ]; then
    echo "🔒 Generating self-signed SSL certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=CA/L=Los Angeles/O=UAV Simulator/CN=localhost"
fi

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh
chmod 600 ssl/*.pem

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v --tb=short

echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the simulator:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "🌐 To start with Docker:"
echo "   docker-compose up -d"
echo ""
echo "📊 Dashboard will be available at: http://localhost:8050"
echo "🔌 API will be available at: http://localhost:8000"
echo ""
echo "📖 For more information, see the documentation in docs/"
