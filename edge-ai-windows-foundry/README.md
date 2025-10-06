# 🪟 Windows AI Foundry Demo

A comprehensive showcase of local AI capabilities running directly on Windows devices through the Windows AI Foundry platform. Experience 8 different AI capabilities powered by 7 real AI models - all running locally for complete privacy and maximum performance.

**Port**: http://localhost:5004

## ⚡ Quick Start

### Automated Setup (Recommended)

From the main workspace directory:
```bash
./start_all_demos.sh
```

The script will automatically:
- Check if Foundry Local service is running
- Start Foundry Local if needed (waits 30s for initialization)
- Create virtual environment and install dependencies
- Launch the demo on http://localhost:5004

### Manual Setup

1. **Start Foundry Local service**
   ```bash
   foundry service start
   
   # Wait for initialization
   sleep 30
   
   # Verify it's running
   foundry service status
   ```

2. **Navigate to demo folder**
   ```bash
   cd edge-ai-windows-foundry
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

5. **Start the demo**
   ```bash
   python windows_ai_foundry_app.py
   ```

6. **Access the demo**
   Open http://localhost:5004 in your browser

## 🚀 Features

- **🤖 Multi-Model Support**: Access to 7 different AI models with real-time switching
- **🎯 8 AI Capabilities**: Text generation, code assistance, document analysis, creative writing, multimodal analysis, advanced reasoning, translation, and summarization
- **🔒 100% Local Processing**: All AI operations run locally for complete privacy
- **⚡ Real-time Performance**: Enhanced with intelligent timeout handling and auto-retry mechanisms
- **📊 Model Performance Monitoring**: Real-time metrics and connection status indicators
- **🎨 Interactive Interface**: Modern web UI with responsive design
- **🔄 Graceful Error Handling**: Automatic recovery from timeouts and connection issues
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile devices

## 🎯 Available AI Capabilities

### Core Features

1. **📝 Text Generation** 
   - Professional content creation and writing assistance
   - Blog posts, articles, reports, and documentation
   - Business communications and professional writing

2. **💻 Code Assistance**
   - Multi-language programming help (Python, JavaScript, TypeScript, etc.)
   - Code generation, debugging, and optimization
   - Algorithm implementation and code review

3. **📄 Document Analysis**
   - Intelligent document processing and insights
   - Key information extraction
   - Data analysis and summarization

4. **✨ Creative Writing**
   - Stories, poetry, and narrative content
   - Marketing copy and advertising content
   - Creative brainstorming and ideation

5. **👁️ Multimodal Analysis**
   - Visual and text content understanding
   - Image description and analysis
   - Combined text and visual reasoning

6. **🧠 Advanced Reasoning**
   - Complex problem solving and logic
   - Mathematical reasoning
   - Strategic planning and decision support

7. **🌍 Translation**
   - Multi-language translation capabilities
   - Context-aware translations
   - Support for major world languages

8. **📊 Summarization**
   - Document and text summarization
   - Key points extraction
   - Executive summaries and abstracts

### Technical Highlights
- **7 AI Models**: Real-time switching between different AI models
- **Intelligent Timeouts**: Model-specific timeout handling (60s to 5+ minutes)
  - qwen2.5-0.5b-instruct: 60s timeout (fast model)
  - Phi-3.5-mini-instruct: 300s timeout
  - Llama models: 300s timeout
  - Mistral-7B: 400s timeout
  - DeepSeek-R1: 500s timeout (advanced reasoning)
- **Auto-retry System**: Automatic recovery with 10-minute fallback timeouts
- **Connection Monitoring**: Real-time status updates with visual indicators (🟢 connected, 🔴 disconnected)
- **Session Management**: Fresh HTTP sessions prevent connection issues
- **Streaming Support**: Real-time response generation where available

## 🚀 Usage

1. **Start Windows AI Foundry Local** service first (automatic via start script)
2. **Select an AI Model** from the dropdown menu
3. **Choose a Capability** by clicking on any of the 8 cards
4. **Try Example Prompts** or create your own custom prompts
5. **Generate Response** and watch real AI processing in action
6. **View Results** with syntax highlighting and markdown rendering

### Model Performance Guide

| Model | Size | Speed | Timeout | Best For |
|-------|------|-------|---------|----------|
| qwen2.5-0.5b-instruct | ~0.5GB | ⚡⚡⚡ | 60s | Quick responses, testing |
| Phi-3.5-mini-instruct | ~3.8GB | ⚡⚡ | 300s | Balanced performance |
| Llama-3.2-1B-Instruct | ~1.3GB | ⚡⚡ | 300s | General tasks |
| Llama-3.2-3B-Instruct | ~3.2GB | ⚡⚡ | 300s | Enhanced reasoning |
| gemma-2-2b-it | ~2.6GB | ⚡ | 300s | Detailed responses |
| Mistral-7B-Instruct-v0.3 | ~7GB | ⚡ | 400s | Creative content |
| DeepSeek-R1-Distill-Qwen-7B | ~7GB | ⚡ | 500s | Advanced reasoning |

## Prerequisites

### Software Requirements

1. **Windows AI Foundry Local** (Required)
   ```bash
   # Install via Windows Package Manager
   winget install Microsoft.AIFoundry
   
   # Or download from Microsoft Store
   # Or visit: https://aka.ms/windows-ai-foundry
   ```

2. **Python 3.8+** - Required
   ```bash
   python --version
   ```

3. **Internet Connection** - Required for first-time model downloads

### Python Dependencies

All dependencies are in `requirements.txt`:
- **flask==3.0.0** - Web framework
- **flask-socketio==5.3.6** - Real-time updates
- **python-dotenv==1.0.0** - Environment variables
- **requests==2.31.0** - HTTP client for API calls
- **markdown==3.5.1** - Markdown rendering
- **python-socketio==5.9.0** - WebSocket support
- **simple-websocket==1.0.0** - WebSocket client

### System Requirements

- **Minimum**: 8GB RAM, 5GB free disk space
- **Recommended**: 16GB RAM, 15GB free disk space
- **Optimal**: 32GB RAM, 30GB+ SSD storage

## Project Structure

```
edge-ai-windows-foundry/
├── windows_ai_foundry_app.py   # Main Flask application
├── requirements.txt            # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css          # Application styling
│   └── js/
│       └── app.js             # Frontend JavaScript
├── templates/
│   └── index.html             # Main web interface
└── README.md                  # This file
```

## Troubleshooting

### Common Issues

**Foundry Local service not running**
```bash
# Start the service
foundry service start

