"""
Azure Foundry Local Chat Playground - Real Implementation
This version works with actual Azure Foundry Local service via REST API
"""

import os
import json
import logging
import subprocess
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

class FoundryLocalChatManager:
    """Manages Azure Foundry Local models and chat sessions via REST API"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.chat_history: List[Dict] = []
        self.max_history = int(os.getenv('MAX_HISTORY_MESSAGES', 50))
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.foundry_endpoint = None
        self.foundry_port = None
        self.base_url = None
        
        # Initialize Foundry Local connection
        self._initialize_foundry_connection()
        
    def _initialize_foundry_connection(self):
        """Initialize connection to Foundry Local service"""
        try:
            # Check if Foundry Local service is running
            result = subprocess.run(['foundry', 'service', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.info("Starting Azure Foundry Local service...")
                subprocess.run(['foundry', 'service', 'start'], 
                             capture_output=True, text=True, timeout=30)
                time.sleep(5)  # Wait for service to start
            
            # Get service endpoint information
            status_result = subprocess.run(['foundry', 'service', 'status'], 
                                         capture_output=True, text=True, timeout=10)
            
            if status_result.returncode == 0:
                # Parse output to find endpoint (this is a simplified approach)
                # In practice, you might need to check foundry service configuration
                self.foundry_endpoint = "http://localhost"
                # Default port - this may vary, check foundry service status output
                self.foundry_port = self._get_foundry_port()
                self.base_url = f"{self.foundry_endpoint}:{self.foundry_port}"
                logger.info(f"Connected to Foundry Local at {self.base_url}")
            else:
                raise Exception("Failed to start or connect to Foundry Local service")
                
        except Exception as e:
            logger.error(f"Failed to initialize Foundry Local connection: {str(e)}")
            raise
    
    def _get_foundry_port(self):
        """Get the port that Foundry Local is running on"""
        try:
            # Try to find the port from foundry service status
            result = subprocess.run(['foundry', 'service', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            # Look for port in output - Foundry Local shows URL like http://127.0.0.1:PORT/
            lines = result.stdout.split('\n')
            for line in lines:
                if 'http://127.0.0.1:' in line or 'http://localhost:' in line:
                    # Extract port number from URL
                    import re
                    port_match = re.search(r':(\d+)', line)
                    if port_match:
                        return int(port_match.group(1))
            
            # Default fallback port
            return 51496
        except:
            return 51496
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Foundry Local"""
        try:
            result = subprocess.run(['foundry', 'model', 'list'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                # Parse the model list output
                models = []
                lines = result.stdout.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for lines with model aliases (first column after header)
                    if line and not line.startswith('#') and not line.startswith('Alias') and not line.startswith('---'):
                        # Extract model alias (first column)
                        parts = line.split()
                        if parts and any(keyword in parts[0].lower() for keyword in 
                                       ['qwen', 'phi', 'llama', 'gemma', 'mistral', 'deepseek']):
                            model_alias = parts[0]
                            if model_alias not in models:  # Avoid duplicates
                                models.append(model_alias)
                
                # If no models found in list, provide comprehensive list of available models
                if not models:
                    models = [
                        # Qwen 2.5 Series
                        'qwen2.5-0.5b',
                        'qwen2.5-1.5b',
                        'qwen2.5-7b',
                        'qwen2.5-14b',
                        'qwen2.5-32b',
                        
                        # Qwen 2.5 Coder Series
                        'qwen2.5-coder-0.5b',
                        'qwen2.5-coder-1.5b',
                        'qwen2.5-coder-7b',
                        'qwen2.5-coder-14b',
                        
                        # Phi Series
                        'phi-3-mini-4k',
                        'phi-3-mini-128k',
                        'phi-3.5-mini',
                        'phi-4-mini',
                        'phi-4',
                        'phi-4-mini-reasoning',
                        
                        # DeepSeek Series
                        'deepseek-r1-7b',
                        'deepseek-r1-14b',
                        'deepseek-coder-6.7b',
                        
                        # Mistral Series
                        'mistral-7b-v0.2',
                        'mistral-7b-instruct',
                        
                        # Gemma Series
                        'gemma-2-2b',
                        'gemma-2-9b',
                        'gemma-2-27b',
                        
                        # Llama Series
                        'llama-3.2-1b',
                        'llama-3.2-3b',
                        'llama-3.1-8b',
                        'llama-3.1-70b'
                    ]
                
                return models
            else:
                logger.warning("Failed to get model list, using defaults")
                return [
                    'qwen2.5-0.5b', 'qwen2.5-1.5b', 'qwen2.5-coder-0.5b', 'qwen2.5-coder-1.5b',
                    'phi-3-mini-4k', 'phi-3.5-mini', 'phi-4-mini', 'phi-4',
                    'deepseek-r1-7b', 'mistral-7b-v0.2', 'gemma-2-2b', 'llama-3.2-1b'
                ]
                
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return [
                'qwen2.5-0.5b', 'qwen2.5-1.5b', 'qwen2.5-coder-0.5b', 'qwen2.5-coder-1.5b',
                'phi-3-mini-4k', 'phi-3.5-mini', 'phi-4-mini', 'phi-4',
                'deepseek-r1-7b', 'mistral-7b-v0.2', 'gemma-2-2b', 'llama-3.2-1b'
            ]
    
    def get_model_id_mapping(self) -> Dict[str, str]:
        """Get mapping from model alias to full model ID for API calls"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                mapping = {}
                
                # Create mapping from alias to full model ID using smart matching
                for model in data.get('data', []):
                    model_id = model.get('id', '').lower()
                    if model_id:
                        # Qwen 2.5 Series
                        if 'qwen2.5' in model_id and 'coder' not in model_id:
                            if '0.5b' in model_id:
                                mapping['qwen2.5-0.5b'] = model.get('id', '')
                            elif '1.5b' in model_id:
                                mapping['qwen2.5-1.5b'] = model.get('id', '')
                            elif '7b' in model_id:
                                mapping['qwen2.5-7b'] = model.get('id', '')
                            elif '14b' in model_id:
                                mapping['qwen2.5-14b'] = model.get('id', '')
                            elif '32b' in model_id:
                                mapping['qwen2.5-32b'] = model.get('id', '')
                        
                        # Qwen 2.5 Coder Series
                        elif 'qwen2.5' in model_id and 'coder' in model_id:
                            if '0.5b' in model_id:
                                mapping['qwen2.5-coder-0.5b'] = model.get('id', '')
                            elif '1.5b' in model_id:
                                mapping['qwen2.5-coder-1.5b'] = model.get('id', '')
                            elif '7b' in model_id:
                                mapping['qwen2.5-coder-7b'] = model.get('id', '')
                            elif '14b' in model_id:
                                mapping['qwen2.5-coder-14b'] = model.get('id', '')
                        
                        # Phi Series
                        elif 'phi-4' in model_id:
                            if 'mini' in model_id and 'reasoning' in model_id:
                                mapping['phi-4-mini-reasoning'] = model.get('id', '')
                            elif 'mini' in model_id:
                                mapping['phi-4-mini'] = model.get('id', '')
                            else:
                                mapping['phi-4'] = model.get('id', '')
                        elif 'phi-3.5' in model_id and 'mini' in model_id:
                            mapping['phi-3.5-mini'] = model.get('id', '')
                        elif 'phi-3' in model_id and 'mini' in model_id:
                            if '128k' in model_id:
                                mapping['phi-3-mini-128k'] = model.get('id', '')
                            elif '4k' in model_id:
                                mapping['phi-3-mini-4k'] = model.get('id', '')
                        
                        # DeepSeek Series
                        elif 'deepseek-r1' in model_id:
                            if '7b' in model_id:
                                mapping['deepseek-r1-7b'] = model.get('id', '')
                            elif '14b' in model_id:
                                mapping['deepseek-r1-14b'] = model.get('id', '')
                        elif 'deepseek-coder' in model_id:
                            if '6.7b' in model_id:
                                mapping['deepseek-coder-6.7b'] = model.get('id', '')
                        
                        # Mistral Series
                        elif 'mistral' in model_id and '7b' in model_id:
                            if 'instruct' in model_id:
                                mapping['mistral-7b-instruct'] = model.get('id', '')
                            else:
                                mapping['mistral-7b-v0.2'] = model.get('id', '')
                        
                        # Gemma Series
                        elif 'gemma' in model_id:
                            if '2b' in model_id:
                                mapping['gemma-2-2b'] = model.get('id', '')
                            elif '9b' in model_id:
                                mapping['gemma-2-9b'] = model.get('id', '')
                            elif '27b' in model_id:
                                mapping['gemma-2-27b'] = model.get('id', '')
                        
                        # Llama Series
                        elif 'llama' in model_id:
                            if '3.2' in model_id:
                                if '1b' in model_id:
                                    mapping['llama-3.2-1b'] = model.get('id', '')
                                elif '3b' in model_id:
                                    mapping['llama-3.2-3b'] = model.get('id', '')
                            elif '3.1' in model_id:
                                if '8b' in model_id:
                                    mapping['llama-3.1-8b'] = model.get('id', '')
                                elif '70b' in model_id:
                                    mapping['llama-3.1-70b'] = model.get('id', '')
                
                return mapping
                
        except Exception as e:
            logger.error(f"Error getting model ID mapping: {str(e)}")
        
        return {}
    
    def initialize_model(self, model_alias: str) -> bool:
        """Initialize a Foundry Local model"""
        try:
            logger.info(f"Initializing model: {model_alias}")
            
            # Check if model is already running via the API first
            try:
                response = requests.get(f"{self.base_url}/models", timeout=10)
                if response.status_code == 200:
                    running_models = response.json()
                    for model in running_models:
                        if model.get('alias') == model_alias:
                            logger.info(f"Model {model_alias} is already running")
                            self.models[model_alias] = {
                                'status': 'ready',
                                'initialized_at': datetime.now().isoformat(),
                                'endpoint': f"{self.foundry_endpoint}:{self.foundry_port}"
                            }
                            return True
            except Exception as e:
                logger.debug(f"Could not check running models: {e}")
            
            # Use foundry CLI to start the model
            # Using --retain to keep model loaded and a simple prompt to test initialization
            result = subprocess.run(['foundry', 'model', 'run', model_alias, '--retain', '--prompt', 'Hi'], 
                                  capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                self.models[model_alias] = {
                    'status': 'ready',
                    'initialized_at': datetime.now().isoformat(),
                    'endpoint': f"{self.foundry_endpoint}:{self.foundry_port}"
                }
                logger.info(f"Model {model_alias} initialized successfully")
                return True
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                logger.error(f"Failed to initialize {model_alias}: {error_msg}")
                self.models[model_alias] = {
                    'status': 'error',
                    'error': error_msg,
                    'initialized_at': datetime.now().isoformat()
                }
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout initializing model {model_alias}")
            self.models[model_alias] = {
                'status': 'error',
                'error': 'Initialization timeout',
                'initialized_at': datetime.now().isoformat()
            }
            return False
        except Exception as e:
            logger.error(f"Failed to initialize model {model_alias}: {str(e)}")
            self.models[model_alias] = {
                'status': 'error',
                'error': str(e),
                'initialized_at': datetime.now().isoformat()
            }
            return False
    
    def chat_with_model(self, model_alias: str, message: str, stream: bool = True) -> Any:
        """Send a chat message to Foundry Local model via REST API"""
        if model_alias not in self.models:
            raise ValueError(f"Model {model_alias} not initialized")
        
        if self.models[model_alias].get('status') != 'ready':
            raise ValueError(f"Model {model_alias} not ready")
        
        # Get the full model ID for API calls
        model_mapping = self.get_model_id_mapping()
        model_id = model_mapping.get(model_alias, model_alias)
        
        logger.info(f"Model mapping for {model_alias}: {model_id}")
        logger.info(f"Available mappings: {model_mapping}")
        
        if not model_id:
            raise ValueError(f"Could not find model ID for alias {model_alias}")
        
        # Prepare the request for Foundry Local REST API
        endpoint = f"{self.foundry_endpoint}:{self.foundry_port}/v1/chat/completions"
        
        # Prepare messages with recent history
        messages = []
        
        # Add recent conversation history (last 5 exchanges)
        recent_history = self.chat_history[-5:] if self.chat_history else []
        for hist_msg in recent_history:
            messages.append({"role": "user", "content": hist_msg.get('user', '')})
            for model, response in hist_msg.get('responses', {}).items():
                if model == model_alias and response:
                    messages.append({"role": "assistant", "content": response})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Prepare request payload
        payload = {
            "model": model_id,  # Use the full model ID instead of alias
            "messages": messages,
            "stream": stream,
            "temperature": float(os.getenv('TEMPERATURE', 0.7)),
            "max_tokens": int(os.getenv('MAX_TOKENS', 1000))
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            if stream:
                # Handle streaming response
                response = requests.post(endpoint, json=payload, headers=headers, stream=True, timeout=60)
                response.raise_for_status()
                
                def stream_generator():
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                try:
                                    data = json.loads(line_str[6:])
                                    if 'choices' in data and data['choices']:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta and delta['content']:
                                            yield MockChunk(delta['content'])
                                except json.JSONDecodeError:
                                    continue
                
                return stream_generator()
            else:
                # Handle non-streaming response
                response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                if 'choices' in data and data['choices']:
                    content = data['choices'][0]['message']['content']
                    return MockResponse(content)
                else:
                    raise Exception("Invalid response format")
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            # Fallback to CLI interaction if REST API fails
            return self._chat_via_cli(model_alias, message, stream)
    
    def _chat_via_cli(self, model_alias: str, message: str, stream: bool = True):
        """Fallback method using CLI if REST API is not available"""
        try:
            # Use foundry CLI for chat
            result = subprocess.run(['foundry', 'model', 'run', model_alias, '--prompt', message], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                if stream:
                    # Simulate streaming for CLI response
                    def cli_stream_generator():
                        words = response_text.split()
                        for i, word in enumerate(words):
                            yield MockChunk(word + (" " if i < len(words) - 1 else ""))
                            time.sleep(0.05)  # Simulate typing
                    
                    return cli_stream_generator()
                else:
                    return MockResponse(response_text)
            else:
                raise Exception(f"CLI execution failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"CLI chat failed: {str(e)}")
            raise
    
    def add_to_history(self, user_message: str, responses: Dict[str, str]):
        """Add a conversation to chat history"""
        self.chat_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'responses': responses
        })
        
        # Trim history if too long
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all initialized models"""
        return {
            model_alias: {
                'status': info.get('status', 'unknown'),
                'error': info.get('error'),
                'initialized_at': info.get('initialized_at')
            }
            for model_alias, info in self.models.items()
        }
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()

# Mock classes for compatibility
class MockChunk:
    def __init__(self, content):
        self.choices = [type('obj', (object,), {
            'delta': type('obj', (object,), {'content': content})()
        })]

class MockResponse:
    def __init__(self, content):
        self.choices = [type('obj', (object,), {
            'message': type('obj', (object,), {'content': content})()
        })]

# Initialize the chat manager
try:
    chat_manager = FoundryLocalChatManager()
    FOUNDRY_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to initialize Foundry Local: {str(e)}")
    logger.info("Falling back to mock mode")
    # Import mock manager as fallback
    from demo_app import MockFoundryLocalManager
    chat_manager = MockFoundryLocalManager()
    FOUNDRY_AVAILABLE = False

@app.route('/')
def index():
    """Main chat interface"""
    available_models = chat_manager.get_available_models()
    model_status = chat_manager.get_model_status()
    return render_template('index.html', 
                         available_models=available_models,
                         model_status=model_status)

@app.route('/api/models/available')
def get_available_models():
    """Get list of available models"""
    return jsonify({
        'models': chat_manager.get_available_models(),
        'status': chat_manager.get_model_status(),
        'foundry_available': FOUNDRY_AVAILABLE
    })

@app.route('/api/models/initialize', methods=['POST'])
def initialize_model():
    """Initialize a specific model"""
    data = request.get_json()
    model_alias = data.get('model')
    
    if not model_alias:
        return jsonify({'error': 'Model alias required'}), 400
    
    # Run initialization in background thread to avoid blocking
    def init_task():
        return chat_manager.initialize_model(model_alias)
    
    try:
        future = chat_manager.executor.submit(init_task)
        success = future.result(timeout=300)  # 5 minute timeout
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Model {model_alias} initialized successfully',
                'status': chat_manager.get_model_status()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to initialize model {model_alias}',
                'status': chat_manager.get_model_status()
            }), 500
            
    except Exception as e:
        logger.error(f"Error initializing model {model_alias}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send message to selected models and get responses"""
    data = request.get_json()
    message = data.get('message', '').strip()
    selected_models = data.get('models', [])
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    if not selected_models:
        return jsonify({'error': 'At least one model must be selected'}), 400
    
    responses = {}
    errors = {}
    
    # Get responses from each selected model
    for model_alias in selected_models:
        try:
            if model_alias not in chat_manager.models:
                errors[model_alias] = "Model not initialized"
                continue
            
            if chat_manager.models[model_alias].get('status') != 'ready':
                errors[model_alias] = "Model not ready"
                continue
            
            # Get non-streaming response for this endpoint
            response = chat_manager.chat_with_model(model_alias, message, stream=False)
            responses[model_alias] = response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting response from {model_alias}: {str(e)}")
            errors[model_alias] = str(e)
    
    # Add to history if we got any successful responses
    if responses:
        chat_manager.add_to_history(message, responses)
    
    return jsonify({
        'message': message,
        'responses': responses,
        'errors': errors,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Stream responses from multiple models"""
    data = request.get_json()
    message = data.get('message', '').strip()
    selected_models = data.get('models', [])
    
    if not message or not selected_models:
        return jsonify({'error': 'Message and models are required'}), 400
    
    def generate_responses():
        """Generate streaming responses from multiple models"""
        yield f"data: {json.dumps({'type': 'start', 'message': message})}\n\n"
        
        responses = {}
        
        # Process each model
        for model_alias in selected_models:
            try:
                if model_alias not in chat_manager.models or \
                   chat_manager.models[model_alias].get('status') != 'ready':
                    yield f"data: {json.dumps({'type': 'error', 'model': model_alias, 'error': 'Model not ready'})}\n\n"
                    continue
                
                yield f"data: {json.dumps({'type': 'model_start', 'model': model_alias})}\n\n"
                
                # Get streaming response
                stream = chat_manager.chat_with_model(model_alias, message, stream=True)
                model_response = ""
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        model_response += content
                        yield f"data: {json.dumps({'type': 'chunk', 'model': model_alias, 'content': content})}\n\n"
                
                responses[model_alias] = model_response
                yield f"data: {json.dumps({'type': 'model_complete', 'model': model_alias})}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error with {model_alias}: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'model': model_alias, 'error': str(e)})}\n\n"
        
        # Add to history
        if responses:
            chat_manager.add_to_history(message, responses)
        
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    
    return Response(generate_responses(), mimetype='text/event-stream',
                   headers={'Cache-Control': 'no-cache'})

@app.route('/api/history')
def get_history():
    """Get chat history"""
    return jsonify({
        'history': chat_manager.chat_history,
        'total_messages': len(chat_manager.chat_history)
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear chat history"""
    chat_manager.clear_history()
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/status')
def get_status():
    """Get application status"""
    return jsonify({
        'models': chat_manager.get_model_status(),
        'history_count': len(chat_manager.chat_history),
        'available_models': chat_manager.get_available_models(),
        'foundry_available': FOUNDRY_AVAILABLE
    })

if __name__ == '__main__':
    print("🚀 Starting Azure Foundry Local Chat Playground...")
    
    if FOUNDRY_AVAILABLE:
        print("✅ Connected to Azure Foundry Local service")
        print("🤖 Real AI models will be used")
    else:
        print("⚠️  Running in demo mode (Foundry Local not available)")
        print("🎭 Mock responses will be used")
    
    print("")
    print("🌟 Azure Foundry Local Chat Playground is ready!")
    print("🌐 Open http://localhost:5001 in your browser")
    print("💡 Tip: Model initialization may take several minutes for first-time downloads")
    
    app.run(debug=True, host='0.0.0.0', port=5001)