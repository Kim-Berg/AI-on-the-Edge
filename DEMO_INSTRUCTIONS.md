# 🚀 AI on the Edge Demo Instructions

This workspace contains multiple AI demos showcasing local AI processing capabilities. Each demo demonstrates different aspects of edge computing and local AI inference.

## 🎯 Quick Start - Run All Demos

**Prerequisites:**
- Python 3.8+ installed
- **Foundry Local service** installed (for full functionality)
  ```bash
  # Install Foundry Local (if not already installed)
  winget install Microsoft.AIFoundry
  ```

To start all demos at once with one command:

```bash
# Make scripts executable (first time only)
chmod +x start_all_demos.sh stop_all_demos.sh

# Start all demos (this will automatically start Foundry Local service if available)
./start_all_demos.sh
```

**What the startup script does:**
1. ✅ Checks if Foundry Local service is running
2. 🚀 Starts Foundry Local service if not running (requires ~30 seconds to initialize)
3. 🎯 Launches all 5 demos with their virtual environments

**All demos will run on separate ports:**
- 🔍 Quality Control System: http://localhost:5000
- 🤖 Azure Foundry Chat Playground: http://localhost:5001
- � Smart Camera System: http://localhost:5002
- � IoT Sensor Simulator: http://localhost:5003
- 🪟 Windows AI Foundry Demo: http://localhost:5004

### 🛑 Stopping All Demos

```bash
./stop_all_demos.sh
```

**Note:** On Windows, this will stop all Python processes. On Linux/macOS, it will only stop the demo processes.

---

## 📋 Available Demos

### 1. Quality Control System 🔍
**Location**: `edge-ai-quality-control/`  
**Port**: http://localhost:5000  
**Description**: AI-powered quality control with Azure AI Foundry Local integration for defect detection using computer vision and machine learning

### 2. Azure Foundry Local Chat Playground 🤖
**Location**: `edge-ai-foundrylocal-chat-playground/`  
**Port**: http://localhost:5001  
**Description**: Multi-model AI chat application with real-time streaming via REST API, supporting side-by-side model comparison

### 3. Smart Camera System �
**Location**: `edge-ai-smart-camera/`  
**Port**: http://localhost:5002  
**Description**: Computer vision application for real-time object detection, person tracking, and anomaly detection

### 4. IoT Sensor Simulator �  
**Location**: `edge-ai-iot-sensor/`  
**Port**: http://localhost:5003  
**Description**: Industrial IoT sensor simulation with AI-powered predictive maintenance and anomaly detection

### 5. Windows AI Foundry Demo 🪟
**Location**: `edge-ai-windows-foundry/`  
**Port**: http://localhost:5004  
**Description**: Comprehensive showcase of Windows AI Foundry capabilities across 8 AI domains including text generation, code assistance, document analysis, creative writing, multimodal processing, reasoning, translation, and summarization

---

## ⚙️ Important Notes

### Virtual Environments
Each demo uses its own virtual environment to avoid dependency conflicts:
- `edge-ai-foundrylocal-chat-playground/venv/`
- `edge-ai-iot-sensor/venv/`
- `edge-ai-quality-control/venv/`
- `edge-ai-smart-camera/venv/`
- `edge-ai-windows-foundry/venv/`

The virtual environments are automatically created and activated by the startup scripts.

### Python 3.13 Compatibility
All demos have been updated to work with Python 3.13+:
- Removed deprecated `eventlet` (replaced with `threading` mode for Flask-SocketIO)
- Removed incompatible `threading2` package
- Updated all dependencies to compatible versions

---

## 🪟 Running the Windows AI Foundry Demo

### Prerequisites ✅

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **Windows AI Foundry Local** (Required - demo requires active Foundry service)
   ```bash
   # Windows Package Manager
   winget install Microsoft.AIFoundry
   
   # Or download from Microsoft Store
   # Or visit: https://aka.ms/windows-ai-foundry
   ```

3. **Foundry Local Service** 🔧
   
   The startup script (`start_all_demos.sh`) will automatically:
   - Check if Foundry Local is running
   - Start the service if it's not running
   - Wait for initialization (~30 seconds)
   
   **Manual start (if needed):**
   ```bash
   # Start the Foundry Local service
   foundry service start
   
   # Check if service is running
   foundry service status
   
   # Or check the ports (Foundry uses 52009 or 60632)
   netstat -an | findstr "52009 60632"
   ```

### Quick Start 🚀

**Option 1: Use the automated startup script (Recommended)**

```bash
# From the main workspace directory
./start_all_demos.sh
```
This will automatically start Foundry Local service and all demos.

**Option 2: Manual start**

1. **Start Foundry Local Service** (if not using automated script)
   ```bash
   # Start the Foundry service
   foundry service start
   
   # Wait for initialization (~30 seconds)
   sleep 30
   ```

2. **Navigate to the demo folder**
   ```bash
   cd windows-ai-foundry-demo
   ```

3. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Start the Demo**
   ```bash
   python windows_ai_foundry_app.py
   ```

5. **Access the Demo**  
   Open your web browser: **http://localhost:5004**

### Using the Windows AI Foundry Demo 🎮

1. **Check Connection Status**: The indicator in the top-right corner shows:
   - 🟢 Green = Windows AI Foundry connected and ready
   - � Red = Connection issues (check if service is running)

2. **Select AI Model**: Choose from 7 available models in the dropdown:
   - **qwen2.5-0.5b-instruct** - Fast, efficient responses
   - **Phi-3.5-mini-instruct** - Microsoft's balanced model
   - **Llama-3.2-1B-Instruct** - Meta's compact model
   - **Llama-3.2-3B-Instruct** - Enhanced reasoning capabilities
   - **gemma-2-2b-it** - Google's versatile model
   - **Mistral-7B-Instruct-v0.3** - Creative and detailed responses
   - **DeepSeek-R1-Distill-Qwen-7B** - Advanced reasoning model

