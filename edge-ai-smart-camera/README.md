# Edge AI Smart Surveillance Camera

## Overview
This demo showcases an intelligent surveillance camera system that runs AI models locally on edge devices. The system performs real-time object detection, person tracking, and anomaly detection without requiring cloud connectivity.

## Key Features
- **Real-time Object Detection**: Identifies people, vehicles, and objects instantly
- **Anomaly Detection**: Spots unusual behavior patterns and potential security threats
- **Person Tracking**: Follows individuals across camera frames
- **Privacy-First**: All processing happens locally - no video sent to cloud
- **Edge Optimization**: Lightweight models optimized for edge hardware
- **Instant Alerts**: <50ms detection to alert generation
- **Zone Monitoring**: Configure specific areas for enhanced surveillance

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

## Architecture
```
[Camera Feed] → [Edge AI Processor] → [Local Alerts & Dashboard]
      ↓              ↓                         ↓
[Live Video] → [Object Detection] → [Security Integration]
      ↓              ↓                         ↓  
[Frames] → [Anomaly Detection] → [Real-time Notifications]
```

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Connect camera or use test video: `python smart_camera_app.py`
3. Open dashboard at `http://localhost:5001`
4. Configure detection zones and alert thresholds

## Demo Features
- Live video processing with AI overlays
- Real-time detection statistics
- Configurable alert zones
- Person counting and tracking
- Anomaly detection alerts
- Security event logging