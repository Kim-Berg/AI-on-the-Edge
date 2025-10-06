# Edge AI Industrial IoT Sensor 📡

## Overview
This demo showcases an intelligent IoT sensor system that monitors industrial equipment health in real-time using machine learning on the edge. The system predicts maintenance needs, detects anomalies, and prevents costly equipment failures - all without cloud connectivity.

**Port**: http://localhost:5003

## Key Features
- **🔮 Predictive Maintenance**: ML models (Isolation Forest) predict when equipment will need service
- **📊 Real-time Monitoring**: Continuous sensor data analysis on edge devices
- **⚠️ Anomaly Detection**: Instantly identifies unusual patterns in machine behavior
- **💯 Equipment Health Scoring**: AI-powered health assessment of industrial assets
- **🚨 Maintenance Alerts**: Proactive notifications before failures occur
- **⚡ Edge Optimization**: Lightweight models designed for constrained IoT devices
- **📈 Time-Series Analysis**: Vibration, temperature, pressure, and current monitoring
- **🏭 Industrial Protocols**: MQTT simulation and sensor data streaming
- **💰 Cost Savings Tracking**: ROI calculations for predictive maintenance

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
[Vibration,   [ML Models:         [Predictive
Temperature,   Isolation           Maintenance
Pressure,      Forest for          Scheduling &
Current] →     Anomaly             Alerts]
               Detection] →
```

## Technology Stack
- **Edge Computing**: Real-time inference on industrial gateways
- **Time Series Analysis**: Advanced signal processing and feature extraction
- **Machine Learning**: 
  - Isolation Forest for anomaly detection
  - Statistical analysis for trend detection
  - Health scoring algorithms
- **Industrial IoT**: 
  - MQTT broker simulation
  - Real-time sensor data streaming
  - Alert management system
- **Dashboard**: Flask with SocketIO for real-time visualization
- **Data Processing**: NumPy, Pandas, scikit-learn

## Prerequisites

### Software Requirements
- **Python 3.8+** - Required
  ```bash
  python --version
  ```

### Python Dependencies
All dependencies are in `requirements.txt`:
- **flask>=2.3.0** - Web framework
- **numpy>=1.24.0** - Numerical computing
- **pandas>=2.0.0** - Data manipulation
- **scikit-learn>=1.3.0** - Machine learning (Isolation Forest)
- **scipy>=1.10.0** - Scientific computing
- **matplotlib>=3.7.0** - Plotting
- **plotly>=5.15.0** - Interactive visualizations
- **flask-socketio>=5.0.0** - Real-time updates
- **paho-mqtt>=1.6.0** - MQTT protocol support

## Getting Started

### Automated Setup (Recommended)

From the main workspace directory:
```bash
./start_all_demos.sh
```

This will automatically:
- Create virtual environment
- Install all dependencies
- Launch the IoT sensor demo on http://localhost:5003

### Manual Setup

1. **Navigate to the demo folder**
   ```bash
   cd edge-ai-iot-sensor
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the IoT sensor system**
   ```bash
   python iot_sensor_app.py
   ```

5. **Open dashboard**
   Navigate to http://localhost:5003

## Demo Script

### Interactive Demo Flow

1. **Show normal equipment operation** with healthy sensors
   - Point out the health scores (near 100%)
   - Show real-time sensor data visualization
   - Explain the four monitored parameters (vibration, temperature, pressure, current)

2. **Introduce gradual degradation patterns**
   - Equipment health scores begin to decline
   - Anomaly detection flags unusual patterns
   - Watch as ML model identifies early warning signs

3. **Demonstrate early anomaly detection**
   - System detects issues before catastrophic failure
   - Maintenance alerts triggered automatically
   - Show cost savings calculations

4. **Show maintenance predictions and cost savings**
   - Predicted failure dates displayed
   - ROI calculations for preventive vs reactive maintenance
   - Equipment status transitions (healthy → warning → critical)

5. **Simulate equipment failure prevention**
   - Show how early intervention prevents downtime
   - Demonstrate 40-60% reduction in unplanned maintenance
   - Cost benefit analysis

### Key Talking Points

- **Latency**: <100ms inference time on edge devices
- **Privacy**: Sensor data never leaves the device
- **Offline capability**: Works without internet connection
- **Scalability**: Deploy across hundreds of assets independently
- **Cost savings**: Optimize maintenance schedules, reduce spare parts inventory
- **Safety**: Early detection of potential hazardous conditions

## Project Structure

```
edge-ai-iot-sensor/
├── iot_sensor_app.py       # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Dashboard interface
└── README.md              # This file
```

## Features in Detail

### Equipment Monitoring
- **Multi-equipment support**: Monitor multiple machines simultaneously
- **Sensor types**: Vibration, temperature, pressure, current
- **Real-time data**: Streaming sensor data with SocketIO
- **Health scoring**: AI-powered equipment health assessment (0-100%)

### Anomaly Detection
- **Isolation Forest ML**: Unsupervised learning for anomaly detection
- **Threshold-based alerts**: Configurable warning and critical thresholds
- **Pattern recognition**: Identifies unusual trends in sensor data
- **Early warning system**: Alerts before critical failures

### Predictive Maintenance
- **Failure prediction**: Estimates when equipment will need service
- **Operating hours tracking**: Monitors equipment usage
- **Maintenance scheduling**: Suggests optimal maintenance windows
- **Cost optimization**: Reduces unplanned downtime by 40-60%

## Troubleshooting

### Common Issues

**Port 5003 already in use**
- Stop other applications using port 5003
- Or modify the port in `iot_sensor_app.py` (line 435): change `port=5003`

**Import errors or missing dependencies**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

**SocketIO connection issues**
- Check firewall settings
- Ensure Flask-SocketIO is properly installed
- Try accessing from localhost (not 127.0.0.1)

**Sensor data not updating**
- Check browser console for JavaScript errors
- Refresh the page
- Ensure the Flask app is running without errors

## Technical Details

### ML Model
The system uses **Isolation Forest** algorithm for anomaly detection:
- Unsupervised learning approach
- Effective for detecting outliers in high-dimensional data
- Low computational overhead for edge deployment
- Real-time inference with <10ms latency

### Data Flow
1. Sensor simulator generates realistic equipment data
2. Data flows through feature extraction
3. Isolation Forest model scores each sample
4. Health score calculated based on anomaly scores and thresholds
5. Real-time updates pushed to dashboard via WebSocket
6. Alerts triggered when thresholds exceeded

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Learn More

- [scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Predictive Maintenance Best Practices](https://learn.microsoft.com/en-us/azure/architecture/industries/manufacturing/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)

---

**Built for industrial IoT edge computing scenarios**

*Prevent failures before they happen with AI-powered predictive maintenance!*