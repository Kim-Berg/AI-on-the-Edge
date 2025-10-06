# Edge AI Smart Surveillance Camera 📹

## Overview
This demo showcases an intelligent surveillance camera system that runs AI models locally on edge devices. The system performs real-time object detection, person tracking, and anomaly detection without requiring cloud connectivity.

**Port**: http://localhost:5002

## Key Features
- **🎥 Real-time Object Detection**: Identifies people, vehicles, and objects instantly using computer vision
- **⚡ Ultra-Low Latency**: <50ms detection to alert generation
- **🚶 Person Tracking**: Follows individuals across camera frames with unique IDs
- **🚨 Anomaly Detection**: Spots unusual behavior patterns and potential security threats
- **🔒 Privacy-First**: All processing happens locally - no video sent to cloud
- **⚡ Edge Optimization**: Lightweight models optimized for edge hardware
- **📊 Live Statistics**: Real-time detection counts and FPS monitoring
- **🎯 Zone Monitoring**: Configurable detection areas for enhanced surveillance
- **💾 Event Logging**: Security event history with timestamps
- **📈 Performance Metrics**: Processing time tracking and analytics

## Use Cases
Perfect for various security and monitoring scenarios:

1. **Building Security**: Monitor entrances, detect unauthorized access
2. **Perimeter Protection**: Alert on fence climbing, loitering
3. **Traffic Monitoring**: Count vehicles, detect accidents
4. **Retail Analytics**: Customer flow analysis, theft prevention
5. **Industrial Safety**: PPE compliance, restricted area monitoring

## Real-World Benefits
- **Ultra-Low Latency**: Instant response without cloud round-trips
- **Privacy Compliant**: Video never leaves the premises
- **Cost Effective**: No bandwidth costs for video streaming
- **Always Available**: Works during internet outages
- **Scalable**: Hundreds of cameras with independent processing

## Use Cases
Perfect for various security and monitoring scenarios:

1. **🏢 Building Security**: Monitor entrances, detect unauthorized access, visitor tracking
2. **🚧 Perimeter Protection**: Alert on fence climbing, loitering, restricted area access
3. **🚗 Traffic Monitoring**: Count vehicles, detect accidents, parking violations
4. **🛒 Retail Analytics**: Customer flow analysis, theft prevention, queue management
5. **🏭 Industrial Safety**: PPE compliance, restricted area monitoring, hazard detection
6. **🏠 Smart Home Security**: Intruder detection, package monitoring, pet tracking

## Real-World Benefits
- **⚡ Ultra-Low Latency**: Instant response without cloud round-trips (<50ms)
- **🔒 Privacy Compliant**: Video never leaves the premises (GDPR, HIPAA compliant)
- **💰 Cost Effective**: No bandwidth costs for video streaming to cloud
- **🔋 Always Available**: Works during internet outages and network failures
- **📈 Scalable**: Deploy hundreds of cameras with independent processing
- **🎯 Accurate**: Advanced AI models for reliable detection

## Architecture
```
[Camera Feed/Simulation] → [Edge AI Processor] → [Dashboard & Alerts]
           ↓                       ↓                      ↓
      [Live Video] →    [Object Detection:          [Security
                         MobileNet SSD/YOLO]         Integration]
           ↓                       ↓                      ↓  
      [Frames] →        [Person Tracking &       [Real-time
                         Anomaly Detection] →     Notifications]
```

## Technology Stack
- **Computer Vision**: OpenCV for image processing and video handling
- **Object Detection**: 
  - MobileNet SSD v2 (lightweight, fast)
  - YOLO v4-tiny (alternative, more accurate)
- **Deep Learning**: PyTorch, TorchVision for model inference
- **Real-time Updates**: Flask-SocketIO for WebSocket communication
- **Web Framework**: Flask for dashboard and API
- **Data Processing**: NumPy for numerical operations

## Prerequisites

### Software Requirements
- **Python 3.8+** - Required
  ```bash
  python --version
  ```

### Python Dependencies
All dependencies are in `requirements.txt`:
- **flask>=2.3.0** - Web framework
- **opencv-python>=4.8.0** - Computer vision library
- **numpy>=1.24.0** - Numerical computing
- **pillow>=10.0.0** - Image processing
- **torch>=2.0.0** - PyTorch deep learning
- **torchvision>=0.15.0** - Vision models
- **ultralytics>=8.0.0** - YOLO implementation
- **flask-socketio>=5.0.0** - Real-time updates
- **paho-mqtt>=1.6.0** - MQTT protocol support
- **scikit-learn>=1.3.0** - Machine learning utilities
- **matplotlib>=3.7.0** - Plotting (optional)

### Pre-trained Models
The demo includes pre-trained models in the `models/` directory:
- `mobilenet_ssd_v2_coco_2018_03_29.pb` - TensorFlow model
- `mobilenet_ssd_v2_coco_2018_03_29.pbtxt` - Model configuration
- `yolov4-tiny.weights` - YOLO weights
- `yolov4-tiny.cfg` - YOLO configuration
- `coco.names` - Object class names

*Note: Models are included in the repository. No additional downloads needed.*

## Getting Started

### Automated Setup (Recommended)

From the main workspace directory:
```bash
./start_all_demos.sh
```

This will automatically:
- Create virtual environment
- Install all dependencies
- Launch the smart camera demo on http://localhost:5002

### Manual Setup

