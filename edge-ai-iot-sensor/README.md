# Edge AI Industrial IoT Sensor

## Overview
This demo showcases an intelligent IoT sensor system that monitors industrial equipment health in real-time. The edge AI system predicts maintenance needs, detects anomalies, and prevents costly equipment failures - all without cloud connectivity.

## Key Features
- **Predictive Maintenance**: ML models predict when equipment will need service
- **Real-time Monitoring**: Continuous sensor data analysis on edge devices
- **Anomaly Detection**: Instantly identifies unusual patterns in machine behavior
- **Equipment Health Scoring**: AI-powered health assessment of industrial assets
- **Maintenance Alerts**: Proactive notifications before failures occur
- **Edge Optimization**: Lightweight models designed for constrained IoT devices
- **Industrial Protocols**: MQTT, OPC-UA, and Modbus integration

## Industrial Use Cases

### Manufacturing Equipment
- **CNC Machines**: Monitor spindle vibration, temperature, cutting tool wear
- **Conveyor Belts**: Detect bearing failures, belt tension issues
- **Pumps & Compressors**: Track pressure variations, flow anomalies
- **Motors**: Analyze current signatures, vibration patterns

### Oil & Gas
- **Drilling Equipment**: Monitor drilling parameters, equipment stress
- **Pipeline Systems**: Detect leaks, pressure anomalies
- **Refineries**: Process optimization, safety monitoring

### Utilities
- **Power Generation**: Turbine monitoring, generator health
- **Water Treatment**: Pump efficiency, filter condition monitoring
- **HVAC Systems**: Energy optimization, equipment lifecycle

## Real-World Benefits
- **Prevent Downtime**: 40-60% reduction in unplanned maintenance
- **Cost Savings**: Optimize maintenance schedules, reduce spare parts inventory
- **Safety**: Early detection of potential hazardous conditions
- **Efficiency**: Maximize equipment lifespan and performance
- **Scalability**: Deploy across hundreds of assets independently

## Architecture
```
[Sensors] → [Edge AI Gateway] → [Maintenance Dashboard]
     ↓             ↓                    ↓
[Vibration,   [ML Models      [Predictive
Temperature,   Anomaly         Maintenance
Pressure] →    Detection] →    Scheduling]
```

## Technology Stack
- **Edge Computing**: Real-time inference on industrial gateways
- **Time Series Analysis**: Advanced signal processing and feature extraction
- **Machine Learning**: Isolation Forest, LSTM, AutoEncoders for anomaly detection
- **Industrial IoT**: MQTT broker, sensor simulation, alert management
- **Dashboard**: Real-time visualization of equipment health and predictions

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Run the IoT sensor system: `python iot_sensor_app.py`
3. Open dashboard at `http://localhost:5002`
4. Monitor simulated equipment or connect real sensors

## Demo Script
1. Show normal equipment operation with healthy sensors
2. Introduce gradual degradation patterns
3. Demonstrate early anomaly detection
4. Show maintenance predictions and cost savings
5. Simulate equipment failure prevention