3. **Choose AI Capability**: Click on any of the 8 capability cards:
   - 📝 **Text Generation** - Content creation and writing assistance
   - 💻 **Code Assistance** - Programming help and code generation
   - 📄 **Document Analysis** - Document processing and insights
   - ✨ **Creative Writing** - Stories, marketing content, and creativity
   - 👁️ **Multimodal Analysis** - Visual and text content understanding
   - 🧠 **Advanced Reasoning** - Complex problem solving and logic
   - 🌍 **Translation** - Multi-language translation capabilities
   - 📊 **Summarization** - Document and text summarization

4. **Use Example Prompts**: Click on provided examples or create your own

5. **Generate Responses**: Click "Generate Response" and watch real AI processing
   - ⏱️ **Note**: Model switching takes 2-5 minutes for complex requests
   - 🔄 Auto-retry mechanism handles temporary timeouts
   - 📊 Performance metrics shown for each model

6. **Explore Features**:
   - Real-time model performance monitoring
   - Automatic timeout handling and retries
   - Copy responses to clipboard
   - View detailed model information

### AI Capabilities Examples 🎯

**Text Generation:**
- "Explain the benefits of local AI processing on Windows devices"
- "Write a professional email about implementing AI solutions"

**Code Assistance:**
- "Create a Python function to connect to Windows AI Foundry API"
- "Write a React component for displaying AI responses"

**Document Analysis:**
- "Analyze this business report and extract key metrics"
- "Identify action items from this meeting transcript"

**Creative Writing:**
- "Write a short story about AI assistants helping developers"
- "Create marketing copy for a local AI platform"

---

## 🎯 Running the Azure Foundry Local Chat Demo

### Prerequisites ✅

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **Azure Foundry Local** installed and working
   ```bash
   foundry --version
   ```
   
   If not installed:
   ```bash
   # Windows
   winget install Microsoft.FoundryLocal
   
   # macOS  
   brew tap microsoft/foundrylocal && brew install foundrylocal
   ```

### Quick Start 🚀

1. **Start Azure Foundry Local Service**
   ```bash
   foundry service start
   ```

2. **Navigate to the demo folder**
   ```bash
   cd edge-ai-foundrylocal-chat-playground
   ```

3. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Run the Demo**
   ```bash
   python foundry_app.py
   ```

5. **Access the Demo**  
   Open your web browser: **http://localhost:5001**

### Using the Chat Playground 🎮

1. **Check Connection**: Verify the Foundry Local service is connected (green indicator)
2. **Select Models**: Click on model tiles to select/deselect them (multiple selection supported)
3. **Initialize Models**: Selected models will automatically initialize (may take a few moments for first-time download)
4. **Start Chatting**: Type your message in the chat input and press Enter or click Send
5. **Compare Responses**: See how different AI models respond to the same prompt in real-time

### Available Models 🤖
- **qwen2.5-0.5b-instruct** - Lightweight, fast responses
- **Phi-3.5-mini-instruct** - Microsoft's efficient model  
- **Llama-3.2-1B-Instruct** - Meta's balanced model
- **Llama-3.2-3B-Instruct** - Enhanced reasoning
- **gemma-2-2b-it** - Google's versatile model
- **Mistral-7B-Instruct-v0.3** - Creative and detailed responses

---

## 🔧 Troubleshooting

### Common Issues

**"foundry: command not found"**
- Install Azure Foundry Local using the commands above
- Restart your terminal after installation

**"Model not found in catalog" errors**
- Some models may not be available in your installation
- Focus on models that successfully initialize (usually Qwen 2.5 and Phi-3.5 Mini)

**"Connection refused" errors**
- Ensure Azure Foundry Local service is running: `foundry service start`
- Check service status: `foundry service status`

**Port already in use**
- Check which demo uses which port:
  - Quality Control: 5000
  - Foundry Chat: 5001
  - Smart Camera: 5002
  - IoT Sensor: 5003
  - Windows Foundry: 5004
- Stop conflicting applications or modify the port in the app's Python file

**Import/dependency errors**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure virtual environment is activated

### Getting Service Status
```bash
foundry service status
```
You should see: `🟢 Model management service is running on http://127.0.0.1:52009/...`

---

## 🛑 Stopping the Demo

1. Press `Ctrl+C` in the terminal where `foundry_app.py` is running
2. Optionally stop the Foundry Local service: `foundry service stop`
3. Deactivate the virtual environment: `deactivate`

---

## 🧹 Cleanup After Demo

After stopping the demo, you can clean up temporary files:

**Windows:**
```bash
cd edge-ai-foundrylocal-chat-playground
cleanup.bat
```

**Linux/macOS:**
```bash
cd edge-ai-foundrylocal-chat-playground
rm -rf venv __pycache__
find . -name "*.pyc" -delete
```

---

## 🎯 Demo Features Highlight

- **🤖 Multi-Model Chat**: Chat with multiple AI models simultaneously
- **⚡ Real-time Streaming**: See responses as they're generated  
- **🏠 100% Local Processing**: No cloud dependencies, complete privacy
- **🔄 Model Comparison**: Compare different AI model responses side-by-side
- **🎨 Modern UI**: Beautiful, responsive web interface
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile

---

## 📚 Additional Resources

- **Troubleshooting Guide**: Check `edge-ai-foundrylocal-chat-playground/TROUBLESHOOTING.md`
- **API Documentation**: See `edge-ai-foundrylocal-chat-playground/API.md`
- **Azure Foundry Local Docs**: [https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)

---

**🎉 Enjoy exploring local AI with Azure Foundry Local!**