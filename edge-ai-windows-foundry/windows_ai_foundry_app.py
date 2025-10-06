"""
Windows AI Foundry Demo - Comprehensive AI Capabilities Showcase
Demonstrates the power of Windows AI Foundry for local AI development
"""

import os
import json
import logging
import subprocess
import requests
import time
import base64
import io
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import deque
import markdown
import re

# Load environment variables
load_dotenv()

# Feature flags for logging control
ENABLE_DEBUG_LOGGING = os.getenv('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true'
ENABLE_FLASK_DEBUG = os.getenv('ENABLE_FLASK_DEBUG', 'false').lower() == 'true'

# Configure logging based on feature flags
log_level = logging.DEBUG if ENABLE_DEBUG_LOGGING else logging.WARNING
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Reduce werkzeug (Flask) logging noise
logging.getLogger('werkzeug').setLevel(logging.ERROR if not ENABLE_FLASK_DEBUG else logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'windows-ai-foundry-demo-secret')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class WindowsAIFoundryManager:
    """Manages Windows AI Foundry models and AI capabilities"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.max_history = int(os.getenv('MAX_HISTORY_MESSAGES', 100))
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.foundry_endpoint = None
        self.base_url = None
        self.available_models = []
        self.current_model = None
        
        # Demo capabilities
        self.capabilities = {
            'text_generation': True,
            'code_assistance': True,
            'document_analysis': True,
            'creative_writing': True,
            'multimodal': True,
            'reasoning': True,
            'translation': True,
            'summarization': True
        }
        
        # Initialize Windows AI Foundry connection
        self._initialize_foundry_connection()
        
    def _initialize_foundry_connection(self):
        """Initialize connection to Windows AI Foundry service"""
        try:
            # Check for local AI services (Windows AI Foundry compatible)
            endpoints = [
                ('http://localhost:60632', '/v1/models'), # Foundry Local service port (dynamic)
                ('http://localhost:52009', '/v1/models'), # Alternative Foundry Local service port
                ('http://localhost:3928', '/health'),     # Default Azure AI Foundry Local port
                ('http://localhost:1234', '/v1/models'),  # LM Studio compatibility
                ('http://localhost:11434', '/api/tags'),  # Ollama compatibility  
                ('http://localhost:8080', '/health')      # Alternative port
            ]
            
            for endpoint, health_path in endpoints:
                try:
                    response = requests.get(f"{endpoint}{health_path}", timeout=5)
                    if response.status_code == 200:
                        self.foundry_endpoint = endpoint
                        self.base_url = endpoint
                        logger.info(f"✅ Connected to local AI service at {endpoint}")
                        self._load_available_models()
                        return
                except requests.exceptions.RequestException:
                    continue
                    
            # Fallback: Check if service is running via CLI
            try:
                result = subprocess.run(['ai-foundry', 'status'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.foundry_endpoint = 'http://localhost:3928'
                    self.base_url = 'http://localhost:3928'
                    logger.info("✅ Windows AI Foundry service detected via CLI")
                    self._load_available_models()
                    return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
            logger.warning("⚠️  Windows AI Foundry Local service not found")
            logger.info("📋 Running in demonstration mode without AI service")
            logger.info("💡 To enable real AI: Start Windows AI Foundry service")
            # Don't raise exception - allow app to run in demo mode
            
        except Exception as e:
            logger.error(f"Error initializing Windows AI Foundry: {e}")
            logger.info("📋 Continuing in demonstration mode")
            # Don't raise - allow graceful degradation
            
    def _load_available_models(self):
        """Load available models from Windows AI Foundry"""
        try:
            if self.base_url:
                # Try to get models from API
                response = requests.get(f"{self.base_url}/v1/models", timeout=10)
                if response.status_code == 200:
                    models_data = response.json()
                    self.available_models = [model['id'] for model in models_data.get('data', [])]
                    if self.available_models:
                        # Use the smallest, fastest model first
                        fastest_models = [m for m in self.available_models if 'qwen2.5-0.5b' in m]
                        self.current_model = fastest_models[0] if fastest_models else self.available_models[0]
                        logger.info(f"📋 Loaded {len(self.available_models)} models")
                        logger.info(f"🎯 Using model: {self.current_model}")
                        return
                        
            # No fallback - require real Foundry connection
            raise Exception("Unable to load models from Windows AI Foundry")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise Exception(f"Failed to load models from Windows AI Foundry: {e}")
        
    def get_available_models(self):
        """Get list of available AI models"""
        return self.available_models
        
    def set_current_model(self, model_name: str):
        """Set the current model for inference"""
        if model_name in self.available_models:
            self.current_model = model_name
            return True
        return False
        
    def test_model_readiness(self, model_name: str, max_retries: int = 3) -> Dict:
        """Test if a model is ready for inference with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Make a simple test request to verify model is ready
                payload = {
                    'model': model_name,
                    'messages': [{'role': 'user', 'content': 'Hi'}],
                    'temperature': 0.1,
                    'max_tokens': 5,  # Very short response
                    'stream': False
                }
                
                # Use progressively longer timeouts for retries
                timeout = 15 + (attempt * 10)  # 15s, 25s, 35s
                
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=timeout
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('choices') and len(result['choices']) > 0:
                        return {
                            'ready': True,
                            'response_time': response_time,
                            'test_response': result['choices'][0]['message']['content'],
                            'attempt': attempt + 1
                        }
                
                # If we get a bad status code, try again
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds between attempts
                    continue
                    
                return {
                    'ready': False,
                    'response_time': response_time,
                    'error': f'API returned status {response.status_code} after {max_retries} attempts'
                }
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.info(f"Model readiness check timeout on attempt {attempt + 1}, retrying...")
                    continue
                return {
                    'ready': False,
                    'error': f'Model not responding after {max_retries} attempts - may still be loading',
                    'loading': True
                }
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.info(f"Model readiness check error on attempt {attempt + 1}: {e}, retrying...")
                    time.sleep(1)
                    continue
                return {
                    'ready': False,
                    'error': f'Model test failed after {max_retries} attempts: {str(e)}'
                }
        
        return {
            'ready': False,
            'error': 'All readiness check attempts failed'
        }
    
    def check_connection_status(self) -> bool:
        """Check if Windows AI Foundry Local is responsive"""
        try:
            response = requests.get(f'{self.base_url}/v1/models', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_current_loaded_model(self) -> Dict:
        """Check which model is currently loaded and active in Foundry Local"""
        try:
            # First, get the list of models to see their status
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                # For now, we'll assume the current model is loaded
                # Foundry Local API doesn't directly tell us which model is "active"
                return {
                    'loaded_model': self.current_model,
                    'available_models': [model['id'] for model in models_data.get('data', [])]
                }
            return {'error': 'Could not check model status'}
        except Exception as e:
            return {'error': f'Failed to check loaded model: {str(e)}'}
        
    def generate_response(self, prompt: str, capability: str = 'text_generation', **kwargs) -> Dict:
        """Generate AI response using Windows AI Foundry Local models only"""
        try:
            if not self.base_url:
                raise Exception("Windows AI Foundry not connected")
            return self._call_foundry_api(prompt, capability, **kwargs)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise Exception(f"Failed to generate response from Windows AI Foundry: {e}")
            
    def _call_foundry_api(self, prompt: str, capability: str, **kwargs) -> Dict:
        """Call Windows AI Foundry API with adaptive timeout handling and fresh session"""
        try:
            # Progressive timeout strategy based on model size and complexity
            # Dramatically increased timeouts based on actual performance data showing 2+ minute responses
            model_timeouts = {
                'qwen2.5-0.5b': 60,      # Fast model - 60s (was 30s)
                'phi-3.5-mini': 300,     # Medium model - 300s (was 90s) - Phi-4 took 121s, so give mini more time
                'phi-4-mini': 300,       # Large model - 300s (was 120s)
                'phi-4': 300,            # Very large model - 300s (was 180s) - worked at 121s, give buffer
                'mistral': 400,          # Very large model - 400s (was 240s)
                'deepseek': 500          # Extremely large model - 500s (was 300s)
            }
            
            # Determine appropriate timeout based on current model
            timeout_seconds = 300  # Dramatically increased default timeout from 120s to 300s (5 minutes)
            for model_key, timeout_val in model_timeouts.items():
                if model_key.lower() in self.current_model.lower():
                    timeout_seconds = timeout_val
                    break
            
            # Additional checks for models with generic names
            if 'phi' in self.current_model.lower():
                if 'mini' in self.current_model.lower() or '3.5' in self.current_model.lower():
                    timeout_seconds = max(timeout_seconds, 300)  # At least 300s (5 min) for Phi mini models
                else:
                    timeout_seconds = max(timeout_seconds, 300)  # At least 300s (5 min) for full Phi models
                
            # Adjust timeout based on prompt length (longer prompts need more time)
            if len(prompt) > 500:
                timeout_seconds += 15
            elif len(prompt) > 200:
                timeout_seconds += 10
                
            payload = {
                'model': self.current_model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 500),
                'stream': False
            }
            
            logger.info(f"🔄 API call to {self.current_model} (timeout: {timeout_seconds}s, prompt: {len(prompt)} chars)")
            logger.info(f"📋 Payload: model={payload['model']}, temp={payload['temperature']}, max_tokens={payload['max_tokens']}")
            
            start_time = time.time()
            
            # Create a fresh session for each request to avoid connection pooling issues
            session = requests.Session()
            session.headers.update({'Content-Type': 'application/json'})
            
            try:
                response = session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=timeout_seconds
                )
                response_time = round((time.time() - start_time) * 1000, 2)
                
                logger.info(f"📡 HTTP Response: {response.status_code}, Time: {response_time}ms")
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    logger.info(f"✅ Response generated in {response_time}ms ({len(content)} chars)")
                    
                    return {
                        'response': content,
                        'model': self.current_model,
                        'capability': capability,
                        'timestamp': datetime.now().isoformat(),
                        'real_ai': True,
                        'response_time': response_time,
                        'timeout_used': timeout_seconds
                    }
                else:
                    logger.error(f"❌ API Error {response.status_code}: {response.text}")
                    raise Exception(f"API Error: {response.status_code} - {response.text}")
                    
            finally:
                session.close()  # Ensure session is properly closed
                
        except requests.exceptions.Timeout:
            elapsed = round((time.time() - start_time) * 1000, 2)
            logger.error(f"⏰ Request timed out after {elapsed}ms (limit: {timeout_seconds}s) for model {self.current_model}")
            
            # Auto-retry with extended timeout for first failure
            if timeout_seconds < 600:  # If timeout was less than 10 minutes, try once more with 10 minutes
                logger.info(f"🔄 Auto-retrying with extended 10-minute timeout...")
                
                try:
                    retry_session = requests.Session()
                    retry_session.headers.update({'Content-Type': 'application/json'})
                    
                    retry_start = time.time()
                    retry_response = retry_session.post(
                        f"{self.base_url}/v1/chat/completions",
                        json=payload,
                        timeout=600  # 10 minutes
                    )
                    retry_time = round((time.time() - retry_start) * 1000, 2)
                    
                    if retry_response.status_code == 200:
                        result = retry_response.json()
                        content = result['choices'][0]['message']['content']
                        
                        logger.info(f"✅ Retry succeeded in {retry_time}ms ({len(content)} chars)")
                        
                        return {
                            'response': content,
                            'model': self.current_model,
                            'capability': capability,
                            'timestamp': datetime.now().isoformat(),
                            'real_ai': True,
                            'response_time': retry_time,
                            'timeout_used': 600,
                            'retry_success': True
                        }
                    
                    retry_session.close()
                    
                except Exception as retry_error:
                    logger.error(f"❌ Retry also failed: {retry_error}")
            
            # Provide helpful suggestions based on model type
            if 'deepseek' in self.current_model.lower() or 'mistral' in self.current_model.lower():
                suggestion = "Large models can be very slow. Try switching to Qwen2.5 0.5B for reliable fast responses."
            elif any(x in self.current_model.lower() for x in ['phi-4', 'phi-3.5']):
                suggestion = "Phi models can take several minutes to respond. Try Qwen2.5 0.5B for faster responses."
            else:
                suggestion = "Try switching to Qwen2.5 0.5B for the most reliable responses."
            
            raise Exception(f"Request timed out after {timeout_seconds} seconds (and 10-minute retry). {suggestion}")
            
        except requests.exceptions.RequestException as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            logger.error(f"💥 Network error after {elapsed}ms: {e}")
            raise Exception(f"Network error: {e}")
            
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            logger.error(f"🔥 Unexpected API error after {elapsed}ms: {e}")
            raise Exception(f"Windows AI Foundry API call failed: {e}")
