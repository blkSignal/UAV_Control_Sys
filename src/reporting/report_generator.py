"""Automated reporting system for UAV Mission Control & Anomaly Detection Simulator."""

import asyncio
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from jinja2 import Template
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from loguru import logger

from ..utils.config import config
from ..utils.models import TelemetryData, Alert, SeverityLevel


class ReportGenerator:
    """Automated report generator for UAV simulator."""
    
    def __init__(self):
        """Initialize report generator."""
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Report templates
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.telemetry_data: List[Dict] = []
        self.anomaly_data: List[Dict] = []
        self.fault_data: List[Dict] = []
        self.alert_data: List[Dict] = []
        self.performance_data: List[Dict] = []
        
        # Report configuration
        self.report_formats = ["html", "json", "csv", "pdf"]
        self.default_format = "html"
        
        logger.info("ReportGenerator initialized")
    
    def add_telemetry_data(self, telemetry_data: TelemetryData) -> None:
        """Add telemetry data for reporting.
        
        Args:
            telemetry_data: Telemetry data to add
        """
        data_point = {
            "timestamp": telemetry_data.timestamp.isoformat(),
            "uav_id": telemetry_data.uav_id,
            "subsystem": telemetry_data.subsystem,
            "status": telemetry_data.status.value,
            "anomaly_score": telemetry_data.anomaly_score,
            "data": telemetry_data.data
        }
        self.telemetry_data.append(data_point)
    
    def add_anomaly_data(self, uav_id: str, subsystem: str, anomaly_score: float, 
                        features: Dict[str, Any], timestamp: datetime = None) -> None:
        """Add anomaly detection data for reporting.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            anomaly_score: Anomaly score
            features: Features used for detection
            timestamp: Detection timestamp
        """
        data_point = {
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "uav_id": uav_id,
            "subsystem": subsystem,
            "anomaly_score": anomaly_score,
            "features": features
        }
        self.anomaly_data.append(data_point)
    
    def add_fault_data(self, uav_id: str, subsystem: str, fault_type: str, 
                      parameters: Dict[str, Any], timestamp: datetime = None) -> None:
        """Add fault injection data for reporting.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            fault_type: Type of fault
            parameters: Fault parameters
            timestamp: Injection timestamp
        """
        data_point = {
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "uav_id": uav_id,
            "subsystem": subsystem,
            "fault_type": fault_type,
            "parameters": parameters
        }
        self.fault_data.append(data_point)
    
    def add_alert_data(self, alert: Alert) -> None:
        """Add alert data for reporting.
        
        Args:
            alert: Alert to add
        """
        data_point = {
            "timestamp": alert.timestamp.isoformat(),
            "uav_id": alert.uav_id,
            "subsystem": alert.subsystem,
            "severity": alert.severity.value,
            "message": alert.message,
            "data": alert.data,
            "acknowledged": alert.acknowledged,
            "resolved": alert.resolved
        }
        self.alert_data.append(data_point)
    
    def add_performance_data(self, metrics) -> None:
        """Add performance metrics for reporting.
        
        Args:
            metrics: Performance metrics
        """
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "disk_usage": metrics.disk_usage,
            "network_latency": metrics.network_latency,
            "active_connections": metrics.active_connections,
            "error_rate": metrics.error_rate
        }
        self.performance_data.append(data_point)
    
    async def generate_system_status_report(self, format: str = None) -> str:
        """Generate system status report.
        
        Args:
            format: Report format (html, json, csv, pdf)
            
        Returns:
            Path to generated report file
        """
        format = format or self.default_format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_status_report_{timestamp}.{format}"
        filepath = self.reports_dir / filename
        
        # Generate report data
        report_data = await self._generate_system_status_data()
        
        if format == "html":
            await self._generate_html_report(report_data, filepath)
        elif format == "json":
            await self._generate_json_report(report_data, filepath)
        elif format == "csv":
            await self._generate_csv_report(report_data, filepath)
        elif format == "pdf":
            await self._generate_pdf_report(report_data, filepath)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        logger.info(f"Generated system status report: {filepath}")
        return str(filepath)
    
    async def generate_anomaly_report(self, format: str = None) -> str:
        """Generate anomaly detection report.
        
        Args:
            format: Report format (html, json, csv, pdf)
            
        Returns:
            Path to generated report file
        """
        format = format or self.default_format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"anomaly_report_{timestamp}.{format}"
        filepath = self.reports_dir / filename
        
        # Generate report data
        report_data = await self._generate_anomaly_data()
        
        if format == "html":
            await self._generate_html_report(report_data, filepath)
        elif format == "json":
            await self._generate_json_report(report_data, filepath)
        elif format == "csv":
            await self._generate_csv_report(report_data, filepath)
        elif format == "pdf":
            await self._generate_pdf_report(report_data, filepath)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        logger.info(f"Generated anomaly report: {filepath}")
        return str(filepath)
    
    async def generate_fault_report(self, format: str = None) -> str:
        """Generate fault injection report.
        
        Args:
            format: Report format (html, json, csv, pdf)
            
        Returns:
            Path to generated report file
        """
        format = format or self.default_format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fault_report_{timestamp}.{format}"
        filepath = self.reports_dir / filename
        
        # Generate report data
        report_data = await self._generate_fault_data()
        
        if format == "html":
            await self._generate_html_report(report_data, filepath)
        elif format == "json":
            await self._generate_json_report(report_data, filepath)
        elif format == "csv":
            await self._generate_csv_report(report_data, filepath)
        elif format == "pdf":
            await self._generate_pdf_report(report_data, filepath)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        logger.info(f"Generated fault report: {filepath}")
        return str(filepath)
    
    async def generate_performance_report(self, format: str = None) -> str:
        """Generate performance metrics report.
        
        Args:
            format: Report format (html, json, csv, pdf)
            
        Returns:
            Path to generated report file
        """
        format = format or self.default_format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.{format}"
        filepath = self.reports_dir / filename
        
        # Generate report data
        report_data = await self._generate_performance_data()
        
        if format == "html":
            await self._generate_html_report(report_data, filepath)
        elif format == "json":
            await self._generate_json_report(report_data, filepath)
        elif format == "csv":
            await self._generate_csv_report(report_data, filepath)
        elif format == "pdf":
            await self._generate_pdf_report(report_data, filepath)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        logger.info(f"Generated performance report: {filepath}")
        return str(filepath)
    
    async def generate_comprehensive_report(self, format: str = None) -> str:
        """Generate comprehensive system report.
        
        Args:
            format: Report format (html, json, csv, pdf)
            
        Returns:
            Path to generated report file
        """
        format = format or self.default_format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_report_{timestamp}.{format}"
        filepath = self.reports_dir / filename
        
        # Generate comprehensive report data
        report_data = await self._generate_comprehensive_data()
        
        if format == "html":
            await self._generate_html_report(report_data, filepath)
        elif format == "json":
            await self._generate_json_report(report_data, filepath)
        elif format == "csv":
            await self._generate_csv_report(report_data, filepath)
        elif format == "pdf":
            await self._generate_pdf_report(report_data, filepath)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        logger.info(f"Generated comprehensive report: {filepath}")
        return str(filepath)
    
    async def _generate_system_status_data(self) -> Dict[str, Any]:
        """Generate system status report data."""
        # Calculate statistics
        total_telemetry = len(self.telemetry_data)
        total_anomalies = len(self.anomaly_data)
        total_faults = len(self.fault_data)
        total_alerts = len(self.alert_data)
        
        # UAV statistics
        uav_ids = set(data["uav_id"] for data in self.telemetry_data)
        subsystem_counts = {}
        for data in self.telemetry_data:
            subsystem = data["subsystem"]
            subsystem_counts[subsystem] = subsystem_counts.get(subsystem, 0) + 1
        
        # Status distribution
        status_counts = {}
        for data in self.telemetry_data:
            status = data["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Alert severity distribution
        severity_counts = {}
        for data in self.alert_data:
            severity = data["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "report_type": "System Status",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_telemetry_points": total_telemetry,
                "total_anomalies": total_anomalies,
                "total_faults": total_faults,
                "total_alerts": total_alerts,
                "active_uavs": len(uav_ids)
            },
            "statistics": {
                "subsystem_counts": subsystem_counts,
                "status_distribution": status_counts,
                "alert_severity_distribution": severity_counts
            },
            "data": {
                "telemetry_data": self.telemetry_data[-100:],  # Last 100 points
                "anomaly_data": self.anomaly_data[-50:],  # Last 50 anomalies
                "fault_data": self.fault_data[-50:],  # Last 50 faults
                "alert_data": self.alert_data[-50:]  # Last 50 alerts
            }
        }
    
    async def _generate_anomaly_data(self) -> Dict[str, Any]:
        """Generate anomaly detection report data."""
        if not self.anomaly_data:
            return {
                "report_type": "Anomaly Detection",
                "generated_at": datetime.now().isoformat(),
                "summary": {"total_anomalies": 0},
                "data": []
            }
        
        # Calculate anomaly statistics
        anomaly_scores = [data["anomaly_score"] for data in self.anomaly_data]
        avg_score = sum(anomaly_scores) / len(anomaly_scores) if anomaly_scores else 0
        max_score = max(anomaly_scores) if anomaly_scores else 0
        min_score = min(anomaly_scores) if anomaly_scores else 0
        
        # Anomaly distribution by subsystem
        subsystem_anomalies = {}
        for data in self.anomaly_data:
            subsystem = data["subsystem"]
            subsystem_anomalies[subsystem] = subsystem_anomalies.get(subsystem, 0) + 1
        
        # High anomaly events
        high_anomalies = [data for data in self.anomaly_data if data["anomaly_score"] > 0.8]
        
        return {
            "report_type": "Anomaly Detection",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_anomalies": len(self.anomaly_data),
                "high_anomalies": len(high_anomalies),
                "average_score": avg_score,
                "max_score": max_score,
                "min_score": min_score
            },
            "statistics": {
                "subsystem_anomaly_distribution": subsystem_anomalies,
                "score_distribution": {
                    "low": len([s for s in anomaly_scores if s < 0.3]),
                    "medium": len([s for s in anomaly_scores if 0.3 <= s < 0.7]),
                    "high": len([s for s in anomaly_scores if s >= 0.7])
                }
            },
            "data": {
                "all_anomalies": self.anomaly_data,
                "high_anomalies": high_anomalies
            }
        }
    
    async def _generate_fault_data(self) -> Dict[str, Any]:
        """Generate fault injection report data."""
        if not self.fault_data:
            return {
                "report_type": "Fault Injection",
                "generated_at": datetime.now().isoformat(),
                "summary": {"total_faults": 0},
                "data": []
            }
        
        # Calculate fault statistics
        fault_types = [data["fault_type"] for data in self.fault_data]
        fault_type_counts = {}
        for fault_type in fault_types:
            fault_type_counts[fault_type] = fault_type_counts.get(fault_type, 0) + 1
        
        # Fault distribution by subsystem
        subsystem_faults = {}
        for data in self.fault_data:
            subsystem = data["subsystem"]
            subsystem_faults[subsystem] = subsystem_faults.get(subsystem, 0) + 1
        
        # Recent faults
        recent_faults = sorted(self.fault_data, key=lambda x: x["timestamp"], reverse=True)[:20]
        
        return {
            "report_type": "Fault Injection",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_faults": len(self.fault_data),
                "unique_fault_types": len(fault_type_counts),
                "affected_subsystems": len(subsystem_faults)
            },
            "statistics": {
                "fault_type_distribution": fault_type_counts,
                "subsystem_fault_distribution": subsystem_faults
            },
            "data": {
                "all_faults": self.fault_data,
                "recent_faults": recent_faults
            }
        }
    
    async def _generate_performance_data(self) -> Dict[str, Any]:
        """Generate performance metrics report data."""
        if not self.performance_data:
            return {
                "report_type": "Performance Metrics",
                "generated_at": datetime.now().isoformat(),
                "summary": {"total_metrics": 0},
                "data": []
            }
        
        # Calculate performance statistics
        cpu_values = [data["cpu_usage"] for data in self.performance_data]
        memory_values = [data["memory_usage"] for data in self.performance_data]
        disk_values = [data["disk_usage"] for data in self.performance_data]
        latency_values = [data["network_latency"] for data in self.performance_data]
        
        return {
            "report_type": "Performance Metrics",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_metrics": len(self.performance_data),
                "cpu_avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "memory_avg": sum(memory_values) / len(memory_values) if memory_values else 0,
                "disk_avg": sum(disk_values) / len(disk_values) if disk_values else 0,
                "latency_avg": sum(latency_values) / len(latency_values) if latency_values else 0
            },
            "statistics": {
                "cpu": {"min": min(cpu_values), "max": max(cpu_values), "avg": sum(cpu_values) / len(cpu_values)},
                "memory": {"min": min(memory_values), "max": max(memory_values), "avg": sum(memory_values) / len(memory_values)},
                "disk": {"min": min(disk_values), "max": max(disk_values), "avg": sum(disk_values) / len(disk_values)},
                "latency": {"min": min(latency_values), "max": max(latency_values), "avg": sum(latency_values) / len(latency_values)}
            },
            "data": self.performance_data
        }
    
    async def _generate_comprehensive_data(self) -> Dict[str, Any]:
        """Generate comprehensive report data."""
        return {
            "report_type": "Comprehensive System Report",
            "generated_at": datetime.now().isoformat(),
            "sections": {
                "system_status": await self._generate_system_status_data(),
                "anomaly_detection": await self._generate_anomaly_data(),
                "fault_injection": await self._generate_fault_data(),
                "performance_metrics": await self._generate_performance_data()
            }
        }
    
    async def _generate_html_report(self, data: Dict[str, Any], filepath: Path) -> None:
        """Generate HTML report."""
        template = self._get_html_template()
        
        # Generate charts
        charts = await self._generate_charts(data)
        
        # Render template
        html_content = template.render(
            data=data,
            charts=charts,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    async def _generate_json_report(self, data: Dict[str, Any], filepath: Path) -> None:
        """Generate JSON report."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def _generate_csv_report(self, data: Dict[str, Any], filepath: Path) -> None:
        """Generate CSV report."""
        # Convert data to CSV format
        csv_data = []
        
        if "data" in data:
            for section_name, section_data in data["data"].items():
                if isinstance(section_data, list):
                    for item in section_data:
                        row = {"section": section_name}
                        row.update(item)
                        csv_data.append(row)
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(filepath, index=False)
        else:
            # Create empty CSV with headers
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["section", "timestamp", "data"])
    
    async def _generate_pdf_report(self, data: Dict[str, Any], filepath: Path) -> None:
        """Generate PDF report."""
        # For now, generate HTML and suggest conversion to PDF
        html_filepath = filepath.with_suffix('.html')
        await self._generate_html_report(data, html_filepath)
        
        # Note: PDF generation would require additional libraries like weasyprint or reportlab
        logger.warning(f"PDF generation not implemented. HTML report saved to: {html_filepath}")
    
    def _get_html_template(self) -> Template:
        """Get HTML report template."""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.report_type }} Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .summary { background-color: #e8f4f8; padding: 15px; border-radius: 5px; }
        .statistics { background-color: #f8f8f8; padding: 15px; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .chart { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ data.report_type }} Report</h1>
        <p>Generated on: {{ generated_at }}</p>
    </div>
    
    {% if data.summary %}
    <div class="section">
        <h2>Summary</h2>
        <div class="summary">
            {% for key, value in data.summary.items() %}
            <p><strong>{{ key.replace('_', ' ').title() }}:</strong> {{ value }}</p>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    
    {% if data.statistics %}
    <div class="section">
        <h2>Statistics</h2>
        <div class="statistics">
            {% for section_name, section_data in data.statistics.items() %}
            <h3>{{ section_name.replace('_', ' ').title() }}</h3>
            {% if section_data is mapping %}
                {% for key, value in section_data.items() %}
                <p><strong>{{ key.replace('_', ' ').title() }}:</strong> {{ value }}</p>
                {% endfor %}
            {% else %}
                <p>{{ section_data }}</p>
            {% endif %}
            {% endfor %}
        </div>
    </div>
    {% endif %}
    
    {% if charts %}
    <div class="section">
        <h2>Charts</h2>
        {% for chart in charts %}
        <div class="chart">
            {{ chart|safe }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if data.data %}
    <div class="section">
        <h2>Data</h2>
        {% for section_name, section_data in data.data.items() %}
        <h3>{{ section_name.replace('_', ' ').title() }}</h3>
        {% if section_data is list and section_data %}
        <table>
            <thead>
                <tr>
                    {% for key in section_data[0].keys() %}
                    <th>{{ key.replace('_', ' ').title() }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for item in section_data[:10] %}
                <tr>
                    {% for value in item.values() %}
                    <td>{{ value }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if section_data|length > 10 %}
        <p><em>Showing first 10 of {{ section_data|length }} items</em></p>
        {% endif %}
        {% else %}
        <p>No data available</p>
        {% endif %}
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
        """
        return Template(template_str)
    
    async def _generate_charts(self, data: Dict[str, Any]) -> List[str]:
        """Generate charts for HTML report."""
        charts = []
        
        # Generate charts based on data type
        if data["report_type"] == "System Status":
            charts.extend(await self._generate_system_status_charts(data))
        elif data["report_type"] == "Anomaly Detection":
            charts.extend(await self._generate_anomaly_charts(data))
        elif data["report_type"] == "Fault Injection":
            charts.extend(await self._generate_fault_charts(data))
        elif data["report_type"] == "Performance Metrics":
            charts.extend(await self._generate_performance_charts(data))
        
        return charts
    
    async def _generate_system_status_charts(self, data: Dict[str, Any]) -> List[str]:
        """Generate system status charts."""
        charts = []
        
        # Status distribution pie chart
        if "status_distribution" in data.get("statistics", {}):
            status_data = data["statistics"]["status_distribution"]
            fig = px.pie(values=list(status_data.values()), names=list(status_data.keys()),
                        title="System Status Distribution")
            charts.append(fig.to_html(include_plotlyjs=False, div_id="status_chart"))
        
        # Subsystem activity bar chart
        if "subsystem_counts" in data.get("statistics", {}):
            subsystem_data = data["statistics"]["subsystem_counts"]
            fig = px.bar(x=list(subsystem_data.keys()), y=list(subsystem_data.values()),
                        title="Subsystem Activity")
            charts.append(fig.to_html(include_plotlyjs=False, div_id="subsystem_chart"))
        
        return charts
    
    async def _generate_anomaly_charts(self, data: Dict[str, Any]) -> List[str]:
        """Generate anomaly detection charts."""
        charts = []
        
        # Anomaly score distribution
        if "data" in data and "all_anomalies" in data["data"]:
            anomaly_data = data["data"]["all_anomalies"]
            if anomaly_data:
                scores = [item["anomaly_score"] for item in anomaly_data]
                timestamps = [item["timestamp"] for item in anomaly_data]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=timestamps, y=scores, mode='markers',
                                       name='Anomaly Scores'))
                fig.add_hline(y=0.8, line_dash="dash", line_color="red",
                            annotation_text="Threshold")
                fig.update_layout(title="Anomaly Score Timeline")
                charts.append(fig.to_html(include_plotlyjs=False, div_id="anomaly_timeline"))
        
        return charts
    
    async def _generate_fault_charts(self, data: Dict[str, Any]) -> List[str]:
        """Generate fault injection charts."""
        charts = []
        
        # Fault type distribution
        if "fault_type_distribution" in data.get("statistics", {}):
            fault_data = data["statistics"]["fault_type_distribution"]
            fig = px.pie(values=list(fault_data.values()), names=list(fault_data.keys()),
                        title="Fault Type Distribution")
            charts.append(fig.to_html(include_plotlyjs=False, div_id="fault_type_chart"))
        
        return charts
    
    async def _generate_performance_charts(self, data: Dict[str, Any]) -> List[str]:
        """Generate performance metrics charts."""
        charts = []
        
        # Performance metrics over time
        if "data" in data and isinstance(data["data"], list):
            perf_data = data["data"]
            if perf_data:
                timestamps = [item["timestamp"] for item in perf_data]
                
                fig = make_subplots(rows=2, cols=2, subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage', 'Network Latency'))
                
                fig.add_trace(go.Scatter(x=timestamps, y=[item["cpu_usage"] for item in perf_data],
                                       mode='lines', name='CPU'), row=1, col=1)
                fig.add_trace(go.Scatter(x=timestamps, y=[item["memory_usage"] for item in perf_data],
                                       mode='lines', name='Memory'), row=1, col=2)
                fig.add_trace(go.Scatter(x=timestamps, y=[item["disk_usage"] for item in perf_data],
                                       mode='lines', name='Disk'), row=2, col=1)
                fig.add_trace(go.Scatter(x=timestamps, y=[item["network_latency"] for item in perf_data],
                                       mode='lines', name='Latency'), row=2, col=2)
                
                fig.update_layout(title="Performance Metrics Over Time", height=600)
                charts.append(fig.to_html(include_plotlyjs=False, div_id="performance_chart"))
        
        return charts
    
    def clear_data(self) -> None:
        """Clear all stored data."""
        self.telemetry_data.clear()
        self.anomaly_data.clear()
        self.fault_data.clear()
        self.alert_data.clear()
        self.performance_data.clear()
        logger.info("Cleared all report data")
    
    def get_data_summary(self) -> Dict[str, int]:
        """Get summary of stored data.
        
        Returns:
            Dictionary with data counts
        """
        return {
            "telemetry_points": len(self.telemetry_data),
            "anomalies": len(self.anomaly_data),
            "faults": len(self.fault_data),
            "alerts": len(self.alert_data),
            "performance_metrics": len(self.performance_data)
        }
