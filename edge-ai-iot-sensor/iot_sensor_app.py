"""
Edge AI Industrial IoT Sensor System
Real-time equipment monitoring and predictive maintenance using edge AI
"""

import numpy as np
import pandas as pd
import time
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import deque, defaultdict
import math
import logging
import os

# Feature flags for logging control
ENABLE_DEBUG_LOGGING = os.getenv('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true'
ENABLE_FLASK_DEBUG = os.getenv('ENABLE_FLASK_DEBUG', 'false').lower() == 'true'

# Configure logging based on feature flags
log_level = logging.DEBUG if ENABLE_DEBUG_LOGGING else logging.WARNING
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Reduce werkzeug (Flask) logging noise
logging.getLogger('werkzeug').setLevel(logging.ERROR if not ENABLE_FLASK_DEBUG else logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot-sensor-demo-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class EquipmentSensor:
    """Represents a single piece of industrial equipment with sensors"""
    
    def __init__(self, equipment_id, equipment_type, location):
        self.equipment_id = equipment_id
        self.equipment_type = equipment_type
        self.location = location
        
        # Sensor data buffers (time series)
        self.vibration_data = deque(maxlen=1000)
        self.temperature_data = deque(maxlen=1000)
        self.pressure_data = deque(maxlen=1000)
        self.current_data = deque(maxlen=1000)
        
        # Equipment state
        self.health_score = 100.0
        self.operating_hours = 0
        self.maintenance_due = False
        self.anomaly_detected = False
        self.predicted_failure_date = None
        
        # Baseline values for normal operation
        self.baseline_vibration = np.random.uniform(0.1, 0.3)
        self.baseline_temperature = np.random.uniform(65, 85)
        self.baseline_pressure = np.random.uniform(45, 55)
        self.baseline_current = np.random.uniform(8, 12)
        
        # Degradation simulation
        self.degradation_factor = 1.0
        self.wear_rate = np.random.uniform(0.001, 0.005)
        
    def generate_sensor_data(self, timestamp):
        """Generate realistic sensor data with potential anomalies"""
        
        # Simulate time-based degradation
        self.operating_hours += 0.1  # 6 minutes per call (0.1 hours)
        self.degradation_factor += self.wear_rate * np.random.uniform(0.5, 2.0)
        
        # Base sensor readings with noise
        vibration = self.baseline_vibration * self.degradation_factor + np.random.normal(0, 0.02)
        temperature = self.baseline_temperature + (self.degradation_factor - 1) * 20 + np.random.normal(0, 1)
        pressure = self.baseline_pressure - (self.degradation_factor - 1) * 5 + np.random.normal(0, 0.5)
        current = self.baseline_current * self.degradation_factor + np.random.normal(0, 0.3)
        
        # Add occasional spikes for demonstration
        if np.random.random() < 0.05:  # 5% chance of anomaly
            vibration *= np.random.uniform(1.5, 3.0)
            temperature += np.random.uniform(10, 25)
        
        # Simulate equipment-specific patterns
        if self.equipment_type == "CNC Machine":
            # CNC machines have cyclic vibration patterns
            cycle_time = (time.time() % 30) / 30  # 30-second cycle
            vibration += 0.1 * math.sin(cycle_time * 2 * math.pi)
            
        elif self.equipment_type == "Pump":
            # Pumps show pressure correlation with current
            pressure = self.baseline_pressure + (current - self.baseline_current) * 2
            
        elif self.equipment_type == "Motor":
            # Motors have temperature correlation with current
            temperature = self.baseline_temperature + (current - self.baseline_current) * 5
        
        # Store data
        sensor_reading = {
            'timestamp': timestamp,
            'vibration': max(0, vibration),
            'temperature': max(0, temperature),
            'pressure': max(0, pressure),
            'current': max(0, current)
        }
        
        self.vibration_data.append(sensor_reading['vibration'])
        self.temperature_data.append(sensor_reading['temperature'])
        self.pressure_data.append(sensor_reading['pressure'])
        self.current_data.append(sensor_reading['current'])
        
        return sensor_reading
    
    def calculate_health_score(self):
        """Calculate equipment health score based on sensor trends"""
        if len(self.vibration_data) < 10:
            return self.health_score
        
        # Get recent data for analysis
        recent_vibration = list(self.vibration_data)[-50:]
        recent_temperature = list(self.temperature_data)[-50:]
        recent_pressure = list(self.pressure_data)[-50:]
        recent_current = list(self.current_data)[-50:]
        
        health_factors = []
        
        # Vibration analysis
        vibration_ratio = np.mean(recent_vibration) / self.baseline_vibration
        vibration_health = max(0, 100 - (vibration_ratio - 1) * 50)
        health_factors.append(vibration_health)
        
        # Temperature analysis
        temp_deviation = abs(np.mean(recent_temperature) - self.baseline_temperature)
        temp_health = max(0, 100 - temp_deviation * 2)
        health_factors.append(temp_health)
        
        # Pressure analysis
        pressure_deviation = abs(np.mean(recent_pressure) - self.baseline_pressure)
        pressure_health = max(0, 100 - pressure_deviation * 3)
        health_factors.append(pressure_health)
        
        # Current analysis
        current_ratio = np.mean(recent_current) / self.baseline_current
        current_health = max(0, 100 - abs(current_ratio - 1) * 60)
        health_factors.append(current_health)
        
        # Overall health score (weighted average)
        self.health_score = np.mean(health_factors)
        
        return self.health_score
    
    def predict_maintenance(self):
        """Predict when maintenance will be needed"""
        if self.health_score > 80:
            self.maintenance_due = False
            self.predicted_failure_date = None
        elif self.health_score > 50:
            # Predict based on degradation trend
            if len(self.vibration_data) > 20:
                recent_scores = []
                for i in range(20):
                    idx = -(20 - i)
                    if idx < 0 and abs(idx) <= len(self.vibration_data):
                        # Calculate historical health for trend
                        score = 100 - (self.vibration_data[idx] / self.baseline_vibration - 1) * 50
                        recent_scores.append(max(0, score))
                
                if len(recent_scores) > 5:
                    # Simple linear trend prediction
                    trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
                    if trend < -0.5:  # Declining health
                        days_to_failure = (self.health_score - 30) / abs(trend)  # 30% threshold
                        self.predicted_failure_date = datetime.now() + timedelta(days=days_to_failure)
                        self.maintenance_due = True
        else:
            # Critical health level
            self.maintenance_due = True
            self.predicted_failure_date = datetime.now() + timedelta(days=7)
            
        return self.maintenance_due, self.predicted_failure_date

class IoTSensorSystem:
    def __init__(self):
        # Initialize equipment fleet
        self.equipment = {
            'CNC_001': EquipmentSensor('CNC_001', 'CNC Machine', 'Production Line A'),
            'PUMP_002': EquipmentSensor('PUMP_002', 'Pump', 'Water System'),
            'MOTOR_003': EquipmentSensor('MOTOR_003', 'Motor', 'Conveyor Belt'),
            'COMP_004': EquipmentSensor('COMP_004', 'Compressor', 'Air System'),
        }
        
        # System statistics
        self.system_stats = {
            'total_equipment': len(self.equipment),
            'healthy_equipment': 0,
            'equipment_needing_maintenance': 0,
            'anomalies_detected': 0,
            'cost_savings': 0,
            'alerts': []
        }
        
        # Anomaly detection models (one per equipment type)
        self.anomaly_models = {}
        self.scalers = {}
        self.training_data = defaultdict(list)
        
        # Initialize models
        self.initialize_anomaly_detection()
        
    def initialize_anomaly_detection(self):
        """Initialize anomaly detection models for each equipment type"""
        equipment_types = set(eq.equipment_type for eq in self.equipment.values())
        
        for eq_type in equipment_types:
            self.anomaly_models[eq_type] = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42
            )
            self.scalers[eq_type] = StandardScaler()
            
    def collect_sensor_data(self):
        """Collect data from all equipment sensors"""
        timestamp = datetime.now()
        all_readings = {}
        
        for eq_id, equipment in self.equipment.items():
            reading = equipment.generate_sensor_data(timestamp)
            all_readings[eq_id] = reading
            
            # Add to training data
            feature_vector = [
                reading['vibration'],
                reading['temperature'], 
                reading['pressure'],
                reading['current']
            ]
            self.training_data[equipment.equipment_type].append(feature_vector)
            
        return all_readings, timestamp
    
    def detect_anomalies(self):
        """Detect anomalies using machine learning models"""
        anomalies_found = []
        
        for eq_id, equipment in self.equipment.items():
            if len(self.training_data[equipment.equipment_type]) > 50:
                # Train/update model with recent data
                training_data = np.array(self.training_data[equipment.equipment_type][-200:])
                
                try:
                    # Fit scaler and model
                    scaled_data = self.scalers[equipment.equipment_type].fit_transform(training_data)
                    self.anomaly_models[equipment.equipment_type].fit(scaled_data)
                    
                    # Check latest reading
                    if len(equipment.vibration_data) > 0:
                        latest_reading = [
                            equipment.vibration_data[-1],
                            equipment.temperature_data[-1],
                            equipment.pressure_data[-1],
                            equipment.current_data[-1]
                        ]
                        
                        scaled_reading = self.scalers[equipment.equipment_type].transform([latest_reading])
                        anomaly_score = self.anomaly_models[equipment.equipment_type].decision_function(scaled_reading)[0]
                        is_anomaly = self.anomaly_models[equipment.equipment_type].predict(scaled_reading)[0] == -1
                        
                        if is_anomaly:
                            equipment.anomaly_detected = True
                            anomaly = {
                                'equipment_id': eq_id,
                                'equipment_type': equipment.equipment_type,
                                'location': equipment.location,
                                'anomaly_score': float(anomaly_score),
                                'timestamp': datetime.now().isoformat(),
                                'sensor_values': {
                                    'vibration': latest_reading[0],
                                    'temperature': latest_reading[1],
                                    'pressure': latest_reading[2],
                                    'current': latest_reading[3]
                                }
                            }
                            anomalies_found.append(anomaly)
                        else:
                            equipment.anomaly_detected = False
                            
                except Exception as e:
                    logger.warning(f"Anomaly detection failed for {eq_id}: {e}")
        
        return anomalies_found
    
    def update_system_stats(self):
        """Update overall system statistics"""
        healthy_count = 0
        maintenance_needed = 0
        total_anomalies = 0
        
        for equipment in self.equipment.values():
            # Calculate health scores
            equipment.calculate_health_score()
            
            # Check maintenance predictions
            equipment.predict_maintenance()
            
            # Update counters
            if equipment.health_score > 80:
                healthy_count += 1
            
            if equipment.maintenance_due:
                maintenance_needed += 1
                
            if equipment.anomaly_detected:
                total_anomalies += 1
        
        # Calculate cost savings (simplified model)
        # Assume each prevented failure saves $10,000
        prevented_failures = max(0, maintenance_needed - total_anomalies)
        cost_savings = prevented_failures * 10000
        
        self.system_stats.update({
            'healthy_equipment': healthy_count,
            'equipment_needing_maintenance': maintenance_needed,
            'anomalies_detected': total_anomalies,
            'cost_savings': cost_savings
        })
        
        return self.system_stats
    
    def get_equipment_status(self):
        """Get detailed status of all equipment"""
        status = {}
        
        for eq_id, equipment in self.equipment.items():
            status[eq_id] = {
                'equipment_type': equipment.equipment_type,
                'location': equipment.location,
                'health_score': round(equipment.health_score, 1),
                'operating_hours': round(equipment.operating_hours, 1),
                'maintenance_due': equipment.maintenance_due,
                'anomaly_detected': equipment.anomaly_detected,
                'predicted_failure_date': equipment.predicted_failure_date.isoformat() if equipment.predicted_failure_date else None,
                'current_readings': {
                    'vibration': equipment.vibration_data[-1] if equipment.vibration_data else 0,
                    'temperature': equipment.temperature_data[-1] if equipment.temperature_data else 0,
                    'pressure': equipment.pressure_data[-1] if equipment.pressure_data else 0,
                    'current': equipment.current_data[-1] if equipment.current_data else 0
                }
            }
            
        return status

# Global system instance
iot_system = IoTSensorSystem()

def sensor_monitoring_loop():
    """Background thread for continuous sensor monitoring"""
    while True:
        try:
            # Collect sensor data
            readings, timestamp = iot_system.collect_sensor_data()
            
            # Detect anomalies
            anomalies = iot_system.detect_anomalies()
            
            # Update statistics
            stats = iot_system.update_system_stats()
            
            # Get equipment status
            equipment_status = iot_system.get_equipment_status()
            
            # Convert datetime objects to ISO format strings in readings
            readings_serializable = {}
            for eq_id, reading in readings.items():
                readings_serializable[eq_id] = {
                    'timestamp': reading['timestamp'].isoformat() if isinstance(reading['timestamp'], datetime) else reading['timestamp'],
                    'vibration': reading['vibration'],
                    'temperature': reading['temperature'],
                    'pressure': reading['pressure'],
                    'current': reading['current']
                }
            
            # Emit real-time updates
            socketio.emit('sensor_update', {
                'readings': readings_serializable,
                'anomalies': anomalies,
                'stats': stats,
                'equipment_status': equipment_status,
                'timestamp': timestamp.isoformat()
            })
            
            time.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            logger.error(f"Error in sensor monitoring loop: {e}")
            time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system_status')
def get_system_status():
    return jsonify({
        'stats': iot_system.system_stats,
        'equipment_status': iot_system.get_equipment_status()
    })

@app.route('/api/equipment/<equipment_id>/history')
def get_equipment_history(equipment_id):
    if equipment_id not in iot_system.equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    equipment = iot_system.equipment[equipment_id]
    
    # Get recent history (last 100 readings)
    history = {
        'vibration': list(equipment.vibration_data)[-100:],
        'temperature': list(equipment.temperature_data)[-100:],
        'pressure': list(equipment.pressure_data)[-100:],
        'current': list(equipment.current_data)[-100:]
    }
    
    return jsonify(history)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to IoT system')
    emit('sensor_update', {
        'stats': iot_system.system_stats,
        'equipment_status': iot_system.get_equipment_status()
    })

if __name__ == '__main__':
    # Start sensor monitoring thread
    monitoring_thread = threading.Thread(target=sensor_monitoring_loop, daemon=True)
    monitoring_thread.start()
    
    print("Starting Edge AI Industrial IoT Sensor System...")
    print("Access dashboard at: http://localhost:5003")
    
    socketio.run(app, host='0.0.0.0', port=5003, debug=ENABLE_FLASK_DEBUG, log_output=ENABLE_FLASK_DEBUG)