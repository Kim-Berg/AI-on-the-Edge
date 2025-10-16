Welcome to the Edge AI demo collection! These demos showcase how to run AI models locally on edge devices and some industrial IoT applications.

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

Multi-model AI chat application with streaming via REST API.
- 💬 Interactive chat with multiple AI models simultaneously
- 🔄 Side-by-side model comparison
- ⚡ Response streaming
- 🏠 Local processing via Foundry Local service
- 📊 Chat history management
- 🤖 Supports Qwen, Phi, Llama, Gemma, Mistral models

### 3. Smart Surveillance Camera 📹
**Path**: `edge-ai-smart-camera/`  
**URL**: http://localhost:5002

Intelligent video surveillance with edge AI processing.
- 🎥 Object detection (people, vehicles, objects)
- 👥 Person tracking and counting
- 🚨 Anomaly detection and loitering alerts
- 🔒 Privacy-preserving local processing
- ⚡ Low-latency detection on edge devices
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
- 🤖 AI processing with 7+ local models
- 📝 Text generation & creative writing
- 💻 Code assistance & development help
- 📄 Document analysis & summarization
- 🧠 Advanced reasoning capabilities
- 🌍 Translation and multimodal analysis
- 🔄 Timeout & retry handling
- 🔌 Connection monitoring

### 6. RAG Document Search 📚
**Path**: `edge-ai-rag-document-search/`  
**URL**: http://localhost:5005

Intelligent document search and Q&A using Retrieval-Augmented Generation.
- 📄 Upload and process text documents
- 🔍 Semantic search with sentence embeddings
- 🤖 AI-powered question answering with RAG
- 📊 Source citations and relevance scores
- 🧩 Intelligent document chunking
- 💾 Persistent storage of documents and embeddings
- ⚡ Real-time search and answer generation
- 🏠 Local processing with Windows AI Foundry

### Key Demo Benefits
- 🚀 **Fast Processing**: Low-latency response times with local inference
- 🔒 **Privacy First**: Data processed locally, doesn't leave the device
- 💰 **Cost Effective**: No cloud bandwidth or API costs
- 🔋 **Offline Capable**: Functionality during internet outages
- 📈 **Scalable**: Deploy independently across multiple devices
- 🤖 **Local AI**: Powered by Azure AI Foundry Local with AI models

## 🛠️ Technical Stack

- **Edge AI**: Lightweight ML models optimized for edge devices
- **Azure AI Foundry Local**: Local AI model serving and inference
- **Computer Vision**: OpenCV, YOLO, MobileNet SSD for object detection
- **Machine Learning**: scikit-learn (Isolation Forest) for anomaly detection
- **RAG & Embeddings**: Sentence Transformers for semantic search and retrieval
- **Industrial Protocols**: MQTT, simulated OPC-UA integration
- **Web Framework**: Flask with SocketIO for updates
- **Frontend**: Responsive HTML/CSS/JavaScript
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