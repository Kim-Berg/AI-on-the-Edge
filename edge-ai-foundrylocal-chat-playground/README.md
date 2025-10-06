# Azure Foundry Local Chat Playground 🚀

A cutting-edge multi-model AI chat application showcasing the power of **Azure Foundry Local**. Experience local AI processing with multiple models running simultaneously, real-time streaming responses, and beautiful side-by-side comparisons via REST API integration.

![Azure Foundry Local Chat Playground](https://img.shields.io/badge/Azure-Foundry%20Local-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

> 📖 **Quick Start**: See [../DEMO_INSTRUCTIONS.md](../DEMO_INSTRUCTIONS.md) for step-by-step setup guide.

## 🌟 Features

- **🤖 Multi-Model Chat**: Chat with multiple AI models simultaneously
- **⚡ Real-time Streaming**: See responses as they're generated via REST API
- **🔄 Model Comparison**: Compare responses side-by-side in real-time
- **🏠 100% Local**: No cloud dependencies, complete privacy
- **💬 Chat History**: Persistent conversation management
- **🎨 Modern UI**: Beautiful, responsive web interface
- **🚀 Easy Setup**: Automated setup with Foundry Local service
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile
- **🔌 REST API Integration**: Direct communication with Foundry Local service

## 🎬 Demo Features

### Multi-Model AI Chat via REST API
- Select and chat with multiple local AI models simultaneously
- Compare responses from different models in real-time
- Streaming responses via REST API for immediate feedback
- Automatic model initialization on first use

### Supported Models
- **qwen2.5-0.5b-instruct** - Lightweight, fast responses (500MB)
- **Phi-3.5-mini-instruct** - Microsoft's efficient model (3.8GB)
- **Llama-3.2-1B-Instruct** - Meta's balanced model (1.3GB)
- **Llama-3.2-3B-Instruct** - Enhanced reasoning (3.2GB)
- **gemma-2-2b-it** - Google's versatile model (2.6GB)
- **Mistral-7B-Instruct-v0.3** - Creative and detailed responses (7GB)

### Interactive Features
- 🔧 Dynamic model management via REST API
- 📊 Real-time system status monitoring
- 🗑️ Conversation history management with clear chat option
- ⚙️ Configurable parameters (temperature, max tokens)
- 📱 Responsive design for all devices
- 🔌 Automatic Foundry Local service detection
- ⚡ Real-time streaming responses

## 🚀 Quick Start

### Prerequisites

1. **Azure Foundry Local** - Install Azure Foundry Local service
   ```bash
   # Windows
   winget install Microsoft.AIFoundry
   
   # macOS  
   brew tap microsoft/foundrylocal && brew install foundrylocal
   ```

2. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)

3. **Internet connection** - Required for initial model downloads only

### Installation & Running

#### Automated Setup (Recommended - From Main Workspace)

From the main workspace directory, run:
```bash
./start_all_demos.sh
```

This will:
- Check and start Foundry Local service automatically
- Set up the virtual environment
- Install dependencies
- Launch the chat playground on **http://localhost:5001**

#### Manual Setup

1. **Start Foundry Local service**
   ```bash
   foundry service start
   
   # Verify it's running
   foundry service status
   ```

2. **Navigate to the demo folder**
   ```bash
   cd edge-ai-foundrylocal-chat-playground
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

5. **Run the application**
   ```bash
   python foundry_app.py
   ```

6. **Open your browser**  
   Navigate to **http://localhost:5001** 🌐

## 🎯 Usage Guide

### Getting Started

1. **Launch the application** - Access http://localhost:5001
2. **Check connection status** - Green indicator means Foundry Local is connected
3. **Select models** from the model panel (click to select/deselect, multiple selection supported)
4. **Wait for initialization** - Models will download on first use (requires internet)
5. **Start chatting** - Type your message and press Enter or click Send
6. **Compare responses** - See how different models respond to the same prompt in real-time

### Model Status Indicators

- **🟢 Green**: Model ready to use
- **🟡 Yellow**: Model initializing (downloading or loading)
- **🔴 Red**: Model error (check logs or service status)
- **⚪ Gray**: Model not initialized

### Tips for Best Experience

- 🚀 **Start small**: Begin with lightweight models like qwen2.5-0.5b-instruct
- ⚡ **Internet required**: First-time model downloads need internet connection
- 💾 **Storage space**: Models require 0.5GB - 7GB each
- 🔄 **Model switching**: You can change selected models anytime during chat
- 📱 **Mobile use**: Fully responsive and works great on mobile devices
- 🔌 **Service status**: Check Foundry Local service is running if models fail to load
- 💬 **Clear chat**: Use the clear chat button to start fresh conversations

## 🛠️ Development

### Project Structure

```
edge-ai-foundrylocal-chat-playground/
├── foundry_app.py          # Main Flask application with REST API integration
├── requirements.txt        # Python dependencies
├── static/                 # Web assets
│   ├── css/style.css      # Application styling
│   └── js/app.js          # Frontend JavaScript
├── templates/              # HTML templates
│   └── index.html         # Main web interface
├── API.md                 # API documentation
├── TROUBLESHOOTING.md     # Troubleshooting guide
└── README.md              # This file
```

### Dependencies

Key dependencies from `requirements.txt`:
- **flask==3.0.0** - Web framework
- **openai==1.51.0** - OpenAI SDK for API compatibility
- **foundry-local-sdk==1.0.0** - Foundry Local integration (optional)
- **requests==2.31.0** - HTTP client for REST API calls
- **websockets==12.0** - WebSocket support
- **python-dotenv==1.0.0** - Environment variable management

## 🔧 Troubleshooting

### Common Issues

**"Foundry service not running"**
```bash
# Start the service
foundry service start