# Global AI manager instance
ai_manager = WindowsAIFoundryManager()

@app.route('/')
def index():
    """Main dashboard route"""
    return render_template('index.html')

@app.route('/api/models')
def get_models():
    """Get available AI models"""
    return jsonify({
        'models': ai_manager.get_available_models(),
        'current_model': ai_manager.current_model,
        'capabilities': ai_manager.capabilities
    })

@app.route('/api/connection/status')
def get_connection_status():
    """Check Windows AI Foundry connection status"""
    is_connected = ai_manager.check_connection_status()
    return jsonify({
        'connected': is_connected,
        'service': 'Windows AI Foundry Local',
        'base_url': ai_manager.base_url if is_connected else None
    })

@app.route('/api/model/set', methods=['POST'])
def set_model():
    """Set current AI model with enhanced readiness checking"""
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'success': False, 'error': 'No model specified'}), 400
    
    # Check if model exists in available models
    if model_name not in ai_manager.available_models:
        return jsonify({'success': False, 'error': 'Model not available'}), 400
    
    # Check if we're already using this model
    if ai_manager.current_model == model_name:
        # Still test readiness to make sure it's working
        try:
            test_result = ai_manager.test_model_readiness(model_name, max_retries=1)
            if test_result['ready']:
                return jsonify({
                    'success': True, 
                    'model': model_name,
                    'ready': True,
                    'response_time': test_result.get('response_time', 0),
                    'already_loaded': True
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Current model not responding: {test_result.get("error")}',
                    'ready': False
                }), 500
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'Model check failed: {str(e)}',
                'ready': False
            }), 500
    
    # Set the new model
    if ai_manager.set_current_model(model_name):
        try:
            logger.info(f"🔄 Switching to model: {model_name}")
            
            # Test model readiness with retries
            test_result = ai_manager.test_model_readiness(model_name, max_retries=3)
            
            if test_result['ready']:
                logger.info(f"✅ Model {model_name} is ready (took {test_result.get('response_time', 0)}ms)")
                return jsonify({
                    'success': True, 
                    'model': model_name,
                    'ready': True,
                    'response_time': test_result.get('response_time', 0),
                    'attempts': test_result.get('attempt', 1)
                })
            else:
                logger.error(f"❌ Model {model_name} failed readiness check: {test_result.get('error')}")
                
                # If model is still loading, provide helpful message
                if test_result.get('loading'):
                    return jsonify({
                        'success': False, 
                        'error': f'Model is still loading. This can take several minutes for larger models.',
                        'ready': False,
                        'loading': True,
                        'suggestion': 'Try again in 30-60 seconds, or use a smaller model like qwen2.5-0.5b'
                    }), 202  # 202 Accepted but not ready
                else:
                    return jsonify({
                        'success': False, 
                        'error': test_result.get('error', 'Model not responding'),
                        'ready': False
                    }), 500
                    
        except Exception as e:
            logger.error(f"Exception during model switch: {e}")
            return jsonify({
                'success': False, 
                'error': f'Model readiness check failed: {str(e)}',
                'ready': False
            }), 500
    else:
        return jsonify({'success': False, 'error': 'Failed to set model'}), 400

