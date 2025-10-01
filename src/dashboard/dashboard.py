"""Web-based dashboard for UAV Mission Control & Anomaly Detection Simulator."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from ..utils.config import config
from ..utils.models import TelemetryData, Alert, SeverityLevel


class UAVDashboard:
    """Web-based dashboard for UAV simulator."""
    
    def __init__(self, simulator=None):
        """Initialize dashboard.
        
        Args:
            simulator: UAV simulator instance
        """
        self.simulator = simulator
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            title="UAV Mission Control & Anomaly Detection Simulator"
        )
        
        # Dashboard configuration
        self.host = config.get("dashboard.host", "0.0.0.0")
        self.port = config.get("dashboard.port", 8050)
        self.refresh_interval = config.get("dashboard.refresh_interval", 1000)
        self.max_data_points = config.get("dashboard.max_data_points", 1000)
        
        # Data storage
        self.telemetry_data: Dict[str, List[Dict]] = {}
        self.anomaly_data: Dict[str, List[Dict]] = {}
        self.fault_data: Dict[str, List[Dict]] = {}
        self.performance_data: List[Dict] = []
        
        # Setup dashboard
        self._setup_layout()
        self._setup_callbacks()
        
    def _setup_layout(self) -> None:
        """Setup dashboard layout."""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("UAV Mission Control & Anomaly Detection Simulator", 
                           className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Control Panel"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("UAV ID:"),
                                    dcc.Dropdown(
                                        id="uav-dropdown",
                                        options=[],
                                        value=None,
                                        placeholder="Select UAV"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Subsystem:"),
                                    dcc.Dropdown(
                                        id="subsystem-dropdown",
                                        options=[],
                                        value=None,
                                        placeholder="Select Subsystem"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Fault Type:"),
                                    dcc.Dropdown(
                                        id="fault-dropdown",
                                        options=[
                                            {"label": "GPS Drift", "value": "gps_drift"},
                                            {"label": "Motor Failure", "value": "motor_failure"},
                                            {"label": "Signal Loss", "value": "signal_loss"},
                                            {"label": "Battery Failure", "value": "battery_failure"},
                                            {"label": "Sensor Failure", "value": "sensor_failure"}
                                        ],
                                        value=None,
                                        placeholder="Select Fault Type"
                                    )
                                ], width=4)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Inject Fault", id="inject-fault-btn", 
                                             color="danger", className="me-2"),
                                    dbc.Button("Clear Fault", id="clear-fault-btn", 
                                             color="success", className="me-2"),
                                    dbc.Button("Refresh Data", id="refresh-btn", 
                                             color="primary")
                                ], className="mt-3")
                            ])
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Status Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("System Status", className="card-title"),
                            html.H2(id="system-status", className="text-success"),
                            html.P("Overall System Health")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Active UAVs", className="card-title"),
                            html.H2(id="uav-count", className="text-primary"),
                            html.P("UAVs in Simulation")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Active Faults", className="card-title"),
                            html.H2(id="fault-count", className="text-danger"),
                            html.P("Injected Faults")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Anomalies", className="card-title"),
                            html.H2(id="anomaly-count", className="text-warning"),
                            html.P("Detected Anomalies")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # Charts Row 1
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Telemetry Data"),
                        dbc.CardBody([
                            dcc.Graph(id="telemetry-chart")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Anomaly Detection"),
                        dbc.CardBody([
                            dcc.Graph(id="anomaly-chart")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # Charts Row 2
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("System Performance"),
                        dbc.CardBody([
                            dcc.Graph(id="performance-chart")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Fault Statistics"),
                        dbc.CardBody([
                            dcc.Graph(id="fault-chart")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # UAV Status Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("UAV Status Overview"),
                        dbc.CardBody([
                            html.Div(id="uav-table")
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Auto-refresh
            dcc.Interval(
                id='interval-component',
                interval=self.refresh_interval,
                n_intervals=0
            )
        ], fluid=True)
    
    def _setup_callbacks(self) -> None:
        """Setup dashboard callbacks."""
        
        @self.app.callback(
            [Output('uav-dropdown', 'options'),
             Output('subsystem-dropdown', 'options')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dropdowns(n):
            """Update dropdown options."""
            if not self.simulator:
                return [], []
            
            # Get UAV options
            uav_status = self.simulator.get_all_uav_status()
            uav_options = [{"label": uav_id, "value": uav_id} for uav_id in uav_status.keys()]
            
            # Get subsystem options
            subsystem_options = [
                {"label": "Navigation", "value": "Navigation"},
                {"label": "Propulsion", "value": "Propulsion"},
                {"label": "Communication", "value": "Communication"},
                {"label": "Power", "value": "Power"},
                {"label": "Payload", "value": "Payload"},
                {"label": "Environmental", "value": "Environmental"},
                {"label": "Flight Control", "value": "Flight_Control"},
                {"label": "Sensor Fusion", "value": "Sensor_Fusion"},
                {"label": "Mission Planning", "value": "Mission_Planning"},
                {"label": "Safety Systems", "value": "Safety_Systems"},
                {"label": "Data Storage", "value": "Data_Storage"}
            ]
            
            return uav_options, subsystem_options
        
        @self.app.callback(
            [Output('system-status', 'children'),
             Output('uav-count', 'children'),
             Output('fault-count', 'children'),
             Output('anomaly-count', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_status_cards(n):
            """Update status cards."""
            if not self.simulator:
                return "Unknown", "0", "0", "0"
            
            status = self.simulator.get_status()
            
            system_status = "Healthy" if status["is_running"] else "Stopped"
            uav_count = str(status["uav_count"])
            fault_count = str(status["active_faults"])
            anomaly_count = str(status["anomaly_stats"]["anomalies_detected"])
            
            return system_status, uav_count, fault_count, anomaly_count
        
        @self.app.callback(
            Output('telemetry-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_telemetry_chart(n):
            """Update telemetry chart."""
            fig = go.Figure()
            
            if self.telemetry_data:
                for uav_id, data in self.telemetry_data.items():
                    if data:
                        df = pd.DataFrame(data[-self.max_data_points:])
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df['value'],
                            mode='lines',
                            name=uav_id,
                            line=dict(width=2)
                        ))
            
            fig.update_layout(
                title="Real-time Telemetry Data",
                xaxis_title="Time",
                yaxis_title="Value",
                hovermode='x unified'
            )
            
            return fig
        
        @self.app.callback(
            Output('anomaly-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_anomaly_chart(n):
            """Update anomaly detection chart."""
            fig = go.Figure()
            
            if self.anomaly_data:
                for uav_id, data in self.anomaly_data.items():
                    if data:
                        df = pd.DataFrame(data[-self.max_data_points:])
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df['anomaly_score'],
                            mode='lines+markers',
                            name=f"{uav_id} Anomaly Score",
                            line=dict(width=2),
                            marker=dict(size=4)
                        ))
            
            # Add threshold line
            fig.add_hline(y=0.8, line_dash="dash", line_color="red", 
                         annotation_text="Anomaly Threshold")
            
            fig.update_layout(
                title="Anomaly Detection Scores",
                xaxis_title="Time",
                yaxis_title="Anomaly Score",
                yaxis=dict(range=[0, 1]),
                hovermode='x unified'
            )
            
            return fig
        
        @self.app.callback(
            Output('performance-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_performance_chart(n):
            """Update system performance chart."""
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage', 'Network Latency'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            if self.performance_data:
                df = pd.DataFrame(self.performance_data[-self.max_data_points:])
                
                # CPU Usage
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['cpu_usage'], 
                              mode='lines', name='CPU Usage'),
                    row=1, col=1
                )
                
                # Memory Usage
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['memory_usage'], 
                              mode='lines', name='Memory Usage'),
                    row=1, col=2
                )
                
                # Disk Usage
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['disk_usage'], 
                              mode='lines', name='Disk Usage'),
                    row=2, col=1
                )
                
                # Network Latency
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['network_latency'], 
                              mode='lines', name='Network Latency'),
                    row=2, col=2
                )
            
            fig.update_layout(
                title="System Performance Metrics",
                height=600,
                showlegend=False
            )
            
            return fig
        
        @self.app.callback(
            Output('fault-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_fault_chart(n):
            """Update fault statistics chart."""
            if not self.simulator:
                return go.Figure()
            
            stats = self.simulator.get_status()
            fault_stats = stats["fault_stats"]
            
            # Create pie chart for fault types
            fault_types = list(fault_stats["faults_by_type"].keys())
            fault_counts = list(fault_stats["faults_by_type"].values())
            
            fig = go.Figure(data=[go.Pie(
                labels=fault_types,
                values=fault_counts,
                hole=0.3
            )])
            
            fig.update_layout(
                title="Fault Distribution by Type",
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output('uav-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_uav_table(n):
            """Update UAV status table."""
            if not self.simulator:
                return "No simulator available"
            
            uav_status = self.simulator.get_all_uav_status()
            
            if not uav_status:
                return "No UAVs available"
            
            # Create table rows
            rows = []
            for uav_id, subsystems in uav_status.items():
                row = []
                for subsystem, status in subsystems.items():
                    status_color = "success" if status["status"] == "nominal" else "danger"
                    row.append(
                        dbc.Badge(
                            status["status"],
                            color=status_color,
                            className="me-1"
                        )
                    )
                
                rows.append(
                    html.Tr([
                        html.Td(uav_id),
                        html.Td(row)
                    ])
                )
            
            table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("UAV ID"),
                        html.Th("Subsystem Status")
                    ])
                ]),
                html.Tbody(rows)
            ], striped=True, bordered=True, hover=True)
            
            return table
        
        @self.app.callback(
            Output('inject-fault-btn', 'disabled'),
            [Input('inject-fault-btn', 'n_clicks')],
            [State('uav-dropdown', 'value'),
             State('subsystem-dropdown', 'value'),
             State('fault-dropdown', 'value')]
        )
        def inject_fault(n_clicks, uav_id, subsystem, fault_type):
            """Inject fault callback."""
            if n_clicks and uav_id and subsystem and fault_type:
                if self.simulator:
                    asyncio.create_task(
                        self.simulator.inject_fault(uav_id, subsystem, fault_type)
                    )
            return False
        
        @self.app.callback(
            Output('clear-fault-btn', 'disabled'),
            [Input('clear-fault-btn', 'n_clicks')],
            [State('uav-dropdown', 'value'),
             State('subsystem-dropdown', 'value'),
             State('fault-dropdown', 'value')]
        )
        def clear_fault(n_clicks, uav_id, subsystem, fault_type):
            """Clear fault callback."""
            if n_clicks and uav_id and subsystem and fault_type:
                if self.simulator:
                    asyncio.create_task(
                        self.simulator.clear_fault(uav_id, subsystem, fault_type)
                    )
            return False
    
    def add_telemetry_data(self, telemetry_data: TelemetryData) -> None:
        """Add telemetry data to dashboard.
        
        Args:
            telemetry_data: Telemetry data to add
        """
        uav_id = telemetry_data.uav_id
        subsystem = telemetry_data.subsystem
        
        if uav_id not in self.telemetry_data:
            self.telemetry_data[uav_id] = []
        
        # Extract relevant data (simplified)
        data_point = {
            'timestamp': telemetry_data.timestamp.isoformat(),
            'subsystem': subsystem,
            'value': self._extract_telemetry_value(telemetry_data.data),
            'anomaly_score': telemetry_data.anomaly_score or 0.0
        }
        
        self.telemetry_data[uav_id].append(data_point)
        
        # Limit data points
        if len(self.telemetry_data[uav_id]) > self.max_data_points:
            self.telemetry_data[uav_id] = self.telemetry_data[uav_id][-self.max_data_points:]
    
    def add_anomaly_data(self, uav_id: str, subsystem: str, anomaly_score: float) -> None:
        """Add anomaly data to dashboard.
        
        Args:
            uav_id: UAV identifier
            subsystem: Subsystem name
            anomaly_score: Anomaly score
        """
        key = f"{uav_id}_{subsystem}"
        
        if key not in self.anomaly_data:
            self.anomaly_data[key] = []
        
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'anomaly_score': anomaly_score
        }
        
        self.anomaly_data[key].append(data_point)
        
        # Limit data points
        if len(self.anomaly_data[key]) > self.max_data_points:
            self.anomaly_data[key] = self.anomaly_data[key][-self.max_data_points:]
    
    def add_performance_data(self, metrics) -> None:
        """Add performance metrics to dashboard.
        
        Args:
            metrics: Performance metrics
        """
        data_point = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': metrics.cpu_usage,
            'memory_usage': metrics.memory_usage,
            'disk_usage': metrics.disk_usage,
            'network_latency': metrics.network_latency,
            'active_connections': metrics.active_connections,
            'error_rate': metrics.error_rate
        }
        
        self.performance_data.append(data_point)
        
        # Limit data points
        if len(self.performance_data) > self.max_data_points:
            self.performance_data = self.performance_data[-self.max_data_points:]
    
    def _extract_telemetry_value(self, data: Dict[str, Any]) -> float:
        """Extract a single value from telemetry data for plotting.
        
        Args:
            data: Telemetry data dictionary
            
        Returns:
            Extracted value
        """
        # Try to extract a meaningful value for plotting
        if 'battery' in data and 'voltage' in data['battery']:
            return float(data['battery']['voltage'])
        elif 'position' in data and 'altitude' in data['position']:
            return float(data['position']['altitude'])
        elif 'motors' in data:
            # Sum motor thrust
            total_thrust = sum(motor.get('thrust', 0) for motor in data['motors'].values())
            return float(total_thrust)
        else:
            return 0.0
    
    def run(self, debug: bool = False) -> None:
        """Run the dashboard.
        
        Args:
            debug: Enable debug mode
        """
        self.app.run_server(
            host=self.host,
            port=self.port,
            debug=debug
        )


def create_dashboard(simulator=None):
    """Create and return a dashboard instance.
    
    Args:
        simulator: UAV simulator instance
        
    Returns:
        Dashboard app instance
    """
    dashboard = UAVDashboard(simulator)
    return dashboard.app
