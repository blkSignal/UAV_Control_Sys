# Deployment Guide

## Overview

This guide covers deployment options for the UAV Mission Control & Anomaly Detection Simulator, including local development, Docker deployment, and production configurations.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Git
- 4GB RAM minimum (8GB recommended)
- 10GB disk space

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd UAV_Control_Sys
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Start Simulator

```bash
python main.py
```

### 5. Access Services

- **Dashboard**: http://localhost:8050
- **API**: http://localhost:8000
- **Logs**: `logs/` directory

## Docker Deployment

### 1. Build and Start Services

```bash
docker-compose up -d
```

### 2. View Logs

```bash
docker-compose logs -f uav-simulator
```

### 3. Stop Services

```bash
docker-compose down
```

### 4. Rebuild After Changes

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### 1. Environment Configuration

Create production environment file:

```bash
cp env.example .env.production
```

Edit `.env.production`:

```env
# Production Configuration
DATABASE_URL=postgresql://user:password@db-host:5432/uav_simulator
REDIS_URL=redis://redis-host:6379
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-production-secret-key
LOG_LEVEL=WARNING
MONITORING_INTERVAL=5.0
ANOMALY_THRESHOLD=0.8
NUM_UAVS=10
SIMULATION_SPEED=1.0
```

### 2. SSL Configuration

For HTTPS deployment:

```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=CA/L=Los Angeles/O=UAV Simulator/CN=your-domain.com"
```

### 3. Database Setup

#### PostgreSQL

```sql
CREATE DATABASE uav_simulator;
CREATE USER uav_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE uav_simulator TO uav_user;
```

#### Redis

```bash
# Configure Redis for production
redis-server --port 6379 --requirepass your_redis_password
```

### 4. Nginx Configuration

Update `nginx.conf` for production:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://uav-simulator:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Systemd Service (Linux)

Create `/etc/systemd/system/uav-simulator.service`:

```ini
[Unit]
Description=UAV Mission Control Simulator
After=network.target

[Service]
Type=simple
User=uav
WorkingDirectory=/opt/uav-simulator
Environment=PATH=/opt/uav-simulator/venv/bin
ExecStart=/opt/uav-simulator/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable uav-simulator
sudo systemctl start uav-simulator
sudo systemctl status uav-simulator
```

## Monitoring and Logging

### 1. Log Management

Logs are stored in the `logs/` directory:

- `uav_simulator.log` - Main application log
- `errors.log` - Error log
- `performance.log` - Performance metrics

### 2. Log Rotation

Configure logrotate:

```bash
# /etc/logrotate.d/uav-simulator
/opt/uav-simulator/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 uav uav
    postrotate
        systemctl reload uav-simulator
    endscript
}
```

### 3. Monitoring

#### Prometheus Metrics

The simulator exposes metrics at `/metrics` endpoint for Prometheus monitoring.

#### Health Checks

Health check endpoint: `GET /health`

Response:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "uptime": 3600
}
```

## Scaling

### Horizontal Scaling

For high-load scenarios:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Instances**: Run multiple simulator instances
3. **Database Clustering**: PostgreSQL cluster with read replicas
4. **Redis Cluster**: Redis cluster for session management

### Vertical Scaling

1. **CPU**: Increase CPU cores for more UAVs
2. **Memory**: Increase RAM for larger data sets
3. **Storage**: SSD storage for better I/O performance

## Security Considerations

### 1. Network Security

- Use HTTPS in production
- Implement rate limiting
- Configure firewall rules
- Use VPN for remote access

### 2. Application Security

- Regular security updates
- Secure configuration management
- Input validation and sanitization
- Audit logging

### 3. Data Security

- Encrypt sensitive data
- Secure database connections
- Regular backups
- Access control

## Backup and Recovery

### 1. Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U uav_user uav_simulator > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U uav_user uav_simulator < backup_20240101.sql
```

### 2. Configuration Backup

```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/
```

### 3. Automated Backups

Create backup script:

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/opt/backups/uav-simulator"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U uav_user uav_simulator > $BACKUP_DIR/db_$DATE.sql

# Configuration backup
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Log backup
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Schedule with cron:

```bash
# Add to crontab
0 2 * * * /opt/uav-simulator/scripts/backup.sh
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   ```

2. **Permission Issues**
   ```bash
   # Fix permissions
   chown -R uav:uav /opt/uav-simulator
   chmod +x scripts/*.sh
   ```

3. **Database Connection**
   ```bash
   # Test database connection
   psql -h localhost -U uav_user -d uav_simulator -c "SELECT 1;"
   ```

4. **Memory Issues**
   ```bash
   # Monitor memory usage
   free -h
   ps aux --sort=-%mem | head
   ```

### Log Analysis

```bash
# View recent errors
tail -f logs/errors.log

# Search for specific patterns
grep "ERROR" logs/uav_simulator.log

# Analyze performance
grep "PERFORMANCE" logs/performance.log
```

## Performance Tuning

### 1. System Optimization

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
sysctl -p
```

### 2. Application Optimization

- Adjust telemetry rates in configuration
- Optimize anomaly detection algorithms
- Use connection pooling for databases
- Implement caching strategies

### 3. Database Optimization

```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
SELECT pg_reload_conf();
```

## Maintenance

### Regular Tasks

1. **Weekly**: Review logs and performance metrics
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and update configuration
4. **Annually**: Full system audit and capacity planning

### Update Procedure

1. Backup current system
2. Test updates in staging environment
3. Deploy updates during maintenance window
4. Verify functionality
5. Monitor for issues

This deployment guide provides comprehensive instructions for deploying the UAV Mission Control & Anomaly Detection Simulator in various environments. Follow the appropriate section based on your deployment needs.