@app.route('/api/model/test', methods=['POST'])
def test_model():
    """Test if current model is ready"""
    try:
        model_name = ai_manager.current_model
        if not model_name:
            return jsonify({'ready': False, 'error': 'No model selected'}), 400
            
        test_result = ai_manager.test_model_readiness(model_name)
        return jsonify(test_result)
        
    except Exception as e:
        return jsonify({'ready': False, 'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_ai_response():
    """Generate AI response for any capability"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        capability = data.get('capability', 'text_generation')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        
        if not prompt.strip():
            return jsonify({'error': 'Prompt cannot be empty'}), 400
            
        # Generate response
        result = ai_manager.generate_response(
            prompt=prompt,
            capability=capability,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Add to conversation history
        ai_manager.conversation_history.append({
            'prompt': prompt,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit history size
        if len(ai_manager.conversation_history) > ai_manager.max_history:
            ai_manager.conversation_history.pop(0)
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in generate_ai_response: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get conversation history"""
    return jsonify({
        'history': ai_manager.conversation_history[-20:],  # Last 20 entries
        'total_count': len(ai_manager.conversation_history)
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    ai_manager.conversation_history.clear()
    return jsonify({'success': True})

@app.route('/api/status')
def get_status():
    """Get application status"""
    return jsonify({
        'foundry_connected': ai_manager.base_url is not None,
        'foundry_endpoint': ai_manager.foundry_endpoint,
        'current_model': ai_manager.current_model,
        'available_models': len(ai_manager.available_models),
        'capabilities': ai_manager.capabilities,
        'conversation_count': len(ai_manager.conversation_history),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/capabilities/<capability>/examples')
def get_capability_examples(capability):
    """Get example prompts for specific capabilities"""
    examples = {
        'text_generation': [
            "Explain the benefits of local AI processing on Windows devices",
            "Write a professional email about implementing AI solutions",
            "Create a product description for Windows AI Foundry"
        ],
        'code_assistance': [
            "Create a Python function to connect to Windows AI Foundry API",
            "Write a React component for displaying AI responses",
            "Generate SQL queries for a user analytics dashboard"
        ],
        'document_analysis': [
            "Analyze this business report and extract key metrics",
            "Summarize the main points from this technical documentation",
            "Identify action items from this meeting transcript"
        ],
        'creative_writing': [
            "Write a short story about AI assistants helping developers",
            "Create marketing copy for a local AI platform",
            "Draft a blog post about the future of edge AI computing"
        ],
        'multimodal': [
            "Analyze this interface design and suggest improvements",
            "Describe the visual elements in this application screenshot",
            "Compare these two product images and highlight differences"
        ],
        'reasoning': [
            "Analyze the pros and cons of local vs cloud AI processing",
            "Evaluate the best approach for implementing real-time AI features",
            "Reason through the security implications of edge AI deployment"
        ],
        'translation': [
            "Translate this technical documentation to Spanish",
            "Convert this marketing message for international audiences",
            "Localize this user interface text for multiple languages"
        ],
        'summarization': [
            "Summarize this research paper in 3 key points",
            "Create an executive summary of this quarterly report",
            "Distill the main ideas from this lengthy document"
        ]
    }
    
    return jsonify({
        'capability': capability,
        'examples': examples.get(capability, [])
    })

# WebSocket events for real-time features
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {
        'connected': True,
        'message': 'Connected to Windows AI Foundry Demo',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🪟 Windows AI Foundry Demo - Comprehensive AI Showcase")
    print("="*60)
    
    if ai_manager.base_url:
        print(f"✅ Connected to Windows AI Foundry at {ai_manager.foundry_endpoint}")
        print(f"🤖 {len(ai_manager.available_models)} AI models available")
        print("🎯 Real AI processing enabled")
    else:
        print("⚠️  Running in demonstration mode")
        print("🎭 Simulated AI responses will be used")
        print("💡 Install Windows AI Foundry for real AI capabilities")
    
    print("\n🌟 Demo Features:")
    print("   📝 Text Generation & Creative Writing")  
    print("   💻 Code Assistance & Development Help")
    print("   📄 Document Analysis & Summarization") 
    print("   🌍 Language Translation")
    print("   🧠 Advanced Reasoning & Logic")
    print("   🖼️  Multimodal Analysis")
    
    print(f"\n🌐 Open http://localhost:5004 in your browser")
    print("🚀 Windows AI Foundry Demo is ready!")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5004, debug=ENABLE_FLASK_DEBUG, log_output=ENABLE_FLASK_DEBUG)