1. **Navigate to the demo folder**
   ```bash
   cd edge-ai-smart-camera
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

4. **Run the smart camera system**
   ```bash
   python smart_camera_app.py
   ```

5. **Open dashboard**
   Navigate to http://localhost:5002

## Demo Features

### Live Demo Capabilities
- **Simulated Video Feed**: Generates realistic camera footage with moving objects
- **Real-time Detection**: Detects people, vehicles, and objects in video stream
- **Person Counting**: Tracks number of people currently in view
- **Alert System**: Triggers alerts for anomalies and security events
- **Performance Monitoring**: Displays FPS and processing time
- **Statistics Dashboard**: Total detections, people count, vehicle count
- **Event History**: Scrolling list of recent detection events

### Detection Classes
The system can detect and classify:
- 👤 **People**: Pedestrians, workers, visitors
- 🚗 **Vehicles**: Cars, trucks, motorcycles, bicycles
- 📦 **Objects**: Bags, packages, equipment
- 🐕 **Animals**: Pets, wildlife (using COCO dataset classes)

### Tracking Features
- **Unique ID Assignment**: Each person gets a tracking ID
- **Movement Tracking**: Follows individuals across frames
- **Dwell Time**: Monitors how long people stay in view
- **Loitering Detection**: Alerts when people remain too long in restricted areas

## Demo Script

### Interactive Demo Flow

1. **Show live detection** with simulated camera feed
   - Point out real-time object detection boxes
   - Show person tracking with IDs
   - Explain the detection confidence scores

2. **Explain privacy benefits**
   - All processing happens on the edge device
   - No video sent to cloud
   - GDPR/HIPAA compliant

3. **Demonstrate alert system**
   - Show anomaly detection triggers
   - Security event logging
   - Real-time notifications

4. **Show performance metrics**
   - <50ms detection latency
   - 15-30 FPS processing rate
   - Real-time statistics updates

5. **Compare to cloud-based systems**
   - Edge: <50ms latency
   - Cloud: 200-500ms latency
   - No bandwidth costs
   - Works offline

## Project Structure

```
edge-ai-smart-camera/
├── smart_camera_app.py         # Main Flask application
├── requirements.txt            # Python dependencies
├── models/                     # Pre-trained AI models
│   ├── mobilenet_ssd_v2_coco_2018_03_29.pb
│   ├── mobilenet_ssd_v2_coco_2018_03_29.pbtxt
│   ├── yolov4-tiny.weights
│   ├── yolov4-tiny.cfg
│   └── coco.names
├── templates/
│   └── index.html             # Dashboard interface
└── README.md                  # This file
```

## Troubleshooting

### Common Issues

**Port 5002 already in use**
- Stop other applications using port 5002
- Or modify the port in `smart_camera_app.py` (line 682): change `port=5002`

**Import errors or missing dependencies**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

**OpenCV installation issues**
- **Windows**: May need Visual C++ redistributables
- **Linux**: `sudo apt-get install python3-opencv libopencv-dev`
- **macOS**: Use `pip install opencv-python-headless` if GUI issues
- Alternative: `pip install opencv-contrib-python`

**PyTorch/YOLO model loading errors**
- Ensure model files are present in `models/` directory
- Check file permissions (read access required)
- Verify model files aren't corrupted
- Try re-downloading models if needed

**Low FPS or performance issues**
- Close other resource-intensive applications
- Use lighter model (MobileNet SSD instead of YOLO)
- Reduce video resolution in code
- Check system has sufficient RAM (8GB+ recommended)

**SocketIO connection issues**
- Check browser console for JavaScript errors
- Ensure Flask-SocketIO is properly installed
- Try accessing from localhost (not 127.0.0.1)
- Check firewall settings

**Video feed not displaying**
- Check browser console for errors
- Ensure OpenCV is properly installed
- Video simulation may take a moment to initialize
- Refresh the page

## Technical Details

### Detection Pipeline
1. **Frame Capture**: Get video frames (simulated or real camera)
2. **Preprocessing**: Resize and normalize images for model input
3. **Inference**: Run detection model (MobileNet SSD or YOLO)
4. **Post-processing**: Filter low-confidence detections, apply NMS
5. **Tracking**: Associate detections with existing tracks
6. **Anomaly Detection**: Analyze patterns for unusual behavior
7. **Alerts**: Generate alerts for security events
8. **Dashboard Update**: Push results to web interface via WebSocket

### Performance Metrics
- **Inference time**: 30-50ms per frame (MobileNet SSD)
- **FPS**: 15-30 frames per second
- **Latency**: <50ms from detection to alert
- **Throughput**: Processes ~20-30 frames/second
- **Memory**: ~500MB-1GB RAM usage

### Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| MobileNet SSD | ~30MB | ⚡⚡⚡ | ⭐⭐⭐ | Real-time, resource-constrained |
| YOLO v4-tiny | ~23MB | ⚡⚡ | ⭐⭐⭐⭐ | Better accuracy, still fast |
| YOLO v4 | ~250MB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum accuracy |

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Learn More

- [OpenCV Documentation](https://docs.opencv.org/)
- [YOLO Object Detection](https://github.com/ultralytics/ultralytics)
- [MobileNet SSD](https://github.com/tensorflow/models/tree/master/research/object_detection)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Computer Vision Best Practices](https://learn.microsoft.com/en-us/azure/architecture/guide/ai/computer-vision-inference)

---

**Built for intelligent surveillance edge computing scenarios**

*Real-time object detection and tracking without compromising privacy!*