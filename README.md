# Edge AI Demo Collection

Welcome to the Edge AI demo collection! These demos showcase how to run AI models locally on edge devices for industrial IoT applications.

## 🚀 Quick Start

**Want to run the demos right now?** → **[DEMO_INSTRUCTIONS.md](./DEMO_INSTRUCTIONS.md)**

## 📋 Available Demos

### 1. Quality Control System 🔍
**Path**: `edge-ai-quality-control/`  
**URL**: http://localhost:5000

AI-powered quality control with Azure AI Foundry Local integration.
- 🤖 Real Azure AI model integration for defect analysis
- �️ Vision analysis with multimodal AI models
- ⚡ Real-time defect detection and processing
- � Live quality metrics dashboard
- 🔄 Intelligent fallback to simulation mode
- 🏭 Manufacturing production simulation

### 2. Azure Foundry Local Chat 🤖
**Path**: `edge-ai-foundrylocal-chat-playground/`  
**URL**: http://localhost:5001

Multi-model AI chat application with real-time streaming via REST API.
- 💬 Interactive chat with multiple AI models simultaneously
- 🔄 Side-by-side model comparison
- ⚡ Real-time response streaming
- 🏠 100% local processing via Foundry Local service
- 📊 Chat history management
- 🤖 Supports Qwen, Phi, Llama, Gemma, Mistral models

### 3. Smart Surveillance Camera 📹
**Path**: `edge-ai-smart-camera/`  
**URL**: http://localhost:5002

Intelligent video surveillance with edge AI processing.
- 🎥 Real-time object detection (people, vehicles, objects)
- 👥 Person tracking and counting
- 🚨 Anomaly detection and loitering alerts
- 🔒 Privacy-preserving local processing
- ⚡ <50ms detection latency
- 📊 Live statistics and security event logging

### 4. Industrial IoT Sensors 📡
**Path**: `edge-ai-iot-sensor/`  
**URL**: http://localhost:5003

Predictive maintenance for industrial equipment using edge AI.
- 🏭 Multi-equipment health monitoring
- 🔮 ML-based predictive maintenance (Isolation Forest)
- ⚠️ Real-time anomaly detection on sensor data
- � Time-series analysis (vibration, temperature, pressure)
- �💰 Cost savings tracking and ROI calculations
- 📊 Live dashboard with equipment status

### 5. Windows AI Foundry Demo 🪟
**Path**: `edge-ai-windows-foundry/`  
**URL**: http://localhost:5004

Comprehensive showcase of Windows AI Foundry capabilities across 8 AI domains.
- 🤖 Real AI processing with 7+ local models
- 📝 Text generation & creative writing
- 💻 Code assistance & development help
- 📄 Document analysis & summarization
- 🧠 Advanced reasoning capabilities
- 🌍 Translation and multimodal analysis
- 🔄 Intelligent timeout & retry handling
- 🔌 Real-time connection monitoring

### Key Demo Benefits
- 🚀 **Lightning Fast**: <100ms response times for critical applications
- 🔒 **Privacy First**: All data processed locally, never leaves the device
- 💰 **Cost Effective**: No cloud bandwidth or API costs
- 🔋 **Always On**: Full functionality during internet outages
- 📈 **Scalable**: Deploy independently across hundreds of devices
- 🤖 **Real AI**: Powered by Azure AI Foundry Local with actual AI models

## 🎤 Demo Presentation Guide

### Suggested Demo Flow (15-20 minutes)
1. **Overview** (2 min) - Introduce edge AI concept and demo collection
2. **Quality Control** (5 min) - Show Azure AI integration and defect detection
3. **Smart Camera** (4 min) - Demonstrate video analytics and object detection
4. **IoT Sensors** (4 min) - Present predictive maintenance and anomaly detection
5. **Windows AI Foundry** (3 min) - Showcase comprehensive AI capabilities
6. **Q&A** (2 min) - Address questions

### Key Talking Points
- **Latency comparison**: Edge (<100ms) vs Cloud (200-500ms)
- **Privacy & Compliance**: Data never leaves premises
- **Offline capability**: Disconnect internet to show continued operation
- **Cost savings**: No per-request API fees, reduced bandwidth costs
- **Real AI models**: Actual Azure AI Foundry Local integration, not simulation
- **Industrial applications**: Manufacturing, IoT, surveillance use cases

## 🛠️ Technical Stack

- **Edge AI**: Lightweight ML models optimized for edge devices
- **Azure AI Foundry Local**: Local AI model serving and inference
- **Real-time Processing**: <100ms inference using local compute
- **Computer Vision**: OpenCV, YOLO, MobileNet SSD for object detection
- **Machine Learning**: scikit-learn (Isolation Forest) for anomaly detection
- **Industrial Protocols**: MQTT, simulated OPC-UA integration
- **Web Framework**: Flask with SocketIO for real-time updates
- **Frontend**: Modern responsive HTML/CSS/JavaScript
- **Cross-Platform**: Works on Windows, macOS, Linux

## 📦 Prerequisites

- **Python 3.8+** - Required for all demos
- **Windows AI Foundry Local** - Required for full AI capabilities
  ```bash
  winget install Microsoft.AIFoundry
  ```
- **Git** - For cloning the repository
- **Virtual Environment Support** - Python venv (included with Python)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AI on the Edge"
   ```

2. **Start all demos at once**
   ```bash
   # Make scripts executable (first time only - Linux/macOS)
   chmod +x start_all_demos.sh stop_all_demos.sh
   
   # Start all demos
   ./start_all_demos.sh
   ```

3. **Access the demos** - Open your browser to the URLs listed above

4. **Stop all demos**
   ```bash
   ./stop_all_demos.sh
   ```

For detailed setup instructions, see **[DEMO_INSTRUCTIONS.md](./DEMO_INSTRUCTIONS.md)**

## 📚 Learn More

Each demo includes:
- 📖 Detailed README with use cases
- 🔧 Setup instructions
- 💡 Architecture explanations
- 🎯 Business value propositions

---

**Ready to bring intelligence to the edge?** Start with the **[DEMO_SETUP_GUIDE.md](./DEMO_SETUP_GUIDE.md)** 🚀