# Check status
foundry service status

# Verify endpoint accessibility
curl http://localhost:52009/v1/models
# or
curl http://localhost:60632/v1/models
```

**"Model failed to initialize"**
- Check internet connection (required for first download)
- Verify sufficient disk space (models are 0.5GB - 7GB each)
- Try restarting the Foundry service: `foundry service stop` then `foundry service start`
- Check model availability: `foundry model list`

**"Port 5001 already in use"**
- Stop other applications using port 5001
- Or modify the port in `foundry_app.py` (line 695): change `port=5001` to another port

**"Import errors or dependency issues"**
- Ensure virtual environment is activated: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

**"Connection refused" errors**
- Foundry Local service may not be running properly
- Check if ports 52009 or 60632 are accessible
- Restart Foundry Local service

### Getting Help

1. **Check logs** - Error messages appear in the terminal where you ran `python foundry_app.py`
2. **System status** - The web interface shows connection status in real-time
3. **Foundry Local docs** - [Official Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
4. **Model management** - Use `foundry model list` to see available models
5. **Check TROUBLESHOOTING.md** - More detailed troubleshooting guide in the project

## 📊 Model Performance

### Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| qwen2.5-0.5b-instruct | ~0.5GB | ⚡⚡⚡ | ⭐⭐ | Quick responses, testing |
| Phi-3.5-mini-instruct | ~3.8GB | ⚡⚡ | ⭐⭐⭐ | Reasoning, analysis |
| Llama-3.2-1B-Instruct | ~1.3GB | ⚡⚡ | ⭐⭐⭐ | Balanced performance |
| Llama-3.2-3B-Instruct | ~3.2GB | ⚡⚡ | ⭐⭐⭐⭐ | Enhanced reasoning |
| gemma-2-2b-it | ~2.6GB | ⚡ | ⭐⭐⭐⭐ | Detailed responses |
| Mistral-7B-Instruct-v0.3 | ~7GB | ⚡ | ⭐⭐⭐⭐⭐ | Creative writing |

### Hardware Recommendations

- **Minimum**: 8GB RAM, 3GB free disk space, 2-core CPU
- **Recommended**: 16GB RAM, 15GB free disk space, 4-core CPU
- **Optimal**: 32GB RAM, 30GB+ SSD storage, 8-core CPU, GPU acceleration

## 🚀 Technical Details

### REST API Integration

The application communicates with Foundry Local via REST API:
- **Endpoint Detection**: Automatically detects Foundry Local on ports 52009 or 60632
- **Model Management**: Lists available models via `/v1/models` endpoint
- **Chat Completion**: Sends prompts via `/v1/chat/completions` endpoint
- **Streaming Support**: Real-time responses using streaming completions

### Architecture

```
[Web Browser] ←→ [Flask App (Port 5001)]
                       ↓
                 [REST API Client]
                       ↓
            [Foundry Local Service]
            (Port 52009 or 60632)
                       ↓
                [AI Models (Local)]
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Learn More

- [Azure Foundry Local Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
- [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry/)
- [API Documentation](./API.md) - Detailed API documentation for this project
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Comprehensive troubleshooting

---

**Built with ❤️ using Azure Foundry Local and REST API**

*Experience the power of local AI processing with multiple models running simultaneously!*