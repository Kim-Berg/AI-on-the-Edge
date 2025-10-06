# 🤖 Azure AI Quality Control Demo

An AI-powered quality control system for manufacturing that integrates with **Azure AI Foundry Local** for defect detection using computer vision and machine learning.

**Port**: http://localhost:5000

## 🌟 Features

- **🤖 AI Integration**: Uses Azure AI Foundry Local for defect analysis
- **👁️ Vision Analysis**: Supports multimodal AI models for image inspection  
- **⚡ Processing**: Live defect detection with SocketIO updates
- **📊 Dashboard**: Web interface with live statistics and AI status
- **🔄 Fallback Mode**: Graceful simulation mode when AI unavailable
- **🎯 Production Simulation**: Realistic manufacturing production flow
- **💾 MQTT Integration**: Industrial protocol support for IoT integration
- **📈 Quality Metrics**: Pass/fail rates and defect tracking
- **🏭 Batch Processing**: Simulates continuous production batches

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **Azure AI Foundry Local** (Optional - for full AI functionality)
   ```bash
   # Using Windows Package Manager
   winget install Microsoft.AIFoundry
   ```
   *Note: Demo works in simulation mode if Foundry Local is not available*

3. **Python Dependencies** - All in `requirements.txt`:
   - **flask>=2.3.0** - Web framework
   - **opencv-python>=4.8.0** - Computer vision
   - **numpy>=1.24.0** - Numerical computing
   - **pillow>=10.0.0** - Image processing
   - **torch>=2.0.0** - PyTorch for AI models
   - **torchvision>=0.15.0** - Vision models
   - **flask-socketio>=5.0.0** - Real-time updates
   - **paho-mqtt>=1.6.0** - MQTT protocol
   - **requests>=2.31.0** - HTTP client
   - **tensorflow>=2.13.0** - TensorFlow (alternative AI framework)
   - **ultralytics>=8.0.0** - YOLO object detection

### Automated Setup (Recommended)

From the main workspace directory:
```bash
./start_all_demos.sh
```

This will automatically:
- Check and start Azure AI Foundry Local if available
- Create virtual environment
- Install all dependencies
- Launch the quality control demo on http://localhost:5000

### Manual Setup

1. **Start Azure AI Foundry Local** (optional - demo works without it)
   ```bash
   foundry service start
   foundry service status
   ```

2. **Navigate to the demo folder**
   ```bash
   cd edge-ai-quality-control
   ```

3. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the AI-enhanced quality control system**
   ```bash
   python azure_ai_quality_control.py
   ```

6. **Open the dashboard**
   Navigate to http://localhost:5000

## 🎯 Azure AI Foundry Local Integration

The system automatically detects and connects to Azure AI Foundry Local using the official SDK. When available, it uses real AI models for defect detection. When not available, it gracefully falls back to simulation mode.

### Supported Models
The demo attempts to use available Foundry Local models:
- **phi-3.5-mini-instruct** - Efficient text and image analysis
- **phi-4** - Advanced reasoning capabilities
- **qwen2.5** variants - Multilingual support
- *Falls back to simulation if no models available*

### AI Detection Process
1. System checks for Foundry Local SDK availability
2. Attempts to connect to Foundry Local service
3. Loads available multimodal models
4. Processes product images through AI vision analysis
5. Provides defect detection and quality assessment
6. Falls back to statistical simulation if AI unavailable

## 🕹️ Usage Instructions

1. **Launch**: Access http://localhost:5000 in your browser
2. **Check AI Status**: Green indicator = AI connected, Yellow = Simulation mode
3. **Start Production**: Click "Start Production" button
4. **Monitor**: Watch real-time defect detection with AI insights
5. **View Statistics**: See pass/fail rates, defect counts, batch progress
6. **Stop**: Press `Ctrl+C` in terminal or click "Stop Production"

### Dashboard Features
- **Statistics**: Total processed, defects found, pass/fail rates
- **Batch Progress**: Current batch number and item progress
- **AI Status Indicator**: Shows connection status to Foundry Local
- **Recent Results**: Scrolling list of recent inspection results
- **Live Updates**: WebSocket-powered updates

## 📁 Project Structure

```
edge-ai-quality-control/
├── azure_ai_quality_control.py    # Main AI-powered application
├── start_azure_foundry.py         # Foundry startup helper (if needed)
├── requirements.txt               # Python dependencies
├── templates/
│   └── index.html                 # Web dashboard
└── README.md                      # This file
```

## 🔧 Troubleshooting

### Common Issues

**Azure AI Foundry Local Issues**
1. Ensure Azure AI Foundry Local is running: `foundry service status`
2. Check foundry-local-sdk is installed: `pip install foundry-local-sdk`
3. Verify models are available via Foundry Local Manager
4. System automatically falls back to simulation mode if needed

**Port 5000 already in use**
- Stop other applications using port 5000
- Or modify the port in `azure_ai_quality_control.py` (line 1091): change `port=5000`

**Import or dependency errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)
- Some packages like torch may require specific installation for your platform

**SocketIO connection issues**
- Check browser console for errors
- Ensure Flask-SocketIO is installed correctly
- Try accessing from localhost instead of 127.0.0.1
- Check firewall settings

**OpenCV or torch installation issues**
- **Windows**: May need Visual C++ redistributables
- **Linux**: May need additional system packages: `sudo apt-get install python3-opencv`
- **macOS**: Use `pip install opencv-python-headless` if GUI issues occur
- For torch: Visit https://pytorch.org/ for platform-specific installation

### Getting Help

**Connection errors**
- Restart Azure AI Foundry Local service
- Check service endpoint availability
- Demo works in simulation mode without AI

**Model loading issues**
- Check available models in Foundry Local interface
- Some models may not support vision tasks
- System falls back to simulation automatically

**Performance issues**
- Close other resource-intensive applications
- Reduce batch size in code if needed
- Check system has sufficient RAM (8GB+ recommended)

## Technical Details

### Architecture

```
[Web Dashboard] ←→ [Flask App (Port 5000)]
                         ↓
                   [Quality Control Engine]
                         ↓
            ┌────────────┴────────────┐
            ↓                         ↓
    [Azure AI Foundry Local]    [Simulation Mode]
    (Vision AI Analysis)        (Statistical Detection)
            ↓                         ↓
    [Defect Detection Results]
```

### Detection Process
1. Generate simulated product images or use test images
2. Send images to AI vision model (if available)
3. Analyze for defects, scratches, discoloration
4. Calculate quality score and pass/fail decision
5. Update dashboard with real-time results via WebSocket
6. Track statistics and batch progress

### Performance Metrics
- **Inference time**: Varies by mode (AI: 200-500ms, Simulation: <50ms)
- **Throughput**: 2-5 items per second
- **Accuracy**: Depends on AI model quality
- **Latency**: <100ms dashboard updates via WebSocket

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Learn More

- [Azure AI Foundry Local Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Quality Control with AI Best Practices](https://learn.microsoft.com/en-us/azure/architecture/industries/manufacturing/)

---

**Built for manufacturing quality control edge computing scenarios**

*Detect defects in real-time with AI-powered vision analysis!*