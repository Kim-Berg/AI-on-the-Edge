/**
 * Azure Foundry Local Chat Playground - Frontend JavaScript
 */

class ChatPlayground {
    constructor() {
        this.selectedModels = new Set();
        this.isStreaming = false;
        this.eventSource = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadAvailableModels();
        this.updateUI();
    }

    bindEvents() {
        // Send button and message input
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Character counter
        document.getElementById('messageInput').addEventListener('input', () => {
            this.updateCharCount();
        });

        // Header controls
        document.getElementById('statusBtn').addEventListener('click', () => this.showStatus());
        document.getElementById('clearHistoryBtn').addEventListener('click', () => this.clearHistory());
        document.getElementById('refreshModelsBtn').addEventListener('click', () => this.loadAvailableModels());

        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });
    }

    async loadAvailableModels() {
        try {
            this.showLoading('Loading models...');
            const response = await fetch('/api/models/available');
            const data = await response.json();
            
            this.renderModelGrid(data.models, data.status);
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showToast('Failed to load models', 'error');
            console.error('Error loading models:', error);
        }
    }

    renderModelGrid(models, modelStatus) {
        const grid = document.getElementById('modelGrid');
        grid.innerHTML = '';

        models.forEach(modelAlias => {
            const status = modelStatus[modelAlias] || { status: 'not-initialized' };
            const card = this.createModelCard(modelAlias, status);
            grid.appendChild(card);
        });
    }

    createModelCard(modelAlias, status) {
        const card = document.createElement('div');
        card.className = 'model-card';
        card.dataset.model = modelAlias;

        if (this.selectedModels.has(modelAlias)) {
            card.classList.add('selected');
        }

        const statusClass = status.status || 'not-initialized';
        const statusText = this.getStatusText(status);

        card.innerHTML = `
            <div class="model-info">
                <h4>${this.formatModelName(modelAlias)}</h4>
                <div class="model-status">
                    <div class="status-indicator ${statusClass}"></div>
                    <span class="status-text">${statusText}</span>
                </div>
                <div class="model-description">
                    ${this.getModelDescription(modelAlias)}
                </div>
                ${status.error ? `<div class="response-error">Error: ${status.error}</div>` : ''}
            </div>
        `;

        card.addEventListener('click', () => this.toggleModel(modelAlias, card));
        
        return card;
    }

    formatModelName(alias) {
        // Custom formatting for specific models
        const customNames = {
            'qwen2.5-0.5b': 'Qwen2.5 0.5B',
            'qwen2.5-1.5b': 'Qwen2.5 1.5B',
            'qwen2.5-7b': 'Qwen2.5 7B',
            'qwen2.5-14b': 'Qwen2.5 14B',
            'qwen2.5-32b': 'Qwen2.5 32B',
            'qwen2.5-coder-0.5b': 'Qwen2.5 Coder 0.5B',
            'qwen2.5-coder-1.5b': 'Qwen2.5 Coder 1.5B',
            'qwen2.5-coder-7b': 'Qwen2.5 Coder 7B',
            'qwen2.5-coder-14b': 'Qwen2.5 Coder 14B',
            'phi-3-mini-4k': 'Phi-3 Mini (4K)',
            'phi-3-mini-128k': 'Phi-3 Mini (128K)',
            'phi-3.5-mini': 'Phi-3.5 Mini',
            'phi-4-mini': 'Phi-4 Mini',
            'phi-4': 'Phi-4',
            'phi-4-mini-reasoning': 'Phi-4 Mini Reasoning',
            'deepseek-r1-7b': 'DeepSeek R1 7B',
            'deepseek-r1-14b': 'DeepSeek R1 14B',
            'deepseek-coder-6.7b': 'DeepSeek Coder 6.7B',
            'mistral-7b-v0.2': 'Mistral 7B v0.2',
            'mistral-7b-instruct': 'Mistral 7B Instruct',
            'gemma-2-2b': 'Gemma 2 2B',
            'gemma-2-9b': 'Gemma 2 9B',
            'gemma-2-27b': 'Gemma 2 27B',
            'llama-3.2-1b': 'Llama 3.2 1B',
            'llama-3.2-3b': 'Llama 3.2 3B',
            'llama-3.1-8b': 'Llama 3.1 8B',
            'llama-3.1-70b': 'Llama 3.1 70B'
        };
        
        return customNames[alias] || alias.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getStatusText(status) {
        switch (status.status) {
            case 'ready': return 'Ready';
            case 'error': return 'Error';
            case 'initializing': return 'Initializing...';
            default: return 'Not Initialized';
        }
    }

    getModelDescription(alias) {
        const descriptions = {
            // Qwen 2.5 Series
            'qwen2.5-0.5b': 'Lightweight model, fastest response times',
            'qwen2.5-1.5b': 'Small model, good balance of speed and capability',
            'qwen2.5-7b': 'Medium model, excellent reasoning and math',
            'qwen2.5-14b': 'Large model, superior performance on complex tasks',
            'qwen2.5-32b': 'Very large model, exceptional capabilities',
            
            // Qwen 2.5 Coder Series
            'qwen2.5-coder-0.5b': 'Specialized for coding, lightweight and fast',
            'qwen2.5-coder-1.5b': 'Code-focused model, good for programming tasks',
            'qwen2.5-coder-7b': 'Advanced coding assistant, excellent code generation',
            'qwen2.5-coder-14b': 'Professional coding model, complex algorithms',
            
            // Phi Series
            'phi-3-mini-4k': 'Microsoft Phi, compact with 4K context',
            'phi-3-mini-128k': 'Microsoft Phi, extended 128K context length',
            'phi-3.5-mini': 'Latest Phi model, great reasoning capabilities',
            'phi-4-mini': 'Advanced Phi model, excellent for analysis',
            'phi-4': 'Full Phi-4 model, superior performance',
            'phi-4-mini-reasoning': 'Specialized for step-by-step reasoning',
            
            // DeepSeek Series
            'deepseek-r1-7b': 'DeepSeek reasoning model, excellent for logic',
            'deepseek-r1-14b': 'Large DeepSeek model, advanced reasoning',
            'deepseek-coder-6.7b': 'DeepSeek coding specialist, great for development',
            
            // Mistral Series
            'mistral-7b-v0.2': 'Mistral AI model, creative and balanced',
            'mistral-7b-instruct': 'Instruction-tuned Mistral, follows commands well',
            
            // Gemma Series
            'gemma-2-2b': 'Google Gemma, lightweight and versatile',
            'gemma-2-9b': 'Medium Gemma model, good general capabilities',
            'gemma-2-27b': 'Large Gemma model, advanced performance',
            
            // Llama Series
            'llama-3.2-1b': 'Meta Llama, compact and efficient',
            'llama-3.2-3b': 'Medium Llama model, balanced performance',
            'llama-3.1-8b': 'Large Llama model, excellent capabilities',
            'llama-3.1-70b': 'Very large Llama model, top-tier performance'
        };
        return descriptions[alias] || 'Advanced AI model for various tasks';
    }

    async toggleModel(modelAlias, cardElement) {
        if (this.selectedModels.has(modelAlias)) {
            // Deselect model
            this.selectedModels.delete(modelAlias);
            cardElement.classList.remove('selected');
        } else {
            // Select and initialize model if needed
            const status = this.getModelStatus(modelAlias);
            
            if (status !== 'ready') {
                await this.initializeModel(modelAlias, cardElement);
            }
            
            this.selectedModels.add(modelAlias);
            cardElement.classList.add('selected');
        }
        
        this.updateUI();
    }

    getModelStatus(modelAlias) {
        const card = document.querySelector(`[data-model="${modelAlias}"]`);
        const indicator = card?.querySelector('.status-indicator');
        
        if (indicator?.classList.contains('ready')) return 'ready';
        if (indicator?.classList.contains('error')) return 'error';
        if (indicator?.classList.contains('initializing')) return 'initializing';
        return 'not-initialized';
    }

    async initializeModel(modelAlias, cardElement) {
        try {
            // Update UI to show initializing state
            cardElement.classList.add('initializing');
            const indicator = cardElement.querySelector('.status-indicator');
            const statusText = cardElement.querySelector('.status-text');
            
            indicator.className = 'status-indicator initializing';
            statusText.textContent = 'Initializing...';
            
            this.showLoading(`Initializing ${this.formatModelName(modelAlias)}...`);

            const response = await fetch('/api/models/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model: modelAlias })
            });

            const data = await response.json();
            
            this.hideLoading();
            cardElement.classList.remove('initializing');

            if (data.success) {
                indicator.className = 'status-indicator ready';
                statusText.textContent = 'Ready';
                this.showToast(`${this.formatModelName(modelAlias)} initialized successfully`, 'success');
            } else {
                indicator.className = 'status-indicator error';
                statusText.textContent = 'Error';
                const errorDiv = cardElement.querySelector('.response-error') || document.createElement('div');
                errorDiv.className = 'response-error';
                errorDiv.textContent = `Error: ${data.error}`;
                cardElement.appendChild(errorDiv);
                
                this.showToast(`Failed to initialize ${this.formatModelName(modelAlias)}`, 'error');
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            cardElement.classList.remove('initializing');
            console.error('Error initializing model:', error);
            throw error;
        }
    }

    updateUI() {
        const sendBtn = document.getElementById('sendBtn');
        const selectedModelsSpan = document.getElementById('selectedModels');
        
        const hasSelectedModels = this.selectedModels.size > 0;
        const hasMessage = document.getElementById('messageInput').value.trim().length > 0;
        
        sendBtn.disabled = !hasSelectedModels || !hasMessage || this.isStreaming;
        
        if (this.selectedModels.size === 0) {
            selectedModelsSpan.textContent = 'No models selected';
        } else if (this.selectedModels.size === 1) {
            selectedModelsSpan.textContent = `Selected: ${this.formatModelName([...this.selectedModels][0])}`;
        } else {
            selectedModelsSpan.textContent = `Selected: ${this.selectedModels.size} models`;
        }
        
        this.updateCharCount();
    }

    updateCharCount() {
        const input = document.getElementById('messageInput');
        const charCount = document.getElementById('charCount');
        const count = input.value.length;
        charCount.textContent = `${count}/2000`;
        
        if (count > 1800) {
            charCount.style.color = 'var(--danger-color)';
        } else if (count > 1500) {
            charCount.style.color = 'var(--warning-color)';
        } else {
            charCount.style.color = 'var(--text-muted)';
        }
        
        // Removed this.updateUI() to prevent infinite recursion
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        console.log('sendMessage called:', { message, selectedModels: [...this.selectedModels], isStreaming: this.isStreaming });
        
        if (!message) {
            console.log('No message provided');
            alert('Please enter a message');
            return;
        }
        
        if (this.selectedModels.size === 0) {
            console.log('No models selected');
            alert('Please select at least one model first');
            return;
        }
        
        if (this.isStreaming) {
            console.log('Already streaming');
            return;
        }

        // Clear input and disable UI
        messageInput.value = '';
        this.isStreaming = true;
        this.updateUI();

        // Add user message to chat
        this.addUserMessage(message);

        try {
            await this.sendStreamingMessage(message);
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('Failed to send message', 'error');
        } finally {
            this.isStreaming = false;
            this.updateUI();
        }
    }

    addUserMessage(message) {
        const chatMessages = document.getElementById('chatMessages');
        
        // Remove welcome message if present
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';

        const userMessage = document.createElement('div');
        userMessage.className = 'user-message';
        userMessage.innerHTML = `
            <div class="message-content">${this.escapeHtml(message)}</div>
            <div class="timestamp">${new Date().toLocaleTimeString()}</div>
        `;

        messageGroup.appendChild(userMessage);
        chatMessages.appendChild(messageGroup);
        
        this.scrollToBottom();
        return messageGroup;
    }

    async sendStreamingMessage(message) {
        const selectedModelsArray = [...this.selectedModels];
        const messageGroup = document.querySelector('.message-group:last-child');
        
        // Create responses container
        const responsesContainer = document.createElement('div');
        responsesContainer.className = 'model-responses';
        messageGroup.appendChild(responsesContainer);

        // Create response elements for each model
        const responseElements = {};
        selectedModelsArray.forEach(model => {
            const responseDiv = this.createResponseElement(model);
            responsesContainer.appendChild(responseDiv);
            responseElements[model] = responseDiv.querySelector('.response-content');
        });

        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    models: selectedModelsArray
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.handleStreamEvent(data, responseElements);
                        } catch (e) {
                            console.error('Error parsing stream data:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Streaming error:', error);
            // Show error in all response elements
            Object.keys(responseElements).forEach(model => {
                responseElements[model].innerHTML = `<span class="response-error">Error: ${error.message}</span>`;
                responseElements[model].closest('.model-response').classList.remove('streaming');
            });
        }
    }

    handleStreamEvent(data, responseElements) {
        switch (data.type) {
            case 'start':
                console.log('Streaming started for message:', data.message);
                break;
                
            case 'model_start':
                console.log('Model started:', data.model);
                if (responseElements[data.model]) {
                    responseElements[data.model].closest('.model-response').classList.add('streaming');
                }
                break;
                
            case 'chunk':
                if (responseElements[data.model]) {
                    responseElements[data.model].textContent += data.content;
                    this.scrollToBottom();
                }
                break;
                
            case 'model_complete':
                console.log('Model completed:', data.model);
                if (responseElements[data.model]) {
                    responseElements[data.model].closest('.model-response').classList.remove('streaming');
                }
                break;
                
            case 'error':
                console.error('Model error:', data.model, data.error);
                if (responseElements[data.model]) {
                    responseElements[data.model].innerHTML = `<span class="response-error">Error: ${data.error}</span>`;
                    responseElements[data.model].closest('.model-response').classList.remove('streaming');
                }
                break;
                
            case 'complete':
                console.log('All responses completed');
                break;
        }
    }

    createResponseElement(modelAlias) {
        const responseDiv = document.createElement('div');
        responseDiv.className = 'model-response';
        responseDiv.innerHTML = `
            <div class="response-header">
                <div class="model-name">
                    <i class="fas fa-robot"></i>
                    ${this.formatModelName(modelAlias)}
                    <div class="streaming-indicator" style="display: none;"></div>
                </div>
            </div>
            <div class="response-content"></div>
        `;
        return responseDiv;
    }

    async showStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            let statusHtml = '<div class="status-section">';
            statusHtml += '<h4><i class="fas fa-cogs"></i> Model Status</h4>';
            statusHtml += '<div class="status-grid">';
            
            Object.entries(data.models).forEach(([model, status]) => {
                const statusClass = status.status || 'not-initialized';
                statusHtml += `
                    <div class="status-item">
                        <div class="status-indicator ${statusClass}"></div>
                        <div class="status-info">
                            <strong>${this.formatModelName(model)}</strong>
                            <div class="status-details">
                                Status: ${this.getStatusText(status)}<br>
                                ${status.initialized_at ? `Initialized: ${new Date(status.initialized_at).toLocaleString()}` : ''}
                                ${status.error ? `<br><span class="response-error">Error: ${status.error}</span>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            statusHtml += '</div></div>';
            statusHtml += `<div class="status-section">
                <h4><i class="fas fa-comments"></i> Chat Statistics</h4>
                <p>Total messages in history: ${data.history_count}</p>
                <p>Available models: ${data.available_models.length}</p>
            </div>`;
            
            document.getElementById('statusModalBody').innerHTML = statusHtml;
            this.showModal('statusModal');
        } catch (error) {
            console.error('Error loading status:', error);
            this.showToast('Failed to load status', 'error');
        }
    }

    async clearHistory() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }

        try {
            const response = await fetch('/api/history/clear', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-content">
                            <i class="fas fa-comments"></i>
                            <h3>Welcome to Azure Foundry Local Chat Playground!</h3>
                            <p>Select one or more models above and start chatting with local AI models.</p>
                            <ul class="features">
                                <li><i class="fas fa-check"></i> Compare responses from multiple models</li>
                                <li><i class="fas fa-check"></i> Real-time streaming responses</li>
                                <li><i class="fas fa-check"></i> Local AI processing (no cloud required)</li>
                                <li><i class="fas fa-check"></i> Conversation history</li>
                            </ul>
                        </div>
                    </div>
                `;
                this.showToast('Chat history cleared', 'success');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            this.showToast('Failed to clear history', 'error');
        }
    }

    showModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }

    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        overlay.querySelector('p').textContent = message;
        overlay.style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${this.escapeHtml(message)}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => container.removeChild(toast), 300);
        }, 4000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for modal management
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatPlayground = new ChatPlayground();
});

// Add slideOut animation to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .status-section {
        margin-bottom: 25px;
    }
    
    .status-section h4 {
        color: var(--primary-color);
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .status-grid {
        display: grid;
        gap: 15px;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: var(--bg-secondary);
        border-radius: var(--border-radius);
    }
    
    .status-info strong {
        display: block;
        margin-bottom: 4px;
        color: var(--text-primary);
    }
    
    .status-details {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }
`;
document.head.appendChild(style);