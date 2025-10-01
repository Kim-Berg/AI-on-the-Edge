# Azure Foundry Local Chat Playground 🚀

A cutting-edge multi-model AI chat application showcasing the power of **Azure Foundry Local**. Experience local AI processing with multiple models running simultaneously, real-time streaming responses, and beautiful side-by-side comparisons.

![Azure Foundry Local Chat Playground](https://img.shields.io/badge/Azure-Foundry%20Local-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

> 📖 **Quick Start**: See [../DEMO_INSTRUCTIONS.md](../DEMO_INSTRUCTIONS.md) for step-by-step setup guide. Foundry Local Chat Playground 🚀

A cutting-edge multi-model AI chat application showcasing the power of **Azure Foundry Local**. Experience local AI processing with multiple models running simultaneously, real-time streaming responses, and beautiful side-by-side comparisons.

![Azure Foundry Local Chat Playground](https://img.shields.io/badge/Azure-Foundry%20Local-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

> � **Quick Start**: See [DEMO_INSTRUCTIONS.md](DEMO_INSTRUCTIONS.md) for step-by-step setup guide.

## 🌟 Features

- **🤖 Multi-Model Chat**: Chat with multiple AI models simultaneously
- **⚡ Real-time Streaming**: See responses as they're generated
- **🔄 Model Comparison**: Compare responses side-by-side
- **🏠 100% Local**: No cloud dependencies, complete privacy
- **💬 Chat History**: Persistent conversation management
- **🎨 Modern UI**: Beautiful, responsive web interface
- **🚀 Easy Setup**: One-command installation and setup
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile

## 🎬 Demo Features

### Multi-Model AI Chat
- Select and chat with multiple local AI models simultaneously
- Compare responses from different models in real-time
- Streaming responses for immediate feedback

### Supported Models
- **Qwen 2.5 (0.5B)** - Lightweight, fast responses
- **Phi-3.5 Mini** - Microsoft's efficient model
- **Llama 3.2 (1B)** - Meta's balanced model
- **Gemma 2 (2B)** - Google's versatile model
- **Mistral 7B** - Creative and detailed responses

### Interactive Features
- 🔧 Dynamic model management and initialization
- 📊 Real-time system status monitoring
- 🗑️ Conversation history management
- ⚙️ Configurable parameters (temperature, max tokens)
- 📱 Responsive design for all devices

## 🚀 Quick Start

### Prerequisites

1. **Azure Foundry Local** - [Install Azure Foundry Local](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started)
   ```bash
   # Windows
   winget install Microsoft.FoundryLocal
   
   # macOS  
   brew tap microsoft/foundrylocal && brew install foundrylocal
   ```

2. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)

### Installation

#### Option 1: Automatic Setup (Recommended)

**Windows:**
```cmd
setup.bat
```

**Linux/macOS:**
```bash
./setup.sh
```

#### Option 2: Manual Setup

1. **Clone or download this repository**

2. **Create virtual environment**
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

4. **Start Azure Foundry Local**
   ```bash
   foundry service start
   ```

5. **Run the application**
   ```bash
   python foundry_app.py
   ```

### Running the Application

**Windows:**
```cmd
run.bat
```

**Linux/macOS:**
```bash
./run.sh
```

Then open http://localhost:5000 in your web browser! 🌐

## 🎯 Usage Guide

### Getting Started

1. **Launch the application** using the run scripts
2. **Select models** from the model panel (click to select/deselect)
3. **Wait for initialization** - models will download on first use
4. **Start chatting** - type your message and press Enter
5. **Compare responses** - see how different models respond to the same prompt

### Model Management

- **Green indicator**: Model ready to use
- **Yellow indicator**: Model initializing
- **Red indicator**: Model error
- **Gray indicator**: Model not initialized

### Tips for Best Experience

- 🚀 **Start small**: Begin with lightweight models like Qwen 2.5 (0.5B)
- ⚡ **Internet required**: First-time model downloads need internet
- 💾 **Storage space**: Models require 0.5GB - 7GB each
- 🔄 **Model switching**: You can change selected models anytime
- 📱 **Mobile use**: Works great on mobile devices too!

## 🛠️ Development

### Development Mode

Use the development helper script for advanced features:

```bash
# Start in development mode
./scripts/dev.sh start

# Check status
./scripts/dev.sh status

# Manage models
./scripts/dev.sh models

# Clean up
./scripts/dev.sh clean
```

### Project Structure

```
foundry-chat-playground/
├── foundry_app.py          # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                   # Environment configuration
├── setup.sh/.bat          # Automated setup scripts
├── run.sh/.bat            # Application launcher
├── static/                # Web assets
│   ├── css/style.css      # Application styling
│   └── js/app.js          # Frontend JavaScript
├── templates/             # HTML templates
│   └── index.html         # Main web interface
├── scripts/               # Helper scripts
│   └── dev.sh             # Development utilities
└── README.md              # This file
```

### Configuration

Edit `.env` file to customize:

```env
# Default models to load
DEFAULT_MODELS=qwen2.5-0.5b,phi-3.5-mini

# API Configuration  
MAX_TOKENS=1000
TEMPERATURE=0.7

# Chat Configuration
MAX_HISTORY_MESSAGES=50
ENABLE_STREAMING=true
```

## 🔧 Troubleshooting

### Common Issues

**"Foundry service not running"**
```bash
foundry service start
```

**"Model failed to initialize"**
- Check internet connection (first download)
- Verify sufficient disk space
- Try restarting the Foundry service

**"Port 5000 already in use"**
- Stop other applications using port 5000
- Or modify the port in `foundry_app.py`

**"Import errors"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Getting Help

1. **Check logs** - Error messages in the terminal
2. **System status** - Click "Status" button in the web interface
3. **Foundry Local docs** - [Official Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
4. **Model management** - Use `foundry model list` and `foundry cache list`

## 🎨 Customization

### Adding New Models

1. **Check available models**:
   ```bash
   foundry model list
   ```

2. **Add to the model list** in `foundry_app.py`:
   ```python
   def get_available_models(self):
       return [
           'qwen2.5-0.5b',
           'phi-3.5-mini', 
           'your-new-model'  # Add here
       ]
   ```

3. **Add model description** in `static/js/app.js`:
   ```javascript
   getModelDescription(alias) {
       const descriptions = {
           'your-new-model': 'Description of your model'
       };
       return descriptions[alias] || 'Advanced AI model';
   }
   ```

### Styling Customization

Edit `static/css/style.css` to customize the appearance. The CSS uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #0078d4;  /* Change primary color */
    --bg-primary: #ffffff;     /* Change background */
    /* ... other variables ... */
}
```

## 📊 Performance Tips

### Model Performance

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| Qwen 2.5 (0.5B) | ~0.5GB | ⚡⚡⚡ | ⭐⭐ | Quick responses, testing |
| Phi-3.5 Mini | ~2GB | ⚡⚡ | ⭐⭐⭐ | Reasoning, analysis |
| Llama 3.2 (1B) | ~1GB | ⚡⚡ | ⭐⭐⭐ | Balanced performance |
| Gemma 2 (2B) | ~2GB | ⚡ | ⭐⭐⭐⭐ | Detailed responses |
| Mistral 7B | ~7GB | ⚡ | ⭐⭐⭐⭐⭐ | Creative writing |

### Hardware Recommendations

- **Minimum**: 8GB RAM, 3GB free disk space
- **Recommended**: 16GB RAM, 15GB free disk space
- **Optimal**: 32GB RAM, SSD storage, GPU acceleration

## 🚀 Advanced Features

### API Endpoints

The application exposes REST APIs for integration:

- `GET /api/models/available` - List available models
- `POST /api/models/initialize` - Initialize a model
- `POST /api/chat` - Send chat message
- `POST /api/chat/stream` - Stream chat responses
- `GET /api/status` - System status
- `GET /api/history` - Chat history

### Streaming API

Use Server-Sent Events for real-time streaming:

```javascript
const eventSource = new EventSource('/api/chat/stream');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Handle streaming data
};
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🙏 Acknowledgments

- **Microsoft** for Azure Foundry Local
- **OpenAI** for the API compatibility layer
- **Meta, Google, Mistral** for their open models
- The open-source community for inspiration

## 📚 Learn More

- [Azure Foundry Local Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
- [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry/)
- [Local AI Development Best Practices](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/concepts/)

---

**Built with ❤️ using Azure Foundry Local**

*Experience the power of local AI processing with the convenience of cloud-scale models!*