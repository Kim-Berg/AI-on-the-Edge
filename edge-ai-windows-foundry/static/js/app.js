/**
 * Windows AI Foundry Demo - Interactive JavaScript
 * Provides rich interactivity and real-time features
 */

class WindowsAIFoundryDemo {
    constructor() {
        this.currentCapability = null;
        this.currentModel = null;
        this.socket = null;
        this.stats = {
            totalRequests: 0,
            totalResponses: 0,
            responseTimes: [],
            successCount: 0
        };
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.setupEventListeners();
        this.loadModels();
        this.loadSystemStatus();
        this.loadHistory();
        this.startConnectionMonitoring();
        
        // Update stats display
        this.updateStatsDisplay();
        
        console.log('🚀 Windows AI Foundry Demo initialized');
    }
    
    initializeSocket() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('✅ Connected to WebSocket');
                this.updateConnectionStatus(true);
            });
            
            this.socket.on('disconnect', () => {
                console.log('❌ Disconnected from WebSocket');
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('status', (data) => {
                console.log('📊 Status update:', data);
            });
            
        } catch (error) {
            console.error('Socket initialization failed:', error);
        }
    }
    
    setupEventListeners() {
        // Model selection
        const modelSelect = document.getElementById('model-select');
        if (modelSelect) {
            modelSelect.addEventListener('change', (e) => {
                this.setModel(e.target.value);
            });
        }
        
        // Refresh models button
        const refreshModelsBtn = document.getElementById('refresh-models');
        if (refreshModelsBtn) {
            refreshModelsBtn.addEventListener('click', () => {
                this.loadModels();
            });
        }
        
        // Capability cards
        document.querySelectorAll('.capability-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.classList.contains('capability-btn') || e.target.closest('.capability-btn')) {
                    e.stopPropagation();
                }
                const capability = card.dataset.capability;
                this.selectCapability(capability);
            });
        });
        
        // Capability buttons
        document.querySelectorAll('.capability-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const card = e.target.closest('.capability-card');
                const capability = card.dataset.capability;
                this.selectCapability(capability);
                this.scrollToInteraction();
            });
        });
        
        // Generate button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateResponse();
            });
        }
        
        // Clear input button
        const clearInputBtn = document.getElementById('clear-input-btn');
        if (clearInputBtn) {
            clearInputBtn.addEventListener('click', () => {
                this.clearInput();
            });
        }
        
        // Settings toggle
        const settingsToggle = document.getElementById('settings-toggle');
        if (settingsToggle) {
            settingsToggle.addEventListener('click', () => {
                this.toggleSettings();
            });
        }
        
        // Temperature slider
        const tempSlider = document.getElementById('temperature-slider');
        if (tempSlider) {
            tempSlider.addEventListener('input', (e) => {
                document.getElementById('temperature-value').textContent = e.target.value;
            });
        }
        
        // Copy response button
        const copyBtn = document.getElementById('copy-response');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyResponse();
            });
        }
        
        // Regenerate button
        const regenerateBtn = document.getElementById('regenerate-btn');
        if (regenerateBtn) {
            regenerateBtn.addEventListener('click', () => {
                this.regenerateResponse();
            });
        }
        
        // Save response button
        const saveResponseBtn = document.getElementById('save-response-btn');
        if (saveResponseBtn) {
            saveResponseBtn.addEventListener('click', () => {
                this.saveResponse();
            });
        }
        
        // History buttons
        const refreshHistoryBtn = document.getElementById('refresh-history-btn');
        if (refreshHistoryBtn) {
            refreshHistoryBtn.addEventListener('click', () => {
                this.loadHistory();
            });
        }
        
        const clearHistoryBtn = document.getElementById('clear-history-btn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => {
                this.clearHistory();
            });
        }
        
        // Prompt textarea - Enter key handling
        const promptTextarea = document.getElementById('user-prompt');
        if (promptTextarea) {
            promptTextarea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    this.generateResponse();
                }
            });
        }
    }
    
    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            
            const modelSelect = document.getElementById('model-select');
            if (modelSelect) {
                modelSelect.innerHTML = '';
                
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    
                    // Create user-friendly display name
                    let displayName = model;
                    if (model.includes('qwen2.5-0.5b')) {
                        displayName = '🚀 Qwen2.5 0.5B (Fast)';
                    } else if (model.includes('qwen2.5-1.5b')) {
                        displayName = '⚡ Qwen2.5 1.5B (Balanced)';
                    } else if (model.includes('Phi-4-mini')) {
                        displayName = '🧠 Phi-4 Mini (Smart)';
                    } else if (model.includes('Phi-4') && !model.includes('mini')) {
                        displayName = '🎯 Phi-4 (Advanced)';
                    } else if (model.includes('Phi-3.5')) {
                        displayName = '💡 Phi-3.5 Mini';
                    } else if (model.includes('mistral')) {
                        displayName = '🔥 Mistral 7B';
                    } else if (model.includes('deepseek')) {
                        displayName = '🤔 DeepSeek R1 7B';
                    }
                    
                    option.textContent = displayName;
                    if (model === data.current_model) {
                        option.selected = true;
                    }
                    modelSelect.appendChild(option);
                });
            }
            
            this.currentModel = data.current_model;
            this.updateModelInfo(data.current_model);
            this.updateModelCount(data.models.length);
            
            console.log(`📋 Loaded ${data.models.length} models`);
            
        } catch (error) {
            console.error('Error loading models:', error);
            this.showNotification('Error loading models', 'error');
        }
    }
    
    async setModel(modelName) {
        if (!modelName) return;
        
        // Show loading state
        const modelSelect = document.getElementById('model-select');
        const modelInfo = document.getElementById('model-info');
        
        if (modelSelect) {
            modelSelect.disabled = true;
        }
        
        if (modelInfo) {
            modelInfo.innerHTML = `
                <div class="model-loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <h5>🔄 Loading Model...</h5>
                    <p>Switching to ${modelName}</p>
                    <p><small>Testing model readiness...</small></p>
                </div>
            `;
        }
        
        this.showNotification('🔄 Switching model...', 'info');
        
        try {
            const response = await fetch('/api/model/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model: modelName })
            });
            
            const result = await response.json();
            
            if (result.success && result.ready) {
                this.currentModel = modelName;
                
                // Create user-friendly model name for notification
                let friendlyName = modelName;
                if (modelName.includes('qwen2.5-0.5b')) {
                    friendlyName = 'Qwen2.5 0.5B (Fast)';
                } else if (modelName.includes('Phi-4-mini')) {
                    friendlyName = 'Phi-4 Mini (Smart)';
                } else if (modelName.includes('Phi-4')) {
                    friendlyName = 'Phi-4 (Advanced)';
                }
                
                // Show model is ready
                this.updateModelInfo(modelName);
                
                const responseTime = result.response_time ? ` (${result.response_time}ms)` : '';
                const alreadyLoaded = result.already_loaded ? ' (Already loaded)' : '';
                const attempts = result.attempts > 1 ? ` after ${result.attempts} attempts` : '';
                
                this.showNotification(`✅ ${friendlyName} is ready${responseTime}${alreadyLoaded}${attempts}`, 'success');
                console.log(`🤖 Model ready: ${modelName}, Response time: ${result.response_time}ms`);
                
                // Update any active capability display
                if (this.currentCapability) {
                    this.updateCapabilityModelInfo();
                }
                
                // Add ready indicator with response time
                setTimeout(() => {
                    const modelInfo = document.getElementById('model-info');
                    if (modelInfo) {
                        const readyIndicator = document.createElement('div');
                        readyIndicator.className = 'model-ready-indicator';
                        const statusText = result.already_loaded ? 'Already Active' : 'Ready for Inference';
                        readyIndicator.innerHTML = `
                            <i class="fas fa-check-circle"></i> 
                            Model ${statusText}
                            <span class="response-time">(Response: ${result.response_time}ms)</span>
                        `;
                        modelInfo.appendChild(readyIndicator);
                    }
                }, 100);
                
            } else if (!result.success && result.loading) {
                // Model is still loading - provide helpful feedback
                if (modelInfo) {
                    modelInfo.innerHTML = `
                        <div class="model-loading">
                            <i class="fas fa-hourglass-half fa-spin"></i>
                            <h5>⏳ Model Loading...</h5>
                            <p>${modelName} is being loaded into memory</p>
                            <p><small>This can take 1-3 minutes for larger models</small></p>
                            <div class="loading-suggestion">
                                <strong>💡 Tip:</strong> ${result.suggestion || 'Try again in 30-60 seconds'}
                            </div>
                        </div>
                    `;
                }
                
                this.showNotification('⏳ Model is loading... Please wait', 'warning');
                console.log(`⏳ Model loading: ${modelName} - ${result.error}`);
                
                // Don't change currentModel if loading failed
                if (modelSelect && this.currentModel) {
                    modelSelect.value = this.currentModel;
                }
                
            } else {
                throw new Error(result.error || 'Failed to set model');
            }
            
        } catch (error) {
            console.error('Error setting model:', error);
            this.showNotification('❌ Error switching model', 'error');
            
            // Restore previous model selection
            if (modelSelect && this.currentModel) {
                modelSelect.value = this.currentModel;
            }
            
            // Show error in model info
            if (modelInfo) {
                modelInfo.innerHTML = `
                    <div class="model-error">
                        <i class="fas fa-exclamation-triangle text-danger"></i>
                        <h5>Error switching model</h5>
                        <p>Failed to switch to ${modelName}. Please try again.</p>
                    </div>
                `;
            }
        } finally {
            // Re-enable model selector
            if (modelSelect) {
                modelSelect.disabled = false;
            }
        }
    }
    
    updateModelInfo(modelName) {
        const modelInfo = document.getElementById('model-info');
        if (modelInfo && modelName) {
            // Extract base model name from Foundry Local ID (e.g., "phi-4-mini-instruct-generic-cpu:4" -> "phi-4-mini")
            const baseModelName = modelName.split('-instruct')[0].replace(/-generic.*$/, '');
            
            const descriptions = {
                'deepseek-r1-distill-qwen-7b': {
                    title: 'DeepSeek R1 Distilled (7B)',
                    description: 'Advanced reasoning model optimized for complex problem-solving and mathematical tasks. Excellent for logical reasoning and analytical work.',
                    strengths: ['Complex Reasoning', 'Mathematics', 'Problem Solving', 'Code Analysis'],
                    speed: 'Medium',
                    size: '7B parameters'
                },
                'mistralai-Mistral-7B-Instruct-v0-2': {
                    title: 'Mistral 7B Instruct v0.2',
                    description: 'High-quality instruction-following model with excellent balance of capabilities. Great for general tasks and creative writing.',
                    strengths: ['Instruction Following', 'Creative Writing', 'General Tasks', 'Multilingual'],
                    speed: 'Medium',
                    size: '7B parameters'
                },
                'Phi-3.5-mini-instruct': {
                    title: 'Microsoft Phi-3.5 Mini',
                    description: 'Compact yet powerful model optimized for efficiency. Excellent instruction following with strong reasoning capabilities.',
                    strengths: ['Efficiency', 'Reasoning', 'Code Generation', 'Instructions'],
                    speed: 'Fast',
                    size: '3.8B parameters'
                },
                'Phi-4': {
                    title: 'Microsoft Phi-4',
                    description: 'Latest generation flagship model with exceptional reasoning and problem-solving abilities. Best for complex analytical tasks.',
                    strengths: ['Advanced Reasoning', 'Problem Solving', 'Code Generation', 'Analysis'],
                    speed: 'Medium-Slow',
                    size: '14B parameters'
                },
                'Phi-4-mini-instruct': {
                    title: 'Microsoft Phi-4 Mini',
                    description: 'Lightweight version of Phi-4 with excellent performance-to-size ratio. Perfect balance of speed and intelligence.',
                    strengths: ['Balanced Performance', 'Code Assistance', 'Reasoning', 'Efficiency'],
                    speed: 'Fast',
                    size: '14B parameters'
                },
                'qwen2.5-0.5b-instruct': {
                    title: 'Qwen2.5 Ultra-Light (0.5B)',
                    description: 'Ultra-fast lightweight model perfect for quick responses and real-time interactions. Ideal for demonstrations and rapid prototyping.',
                    strengths: ['Ultra-Fast Speed', 'Low Latency', 'Real-time Chat', 'Quick Tasks'],
                    speed: 'Ultra-Fast',
                    size: '0.5B parameters'
                },
                'qwen2.5-1.5b-instruct': {
                    title: 'Qwen2.5 Compact (1.5B)',
                    description: 'Optimally balanced model combining speed with capability. Great for most general tasks with excellent response times.',
                    strengths: ['Speed + Quality', 'General Tasks', 'Balanced Performance', 'Efficient'],
                    speed: 'Very Fast',
                    size: '1.5B parameters'
                }
            };
            
            // Try to match the exact model name first, then fall back to base name
            let modelData = descriptions[modelName] || descriptions[baseModelName];
            if (!modelData) {
                // Create dynamic description based on model characteristics
                if (modelName.includes('qwen')) {
                    modelData = {
                        title: 'Qwen Series Model',
                        description: 'Fast and efficient language model with good general capabilities.',
                        strengths: ['Speed', 'Efficiency', 'General Tasks'],
                        speed: 'Fast',
                        size: 'Compact'
                    };
                } else if (modelName.includes('phi')) {
                    modelData = {
                        title: 'Microsoft Phi Model',
                        description: 'Advanced reasoning and instruction following capabilities.',
                        strengths: ['Reasoning', 'Code Generation', 'Instructions'],
                        speed: 'Medium',
                        size: 'Optimized'
                    };
                } else if (modelName.includes('mistral')) {
                    modelData = {
                        title: 'Mistral AI Model',
                        description: 'High-quality instruction-tuned model with broad capabilities.',
                        strengths: ['Instructions', 'General Tasks', 'Multilingual'],
                        speed: 'Medium',
                        size: 'Standard'
                    };
                } else if (modelName.includes('deepseek')) {
                    modelData = {
                        title: 'DeepSeek Model',
                        description: 'Advanced reasoning and problem-solving capabilities.',
                        strengths: ['Reasoning', 'Problem Solving', 'Analysis'],
                        speed: 'Medium',
                        size: 'Large'
                    };
                } else {
                    modelData = {
                        title: 'AI Language Model',
                        description: 'Advanced AI model with comprehensive capabilities.',
                        strengths: ['General Tasks', 'Text Generation'],
                        speed: 'Variable',
                        size: 'Standard'
                    };
                }
            }
            
            const speedColor = {
                'Ultra-Fast': '#28a745',
                'Very Fast': '#20c997',
                'Fast': '#17a2b8',
                'Medium': '#ffc107',
                'Medium-Slow': '#fd7e14',
                'Slow': '#dc3545'
            }[modelData.speed] || '#6c757d';
            
            modelInfo.innerHTML = `
                <div class="model-details">
                    <h5>🤖 ${modelData.title}</h5>
                    <p class="model-description">${modelData.description}</p>
                    
                    <div class="model-specs">
                        <div class="spec-item">
                            <span class="spec-label">Speed:</span>
                            <span class="spec-value" style="color: ${speedColor}">
                                <i class="fas fa-tachometer-alt"></i> ${modelData.speed}
                            </span>
                        </div>
                        <div class="spec-item">
                            <span class="spec-label">Size:</span>
                            <span class="spec-value">${modelData.size}</span>
                        </div>
                    </div>
                    
                    <div class="model-strengths">
                        <h6>Strengths:</h6>
                        <div class="strength-tags">
                            ${modelData.strengths.map(strength => 
                                `<span class="strength-tag">${strength}</span>`
                            ).join('')}
                        </div>
                    </div>
                    
                    <div class="model-features">
                        <span class="feature-tag">🔒 Local Processing</span>
                        <span class="feature-tag">🛡️ Privacy Protected</span>
                        <span class="feature-tag">⚡ Real-time</span>
                    </div>
                </div>
            `;
        }
        
        // Update current model display
        const currentModelInfo = document.getElementById('current-model-info');
        if (currentModelInfo) {
            currentModelInfo.textContent = modelName || 'Not selected';
        }
    }
    
    updateModelCount(count) {
        const modelCountElement = document.getElementById('model-count');
        if (modelCountElement) {
            modelCountElement.textContent = count;
        }
    }
    
    updateCapabilityModelInfo() {
        // Update any model information displayed in the capability interaction area
        const capabilityModelInfo = document.getElementById('capability-model-info');
        if (capabilityModelInfo && this.currentModel) {
            let friendlyName = this.currentModel;
            if (this.currentModel.includes('qwen2.5-0.5b')) {
                friendlyName = 'Qwen2.5 0.5B';
            } else if (this.currentModel.includes('Phi-4-mini')) {
                friendlyName = 'Phi-4 Mini';
            } else if (this.currentModel.includes('Phi-4')) {
                friendlyName = 'Phi-4';
            }
            capabilityModelInfo.textContent = `Using ${friendlyName}`;
        }
    }
    
    selectCapability(capability) {
        // Update UI state
        document.querySelectorAll('.capability-card').forEach(card => {
            card.classList.remove('active');
        });
        
        const selectedCard = document.querySelector(`[data-capability="${capability}"]`);
        if (selectedCard) {
            selectedCard.classList.add('active');
        }
        
        this.currentCapability = capability;
        
        // Show interaction area
        const interactionArea = document.getElementById('interaction-area');
        if (interactionArea) {
            interactionArea.style.display = 'block';
        }
        
        // Update capability info
        this.updateCapabilityInfo(capability);
        
        // Load examples
        this.loadCapabilityExamples(capability);
        
        console.log(`🎯 Selected capability: ${capability}`);
    }
    
    updateCapabilityInfo(capability) {
        const capabilityTitles = {
            'text_generation': 'Text Generation',
            'code_assistance': 'Code Assistance',
            'document_analysis': 'Document Analysis',
            'creative_writing': 'Creative Writing',
            'multimodal': 'Multimodal Analysis',
            'reasoning': 'Advanced Reasoning',
            'translation': 'Language Translation',
            'summarization': 'Text Summarization'
        };
        
        const capabilityDescriptions = {
            'text_generation': 'Generate high-quality text for various purposes including content creation, writing assistance, and communication.',
            'code_assistance': 'Get intelligent code suggestions, debugging help, and programming guidance across multiple programming languages.',
            'document_analysis': 'Analyze documents, extract key insights, identify important information, and generate comprehensive summaries.',
            'creative_writing': 'Create engaging stories, marketing content, poetry, and other creative written materials with AI assistance.',
            'multimodal': 'Understand and analyze both visual and textual content simultaneously for comprehensive insights and analysis.',
            'reasoning': 'Perform complex logical analysis, problem-solving, critical thinking, and structured reasoning tasks.',
            'translation': 'Translate text between multiple languages with context awareness, cultural adaptation, and technical accuracy.',
            'summarization': 'Generate concise, accurate summaries of long documents, articles, and complex information sources.'
        };
        
        const titleElement = document.getElementById('current-capability');
        const descriptionElement = document.getElementById('capability-description');
        
        if (titleElement) {
            titleElement.textContent = capabilityTitles[capability] || 'Unknown Capability';
        }
        
        if (descriptionElement) {
            descriptionElement.textContent = capabilityDescriptions[capability] || 'No description available.';
        }
    }
    
    async loadCapabilityExamples(capability) {
        try {
            const response = await fetch(`/api/capabilities/${capability}/examples`);
            const data = await response.json();
            
            const examplesSection = document.getElementById('examples-section');
            const examplesList = document.getElementById('examples-list');
            
            if (examplesSection && examplesList) {
                if (data.examples && data.examples.length > 0) {
                    examplesList.innerHTML = '';
                    
                    data.examples.forEach(example => {
                        const exampleElement = document.createElement('div');
                        exampleElement.className = 'example-prompt';
                        exampleElement.textContent = example;
                        exampleElement.addEventListener('click', () => {
                            this.useExamplePrompt(example);
                        });
                        examplesList.appendChild(exampleElement);
                    });
                    
                    examplesSection.style.display = 'block';
                } else {
                    examplesSection.style.display = 'none';
                }
            }
            
        } catch (error) {
            console.error('Error loading examples:', error);
        }
    }
    
    useExamplePrompt(example) {
        const promptTextarea = document.getElementById('user-prompt');
        if (promptTextarea) {
            promptTextarea.value = example;
            promptTextarea.focus();
        }
    }
    
    async generateResponse() {
        const prompt = document.getElementById('user-prompt').value.trim();
        
        if (!prompt) {
            this.showNotification('Please enter a prompt', 'warning');
            return;
        }
        
        if (!this.currentCapability) {
            this.showNotification('Please select a capability first', 'warning');
            return;
        }
        
        // Show loading state
        this.showLoading(true);
        this.setGenerateButtonState(false);
        
        // Get settings
        const temperature = parseFloat(document.getElementById('temperature-slider').value);
        const maxTokens = parseInt(document.getElementById('max-tokens-input').value);
        
        const startTime = Date.now();
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    capability: this.currentCapability,
                    temperature: temperature,
                    max_tokens: maxTokens
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                const responseTime = Date.now() - startTime;
                this.stats.responseTimes.push(responseTime);
                this.stats.totalRequests++;
                this.stats.totalResponses++;
                this.stats.successCount++;
                
                this.displayResponse(result);
                this.updateStatsDisplay();
                this.loadHistory(); // Refresh history
                
                this.showNotification('Response generated successfully', 'success');
                console.log(`✅ Response generated in ${responseTime}ms`);
            } else {
                throw new Error(result.error || 'Failed to generate response');
            }
            
        } catch (error) {
            console.error('Error generating response:', error);
            
            // Enhanced error handling for timeout and model-specific issues
            let errorMessage = error.message;
            let notificationType = 'error';
            
            if (errorMessage.includes('timed out') || errorMessage.includes('timeout')) {
                notificationType = 'warning';
                
                // Extract timeout duration if available
                const timeoutMatch = errorMessage.match(/(\d+)\s*seconds?/);
                const timeoutDuration = timeoutMatch ? timeoutMatch[1] : 'unknown';
                
                // Provide model-specific suggestions
                if (errorMessage.includes('DeepSeek') || errorMessage.includes('Mistral')) {
                    errorMessage = `⏰ Large model timed out after ${timeoutDuration}s. Try switching to Qwen2.5 0.5B or Phi-4 Mini for faster responses.`;
                } else if (errorMessage.includes('Phi-4') && !errorMessage.includes('Mini')) {
                    errorMessage = `⏰ Model timed out after ${timeoutDuration}s. Try Phi-4 Mini or Qwen2.5 0.5B for faster responses.`;
                } else {
                    errorMessage = `⏰ Request timed out after ${timeoutDuration}s. Try shortening your prompt or switching to a faster model.`;
                }
                
                // Show retry suggestion
                setTimeout(() => {
                    this.showRetryOption();
                }, 2000);
                
            } else if (errorMessage.includes('API Error')) {
                errorMessage = `🔌 Connection issue with AI model. Please try again or switch models.`;
            }
            
            this.showNotification(errorMessage, notificationType);
            this.stats.totalRequests++;
        } finally {
            this.showLoading(false);
            this.setGenerateButtonState(true);
        }
    }
    
    displayResponse(result) {
        const responseSection = document.getElementById('response-section');
        const responseContent = document.getElementById('response-content');
        const responseModel = document.getElementById('response-model');
        const responseTimestamp = document.getElementById('response-timestamp');
        
        if (responseSection) {
            responseSection.style.display = 'block';
        }
        
        if (responseContent) {
            // Convert markdown-style formatting to HTML
            let formattedResponse = result.response
                .replace(/```(\w+)?\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>');
            
            // Wrap in paragraphs if not already formatted
            if (!formattedResponse.includes('<p>') && !formattedResponse.includes('<pre>')) {
                formattedResponse = `<p>${formattedResponse}</p>`;
            }
            
            responseContent.innerHTML = formattedResponse;
        }
        
        if (responseModel) {
            responseModel.textContent = `Model: ${result.model}`;
        }
        
        if (responseTimestamp) {
            const timestamp = new Date(result.timestamp).toLocaleString();
            responseTimestamp.textContent = timestamp;
        }
        
        // Store current response for copy/save operations
        this.currentResponse = result;
        
        // Scroll to response
        responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    showLoading(show) {
        const loadingContainer = document.getElementById('loading-container');
        const responseSection = document.getElementById('response-section');
        
        if (loadingContainer) {
            loadingContainer.style.display = show ? 'block' : 'none';
        }
        
        if (!show && responseSection) {
            // Don't hide response section when loading stops
        }
    }
    
    setGenerateButtonState(enabled) {
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.disabled = !enabled;
            generateBtn.innerHTML = enabled 
                ? '<i class="fas fa-paper-plane"></i> Generate Response'
                : '<i class="fas fa-spinner fa-spin"></i> Generating...';
        }
    }
    
    clearInput() {
        const promptTextarea = document.getElementById('user-prompt');
        if (promptTextarea) {
            promptTextarea.value = '';
            promptTextarea.focus();
        }
    }
    
    toggleSettings() {
        const settingsContent = document.getElementById('settings-content');
        const settingsToggle = document.getElementById('settings-toggle');
        
        if (settingsContent && settingsToggle) {
            const isVisible = settingsContent.style.display === 'block';
            settingsContent.style.display = isVisible ? 'none' : 'block';
            
            const icon = settingsToggle.querySelector('i');
            if (icon) {
                icon.className = isVisible ? 'fas fa-cog' : 'fas fa-times';
            }
        }
    }
    
    copyResponse() {
        if (this.currentResponse && this.currentResponse.response) {
            navigator.clipboard.writeText(this.currentResponse.response).then(() => {
                this.showNotification('Response copied to clipboard', 'success');
            }).catch(error => {
                console.error('Error copying to clipboard:', error);
                this.showNotification('Failed to copy to clipboard', 'error');
            });
        }
    }
    
    regenerateResponse() {
        this.generateResponse();
    }
    
    saveResponse() {
        if (this.currentResponse) {
            const data = {
                prompt: document.getElementById('user-prompt').value,
                response: this.currentResponse.response,
                model: this.currentResponse.model,
                capability: this.currentResponse.capability,
                timestamp: this.currentResponse.timestamp
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `windows-ai-foundry-response-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showNotification('Response saved to file', 'success');
        }
    }
    
    async loadHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            this.displayHistory(data.history);
            
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    displayHistory(history) {
        const historyContainer = document.getElementById('history-container');
        
        if (!historyContainer) return;
        
        if (!history || history.length === 0) {
            historyContainer.innerHTML = `
                <div class="history-empty">
                    <i class="fas fa-comments"></i>
                    <p>No conversations yet. Start by selecting a capability and entering a prompt.</p>
                </div>
            `;
            return;
        }
        
        historyContainer.innerHTML = '';
        
        // Show most recent conversations first
        history.reverse().forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const timestamp = new Date(item.timestamp).toLocaleString();
            
            historyItem.innerHTML = `
                <div class="history-prompt">
                    <strong>Prompt:</strong> ${this.escapeHtml(item.prompt)}
                </div>
                <div class="history-response">
                    ${this.formatResponseText(item.result.response)}
                </div>
                <div class="history-meta">
                    <span>Model: ${item.result.model}</span>
                    <span>Capability: ${item.result.capability}</span>
                    <span>Time: ${timestamp}</span>
                </div>
            `;
            
            historyContainer.appendChild(historyItem);
        });
    }
    
    async clearHistory() {
        if (confirm('Are you sure you want to clear all conversation history?')) {
            try {
                const response = await fetch('/api/history/clear', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    this.loadHistory();
                    this.showNotification('History cleared', 'success');
                }
                
            } catch (error) {
                console.error('Error clearing history:', error);
                this.showNotification('Error clearing history', 'error');
            }
        }
    }
    
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            this.updateSystemStatus(data);
            
        } catch (error) {
            console.error('Error loading system status:', error);
        }
    }
    
    async checkConnectionStatus() {
        try {
            const response = await fetch('/api/connection/status');
            const data = await response.json();
            
            this.updateConnectionStatus(data.connected);
            
            if (!data.connected) {
                // If not connected, show a more helpful message
                const statusText = document.getElementById('status-text');
                if (statusText) {
                    statusText.textContent = 'Windows AI Foundry Not Connected';
                }
            }
            
        } catch (error) {
            console.error('Error checking connection status:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    startConnectionMonitoring() {
        // Check connection every 10 seconds
        this.connectionCheckInterval = setInterval(() => {
            this.checkConnectionStatus();
        }, 10000);
        
        // Initial check
        this.checkConnectionStatus();
    }
    
    updateSystemStatus(status) {
        // Update connection status
        const foundryEndpoint = document.getElementById('foundry-endpoint');
        if (foundryEndpoint) {
            foundryEndpoint.textContent = status.foundry_endpoint || 'Demo Mode';
        }
        
        const processingMode = document.getElementById('processing-mode');
        if (processingMode) {
            processingMode.textContent = status.foundry_connected ? 'Real AI Processing' : 'Simulation Mode';
        }
        
        this.updateConnectionStatus(status.foundry_connected);
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('connection-status');
        const statusText = document.getElementById('status-text');
        
        if (statusDot) {
            statusDot.className = connected ? 'status-dot connected' : 'status-dot disconnected';
        }
        
        if (statusText) {
            statusText.textContent = connected ? 'Windows AI Foundry Connected' : 'Not Connected';
        }
        
        // Store connection state for other parts of the app
        this.isConnected = connected;
    }
    
    updateStatsDisplay() {
        const responseCountElement = document.getElementById('response-count');
        if (responseCountElement) {
            responseCountElement.textContent = this.stats.totalResponses;
        }
        
        const totalRequestsElement = document.getElementById('total-requests');
        if (totalRequestsElement) {
            totalRequestsElement.textContent = this.stats.totalRequests;
        }
        
        const avgResponseTimeElement = document.getElementById('avg-response-time');
        if (avgResponseTimeElement && this.stats.responseTimes.length > 0) {
            const avgTime = this.stats.responseTimes.reduce((a, b) => a + b, 0) / this.stats.responseTimes.length;
            avgResponseTimeElement.textContent = `${Math.round(avgTime)}ms`;
        }
        
        const successRateElement = document.getElementById('success-rate');
        if (successRateElement && this.stats.totalRequests > 0) {
            const rate = (this.stats.successCount / this.stats.totalRequests * 100).toFixed(1);
            successRateElement.textContent = `${rate}%`;
        }
    }
    
    scrollToInteraction() {
        const interactionArea = document.getElementById('interaction-area');
        if (interactionArea) {
            interactionArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <span>${this.escapeHtml(message)}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2em; padding: 0; margin-left: 10px;">&times;</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    showRetryOption() {
        const container = document.getElementById('notifications');
        if (!container) return;
        
        const retryNotification = document.createElement('div');
        retryNotification.className = 'notification info retry-suggestion';
        retryNotification.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 15px;">
                <div>
                    <strong>💡 Quick Tips:</strong><br>
                    • Try a faster model (Qwen2.5 0.5B)<br>
                    • Shorten your prompt<br>
                    • Click "Generate" to retry
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="document.getElementById('model-select').value='qwen2.5-0.5b-instruct-generic-cpu:3'; aiFoundryDemo.setModel('qwen2.5-0.5b-instruct-generic-cpu:3')" 
                            style="padding: 5px 10px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                        Switch to Fast Model
                    </button>
                    <button onclick="this.closest('.notification').remove()" 
                            style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2em; padding: 0;">&times;</button>
                </div>
            </div>
        `;
        
        container.appendChild(retryNotification);
        
        // Auto-remove after 10 seconds (longer for retry suggestions)
        setTimeout(() => {
            if (retryNotification.parentNode) {
                retryNotification.remove();
            }
        }, 10000);
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
    
    formatResponseText(text) {
        // Basic markdown-style formatting for history display
        return text
            .replace(/```[\s\S]*?```/g, '<pre style="background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto;">$&</pre>')
            .replace(/`([^`]+)`/g, '<code style="background: #f4f4f4; padding: 2px 4px; border-radius: 2px;">$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aiFoundryDemo = new WindowsAIFoundryDemo();
    console.log('🪟 Windows AI Foundry Demo ready!');
});

// Add dynamic CSS for feature tags
const style = document.createElement('style');
style.textContent = `
    .model-features {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .feature-tag {
        background: var(--primary-color);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .history-response {
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .history-response pre {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        overflow-x: auto;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    
    .history-response code {
        background: #f8f9fa;
        padding: 2px 4px;
        border-radius: 2px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
`;
document.head.appendChild(style);