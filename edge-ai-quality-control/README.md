# 🤖 Azure AI Quality Control Demo

An AI-powered quality control system for manufacturing that integrates with **Azure AI Foundry Local** for real-time defect detection using computer vision and machine learning.

## 🌟 Features

- **🔍 Real AI Integration**: Uses Azure AI Foundry Local for actual defect analysis
- **👁️ Vision Analysis**: Supports multimodal AI models for image inspection  
- **⚡ Real-time Processing**: Live defect detection with Socket.IO updates
- **📊 Smart Dashboard**: Web interface with statistics and AI status
- **🔄 Intelligent Fallback**: Graceful simulation mode when AI unavailable
- **🎯 Realistic Testing**: Enhanced with real manufacturing imagery

## 🚀 Quick Start

### Prerequisites

1. **Install Azure AI Foundry Local**:
   ```bash
   # Using Windows Package Manager
   winget install Microsoft.AzureAIFoundryLocal
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Demo

1. **Start Azure AI Foundry Local** and ensure models are available

2. **Run the AI-enhanced quality control system**:
   ```bash
   python azure_ai_quality_control.py
   ```

3. **Open the dashboard**: Navigate to `http://localhost:5000`

## 🎯 Azure AI Foundry Local Integration

The system automatically detects and connects to Azure AI Foundry Local using the official SDK. Supported models include:

- **phi-3.5-mini** - Efficient text analysis (currently loaded)
- **phi-4** - Advanced reasoning capabilities
- **qwen2.5** variants - Multilingual support

## 🕹️ Usage Instructions

1. **Launch**: `python azure_ai_quality_control.py`
2. **Open dashboard**: `http://localhost:5000`
3. **Start Production**: Click to begin AI-powered quality analysis
4. **Monitor**: Watch real-time defect detection with AI insights
5. **Stop**: Press `Ctrl+C` in terminal

## 📁 Project Structure

```
edge-ai-quality-control/
├── azure_ai_quality_control.py    # Main AI-powered application
├── start_azure_foundry.py         # Foundry startup helper
├── requirements.txt               # Python dependencies
├── templates/index.html           # Web dashboard
└── README.md                     # This file
```

## 🔧 Troubleshooting

### Azure AI Foundry Local Issues
1. Ensure Azure AI Foundry Local is running and models are loaded
2. Check foundry-local-sdk is installed: `pip install foundry-local-sdk`
3. Verify models are available via Foundry Local Manager
4. System automatically falls back to simulation mode if needed

### Common Solutions
- **Connection errors**: Restart Azure AI Foundry Local
- **Model loading**: Check available models in Foundry Local interface
- **Port conflicts**: Default detection handles multiple endpoints