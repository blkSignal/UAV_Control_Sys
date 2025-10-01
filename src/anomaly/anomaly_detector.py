"""Real-time anomaly detection engine for UAV telemetry data."""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import deque
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from loguru import logger

from ..utils.models import TelemetryData, AnomalyDetectionResult, Alert, SeverityLevel
from ..utils.config import config


class AnomalyDetector:
    """Real-time anomaly detection engine for UAV telemetry data."""
    
    def __init__(self):
        """Initialize anomaly detector."""
        self.enabled = config.get("anomaly_detection.enabled", True)
        self.algorithm = config.get("anomaly_detection.algorithm", "isolation_forest")
        self.threshold = config.get("anomaly_detection.threshold", 0.8)
        self.window_size = config.get("anomaly_detection.window_size", 100)
        self.retrain_interval = config.get("anomaly_detection.retrain_interval", 300)
        
        # Feature configuration
        self.features = config.get("anomaly_detection.features", [
            "cpu_usage", "memory_usage", "temperature", "voltage", "current",
            "altitude", "speed", "battery_level"
        ])
        
        # Data storage
        self.data_windows: Dict[str, deque] = {}
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.last_retrain: Dict[str, datetime] = {}
        
        # Callbacks
        self.anomaly_callbacks: List[Callable] = []
        
        # Alert storage
        self.alerts: List[Alert] = []
        
        # Statistics
        self.stats = {
            "total_predictions": 0,
            "anomalies_detected": 0,
            "false_positives": 0,
            "true_positives": 0,
            "model_retrains": 0
        }
        
        logger.info(f"AnomalyDetector initialized with {self.algorithm} algorithm")
    
    async def process_telemetry(self, telemetry_data: TelemetryData) -> AnomalyDetectionResult:
        """Process telemetry data for anomaly detection.
        
        Args:
            telemetry_data: Telemetry data to analyze
            
        Returns:
            AnomalyDetectionResult with detection results
        """
        if not self.enabled:
            return AnomalyDetectionResult(
                uav_id=telemetry_data.uav_id,
                subsystem=telemetry_data.subsystem,
                anomaly_score=0.0,
                is_anomaly=False,
                features={},
                algorithm=self.algorithm,
                confidence=1.0
            )
        
        # Extract features from telemetry data
        features = self._extract_features(telemetry_data)
        
        if not features:
            logger.warning(f"No features extracted from {telemetry_data.subsystem}")
            return AnomalyDetectionResult(
                uav_id=telemetry_data.uav_id,
                subsystem=telemetry_data.subsystem,
                anomaly_score=0.0,
                is_anomaly=False,
                features={},
                algorithm=self.algorithm,
                confidence=0.0
            )
        
        # Get or create data window for this subsystem
        window_key = f"{telemetry_data.uav_id}_{telemetry_data.subsystem}"
        if window_key not in self.data_windows:
            self.data_windows[window_key] = deque(maxlen=self.window_size)
            self.models[window_key] = self._create_model()
            self.scalers[window_key] = StandardScaler()
            self.last_retrain[window_key] = datetime.now()
        
        # Add features to data window
        self.data_windows[window_key].append(features)
        
        # Check if we have enough data for prediction
        if len(self.data_windows[window_key]) < 10:
            return AnomalyDetectionResult(
                uav_id=telemetry_data.uav_id,
                subsystem=telemetry_data.subsystem,
                anomaly_score=0.0,
                is_anomaly=False,
                features=features,
                algorithm=self.algorithm,
                confidence=0.5
            )
        
        # Retrain model if needed
        await self._retrain_model_if_needed(window_key)
        
        # Perform anomaly detection
        anomaly_score, is_anomaly = await self._detect_anomaly(window_key, features)
        
        # Update statistics
        self.stats["total_predictions"] += 1
        if is_anomaly:
            self.stats["anomalies_detected"] += 1
        
        # Create result
        result = AnomalyDetectionResult(
            uav_id=telemetry_data.uav_id,
            subsystem=telemetry_data.subsystem,
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            features=features,
            algorithm=self.algorithm,
            confidence=self._calculate_confidence(window_key, anomaly_score)
        )
        
        # Send to callbacks if anomaly detected
        if is_anomaly:
            await self._handle_anomaly(result, telemetry_data)
        
        return result
    
    def _extract_features(self, telemetry_data: TelemetryData) -> Dict[str, float]:
        """Extract features from telemetry data.
        
        Args:
            telemetry_data: Telemetry data to extract features from
            
        Returns:
            Dictionary of feature names and values
        """
        features = {}
        data = telemetry_data.data
        
        # Extract common features
        for feature_name in self.features:
            feature_value = self._extract_feature_value(data, feature_name)
            if feature_value is not None:
                features[feature_name] = feature_value
        
        # Extract subsystem-specific features
        subsystem_features = self._extract_subsystem_features(data, telemetry_data.subsystem)
        features.update(subsystem_features)
        
        return features
    
    def _extract_feature_value(self, data: Dict[str, Any], feature_name: str) -> Optional[float]:
        """Extract a specific feature value from telemetry data.
        
        Args:
            data: Telemetry data dictionary
            feature_name: Name of the feature to extract
            
        Returns:
            Feature value or None if not found
        """
        # Common feature mappings
        feature_mappings = {
            "cpu_usage": ["system", "cpu_usage"],
            "memory_usage": ["system", "memory_usage"],
            "temperature": ["temperature", "battery", "temperature", "motors", "motor_1", "temperature"],
            "voltage": ["voltage", "battery", "voltage", "motors", "motor_1", "voltage"],
            "current": ["current", "battery", "current", "motors", "motor_1", "current"],
            "altitude": ["position", "altitude", "altitude"],
            "speed": ["velocity", "speed", "speed"],
            "battery_level": ["battery", "state_of_charge", "remaining_capacity"]
        }
        
        if feature_name not in feature_mappings:
            return None
        
        # Navigate through nested data structure
        current_data = data
        for key in feature_mappings[feature_name]:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return None
        
        # Convert to float if possible
        try:
            return float(current_data)
        except (ValueError, TypeError):
            return None
    
    def _extract_subsystem_features(self, data: Dict[str, Any], subsystem: str) -> Dict[str, float]:
        """Extract subsystem-specific features.
        
        Args:
            data: Telemetry data dictionary
            subsystem: Name of the subsystem
            
        Returns:
            Dictionary of subsystem-specific features
        """
        features = {}
        
        if subsystem == "Navigation":
            # Navigation-specific features
            if "position" in data:
                pos = data["position"]
                features["latitude"] = pos.get("latitude", 0.0)
                features["longitude"] = pos.get("longitude", 0.0)
                features["altitude"] = pos.get("altitude", 0.0)
            
            if "attitude" in data:
                att = data["attitude"]
                features["heading"] = att.get("heading", 0.0)
                features["roll"] = att.get("roll", 0.0)
                features["pitch"] = att.get("pitch", 0.0)
        
        elif subsystem == "Propulsion":
            # Propulsion-specific features
            if "motors" in data:
                motors = data["motors"]
                total_thrust = sum(motor.get("thrust", 0) for motor in motors.values())
                features["total_thrust"] = total_thrust
                
                avg_temp = sum(motor.get("temperature", 0) for motor in motors.values()) / len(motors)
                features["avg_motor_temp"] = avg_temp
        
        elif subsystem == "Power":
            # Power-specific features
            if "battery" in data:
                battery = data["battery"]
                features["battery_voltage"] = battery.get("voltage", 0.0)
                features["battery_current"] = battery.get("current", 0.0)
                features["battery_soc"] = battery.get("state_of_charge", 0.0)
        
        elif subsystem == "Communication":
            # Communication-specific features
            if "radio" in data:
                radio = data["radio"]
                features["rssi"] = radio.get("rssi", 0.0)
                features["snr"] = radio.get("snr", 0.0)
                features["packet_loss"] = radio.get("packet_loss", 0.0)
        
        return features
    
    def _create_model(self) -> Any:
        """Create a new anomaly detection model.
        
        Returns:
            Anomaly detection model
        """
        if self.algorithm == "isolation_forest":
            return IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
        elif self.algorithm == "one_class_svm":
            return OneClassSVM(
                nu=0.1,
                kernel="rbf",
                gamma="scale"
            )
        elif self.algorithm == "local_outlier_factor":
            return LocalOutlierFactor(
                n_neighbors=20,
                contamination=0.1
            )
        else:
            logger.warning(f"Unknown algorithm {self.algorithm}, using IsolationForest")
            return IsolationForest(contamination=0.1, random_state=42)
    
    async def _retrain_model_if_needed(self, window_key: str) -> None:
        """Retrain model if needed based on time interval.
        
        Args:
            window_key: Key for the data window
        """
        now = datetime.now()
        last_retrain = self.last_retrain[window_key]
        
        if (now - last_retrain).total_seconds() >= self.retrain_interval:
            await self._retrain_model(window_key)
            self.last_retrain[window_key] = now
            self.stats["model_retrains"] += 1
    
    async def _retrain_model(self, window_key: str) -> None:
        """Retrain the anomaly detection model.
        
        Args:
            window_key: Key for the data window
        """
        if len(self.data_windows[window_key]) < 20:
            return
        
        try:
            # Convert data window to numpy array
            data_array = np.array(list(self.data_windows[window_key]))
            
            # Scale the data
            scaled_data = self.scalers[window_key].fit_transform(data_array)
            
            # Train the model
            model = self.models[window_key]
            if self.algorithm == "local_outlier_factor":
                # LOF doesn't have fit method, it's used differently
                pass
            else:
                model.fit(scaled_data)
            
            logger.debug(f"Retrained model for {window_key}")
            
        except Exception as e:
            logger.error(f"Error retraining model for {window_key}: {e}")
    
    async def _detect_anomaly(self, window_key: str, features: Dict[str, float]) -> tuple[float, bool]:
        """Detect anomaly in the given features.
        
        Args:
            window_key: Key for the data window
            features: Features to analyze
            
        Returns:
            Tuple of (anomaly_score, is_anomaly)
        """
        try:
            # Convert features to array
            feature_array = np.array([list(features.values())]).reshape(1, -1)
            
            # Scale the features
            scaled_features = self.scalers[window_key].transform(feature_array)
            
            # Get model and make prediction
            model = self.models[window_key]
            
            if self.algorithm == "isolation_forest":
                anomaly_score = model.decision_function(scaled_features)[0]
                is_anomaly = model.predict(scaled_features)[0] == -1
            elif self.algorithm == "one_class_svm":
                anomaly_score = model.decision_function(scaled_features)[0]
                is_anomaly = model.predict(scaled_features)[0] == -1
            elif self.algorithm == "local_outlier_factor":
                anomaly_score = model.score_samples(scaled_features)[0]
                is_anomaly = model.fit_predict(scaled_features)[0] == -1
            else:
                anomaly_score = 0.0
                is_anomaly = False
            
            # Normalize anomaly score to 0-1 range
            if self.algorithm == "isolation_forest":
                # IsolationForest: higher score = more normal
                anomaly_score = max(0, min(1, (anomaly_score + 0.5) / 1.0))
            elif self.algorithm == "one_class_svm":
                # OneClassSVM: higher score = more normal
                anomaly_score = max(0, min(1, (anomaly_score + 1.0) / 2.0))
            elif self.algorithm == "local_outlier_factor":
                # LOF: lower score = more anomalous
                anomaly_score = max(0, min(1, -anomaly_score))
            
            # Apply threshold
            is_anomaly = is_anomaly or anomaly_score > self.threshold
            
            return anomaly_score, is_anomaly
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return 0.0, False
    
    def _calculate_confidence(self, window_key: str, anomaly_score: float) -> float:
        """Calculate confidence in the anomaly detection result.
        
        Args:
            window_key: Key for the data window
            anomaly_score: Anomaly score
            
        Returns:
            Confidence value between 0 and 1
        """
        # Base confidence on data window size and anomaly score
        window_size = len(self.data_windows[window_key])
        size_confidence = min(1.0, window_size / self.window_size)
        
        # Confidence decreases with extreme anomaly scores
        score_confidence = 1.0 - abs(anomaly_score - 0.5) * 2
        
        return (size_confidence + score_confidence) / 2
    
    async def _handle_anomaly(self, result: AnomalyDetectionResult, telemetry_data: TelemetryData) -> None:
        """Handle detected anomaly.
        
        Args:
            result: Anomaly detection result
            telemetry_data: Original telemetry data
        """
        # Create alert
        alert = Alert(
            uav_id=result.uav_id,
            subsystem=result.subsystem,
            severity=SeverityLevel.HIGH if result.anomaly_score > 0.9 else SeverityLevel.MEDIUM,
            message=f"Anomaly detected in {result.subsystem} (score: {result.anomaly_score:.3f})",
            data={
                "anomaly_score": result.anomaly_score,
                "confidence": result.confidence,
                "algorithm": result.algorithm,
                "features": result.features
            }
        )
        
        # Send to callbacks
        for callback in self.anomaly_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in anomaly callback: {e}")
        
        logger.warning(f"Anomaly detected: {result.subsystem} for UAV {result.uav_id} "
                      f"(score: {result.anomaly_score:.3f})")
    
    def register_anomaly_callback(self, callback: Callable) -> None:
        """Register a callback for anomaly alerts.
        
        Args:
            callback: Async callback function that receives Alert
        """
        self.anomaly_callbacks.append(callback)
        logger.debug("Registered anomaly callback")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics.
        
        Returns:
            Dictionary containing statistics
        """
        stats = self.stats.copy()
        stats["data_windows"] = len(self.data_windows)
        stats["models"] = len(self.models)
        stats["enabled"] = self.enabled
        stats["algorithm"] = self.algorithm
        stats["threshold"] = self.threshold
        
        return stats
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> None:
        """Update anomaly detection configuration.
        
        Args:
            config_updates: Dictionary of configuration updates
        """
        if "enabled" in config_updates:
            self.enabled = config_updates["enabled"]
        
        if "algorithm" in config_updates:
            self.algorithm = config_updates["algorithm"]
            # Recreate all models with new algorithm
            for window_key in self.models.keys():
                self.models[window_key] = self._create_model()
        
        if "threshold" in config_updates:
            self.threshold = config_updates["threshold"]
        
        if "window_size" in config_updates:
            new_window_size = config_updates["window_size"]
            for window_key in self.data_windows.keys():
                old_window = self.data_windows[window_key]
                new_window = deque(maxlen=new_window_size)
                new_window.extend(old_window)
                self.data_windows[window_key] = new_window
            self.window_size = new_window_size
        
        logger.info(f"Updated anomaly detection configuration: {config_updates}")
    
    async def start(self) -> None:
        """Start the anomaly detection system."""
        self.enabled = True
        logger.info("Anomaly detection system started")
    
    async def stop(self) -> None:
        """Stop the anomaly detection system."""
        self.enabled = False
        logger.info("Anomaly detection system stopped")
    
    async def get_recent_alerts(self, uav_id: str, limit: int = 10) -> List[Alert]:
        """Get recent alerts for a specific UAV.
        
        Args:
            uav_id: UAV identifier
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        # Filter alerts by UAV ID and return recent ones
        uav_alerts = [alert for alert in self.alerts if alert.uav_id == uav_id]
        return uav_alerts[-limit:] if uav_alerts else []