# Check status
foundry service status

# Verify endpoint is accessible
curl http://localhost:52009/v1/models
# or
curl http://localhost:60632/v1/models
```

**Port 5004 already in use**
- Stop other applications using port 5004
- Or modify the port in `windows_ai_foundry_app.py` (line 683): change `port=5004`

**Connection timeout errors**
- Check that Foundry Local service is running
- Wait for service initialization (30 seconds after starting)
- System automatically retries with longer timeouts
- Some models may take several minutes for complex requests

**Model not responding**
- Try a lighter model (qwen2.5-0.5b-instruct)
- Check system resources (RAM, CPU)
- Restart Foundry Local service
- Check Foundry Local logs for errors

**Import or dependency errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

**SocketIO connection issues**
- Check browser console for errors
- Ensure Flask-SocketIO is properly installed
- Try accessing from localhost (not 127.0.0.1)
- Check firewall settings

### Performance Tips

- **Start with small models**: qwen2.5-0.5b-instruct is fastest
- **Allow time for initialization**: First model load takes longer
- **Close unused applications**: Free up RAM and CPU
- **Use SSD storage**: Faster model loading
- **Be patient**: Larger models (7B) take more time

## Technical Details

### Architecture

```
[Web Browser] ←→ [Flask App (Port 5004)]
                       ↓
              [SocketIO Real-time Updates]
                       ↓
            [Windows AI Foundry Manager]
                       ↓
            [REST API Client with Retry Logic]
                       ↓
            [Foundry Local Service]
            (Port 52009 or 60632)
                       ↓
            [Local AI Models (7 models)]
```

### API Communication
- **Endpoint Detection**: Automatically finds Foundry Local on ports 52009 or 60632
- **Model Management**: Lists and switches between available models
- **Chat Completion**: Sends prompts via `/v1/chat/completions`
- **Retry Mechanism**: Automatic retry with extended timeouts on failure
- **Session Management**: Fresh sessions for each request to prevent connection issues

## 📚 Documentation

For complete setup instructions and troubleshooting, see the main [DEMO_INSTRUCTIONS.md](../DEMO_INSTRUCTIONS.md) file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Learn More

- [Windows AI Foundry Documentation](https://learn.microsoft.com/en-us/windows/ai/)
- [Azure AI Foundry Local](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
- [Local AI Development Best Practices](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/concepts/)

---

**Built with ❤️ using Windows AI Foundry**

*Experience the full power of local AI with 8 comprehensive capabilities!*