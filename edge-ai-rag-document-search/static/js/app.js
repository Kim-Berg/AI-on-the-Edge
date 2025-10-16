// RAG Document Search Demo - JavaScript

// State management
let currentDocuments = [];
let currentStats = {};
let selectedFile = null;
let deleteDocId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadDocuments();
    loadStats();
});

// Initialize the application
function initializeApp() {
    console.log('Initializing RAG Document Search Demo...');
    updateStatus('connected', 'Ready');
    checkConnectionStatus();
    loadModels();
}

// Check Foundry connection status
async function checkConnectionStatus() {
    try {
        const response = await fetch('/api/connection/status');
        const data = await response.json();
        
        const foundryStatus = document.getElementById('foundryStatus');
        const foundryStatusText = document.getElementById('foundryStatusText');
        
        if (data.connected) {
            foundryStatus.classList.add('connected');
            foundryStatus.classList.remove('disconnected');
            foundryStatusText.textContent = 'Foundry Connected';
            console.log('✅ Connected to Windows AI Foundry:', data.base_url);
        } else {
            foundryStatus.classList.add('disconnected');
            foundryStatus.classList.remove('connected');
            foundryStatusText.textContent = 'Foundry Disconnected';
            console.warn('⚠️ Foundry not connected - embeddings only mode');
        }
    } catch (error) {
        console.error('Error checking connection:', error);
    }
}

// Load available models
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        if (!data.success) {
            console.error('Failed to load models:', data.error);
            return;
        }
        
        const modelSelect = document.getElementById('modelSelect');
        const modelDetails = document.getElementById('modelDetails');
        
        if (data.models && data.models.length > 0) {
            modelSelect.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                
                // Create user-friendly display names
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
            
            updateModelDetails(data.current_model);
            console.log(`📋 Loaded ${data.models.length} models`);
        } else {
            modelSelect.innerHTML = '<option>No models available</option>';
            modelDetails.innerHTML = '<p style="color: var(--warning-color);">⚠️ No AI models available. Foundry may not be connected.</p>';
        }
        
    } catch (error) {
        console.error('Error loading models:', error);
        document.getElementById('modelSelect').innerHTML = '<option>Error loading models</option>';
    }
}

// Update model details display
function updateModelDetails(modelName) {
    const modelDetails = document.getElementById('modelDetails');
    const currentModelSpan = document.getElementById('currentModel');
    
    if (!modelName) {
        modelDetails.innerHTML = '<p>No model selected</p>';
        currentModelSpan.textContent = 'No Model';
        return;
    }
    
    // Extract model info
    let modelInfo = {
        name: modelName,
        type: 'General',
        speed: 'Medium',
        size: 'Unknown'
    };
    
    if (modelName.includes('qwen2.5-0.5b')) {
        modelInfo = { name: 'Qwen 2.5 0.5B', type: 'Fast & Efficient', speed: 'Very Fast', size: '0.5B parameters' };
    } else if (modelName.includes('qwen2.5-1.5b')) {
        modelInfo = { name: 'Qwen 2.5 1.5B', type: 'Balanced', speed: 'Fast', size: '1.5B parameters' };
    } else if (modelName.includes('Phi-4-mini')) {
        modelInfo = { name: 'Phi-4 Mini', type: 'Reasoning', speed: 'Fast', size: '4B parameters' };
    } else if (modelName.includes('Phi-4')) {
        modelInfo = { name: 'Phi-4', type: 'Advanced Reasoning', speed: 'Medium', size: '14B parameters' };
    } else if (modelName.includes('Phi-3.5')) {
        modelInfo = { name: 'Phi-3.5 Mini', type: 'Compact', speed: 'Fast', size: '3.8B parameters' };
    } else if (modelName.includes('mistral')) {
        modelInfo = { name: 'Mistral 7B', type: 'General Purpose', speed: 'Medium', size: '7B parameters' };
    } else if (modelName.includes('deepseek')) {
        modelInfo = { name: 'DeepSeek R1 7B', type: 'Deep Reasoning', speed: 'Medium', size: '7B parameters' };
    }
    
    modelDetails.innerHTML = `
        <h5>${modelInfo.name}</h5>
        <p><strong>Type:</strong> ${modelInfo.type}</p>
        <p><strong>Speed:</strong> ${modelInfo.speed} | <strong>Size:</strong> ${modelInfo.size}</p>
    `;
    
    currentModelSpan.textContent = modelInfo.name;
}

// Set model
async function setModel(modelName) {
    if (!modelName) return;
    
    const modelSelect = document.getElementById('modelSelect');
    const modelDetails = document.getElementById('modelDetails');
    
    // Show loading state
    modelSelect.disabled = true;
    modelDetails.innerHTML = `
        <div class="model-info-box loading">
            <i class="fas fa-spinner fa-spin"></i>
            <div>
                <h5>🔄 Switching Model...</h5>
                <p>Testing model readiness...</p>
            </div>
        </div>
    `;
    
    showNotification('🔄 Switching model...', 'info');
    
    try {
        const response = await fetch('/api/model/set', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ model: modelName })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateModelDetails(modelName);
            showNotification(`✅ Switched to ${modelName}`, 'success');
            console.log(`✅ Model switched to: ${modelName}`);
        } else {
            showNotification(`❌ Failed to switch model: ${data.error}`, 'error');
            console.error('Failed to switch model:', data.error);
            // Reload to restore previous state
            loadModels();
        }
        
    } catch (error) {
        console.error('Error setting model:', error);
        showNotification('❌ Error switching model', 'error');
        loadModels();
    } finally {
        modelSelect.disabled = false;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Model selector
    document.getElementById('modelSelect').addEventListener('change', (e) => {
        setModel(e.target.value);
    });
    
    document.getElementById('refreshModels').addEventListener('click', () => {
        loadModels();
        checkConnectionStatus();
    });
    // Upload button
    document.getElementById('uploadBtn').addEventListener('click', () => {
        openModal('uploadModal');
    });

    // Modal controls
    document.getElementById('closeModal').addEventListener('click', () => {
        closeModal('uploadModal');
    });
    document.getElementById('cancelUpload').addEventListener('click', () => {
        closeModal('uploadModal');
    });

    // Delete modal controls
    document.getElementById('closeDeleteModal').addEventListener('click', () => {
        closeModal('deleteModal');
    });
    document.getElementById('cancelDelete').addEventListener('click', () => {
        closeModal('deleteModal');
    });
    document.getElementById('confirmDelete').addEventListener('click', deleteDocument);

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });

    // File upload
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-color)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border-color)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        const file = e.dataTransfer.files[0];
        if (file) handleFileSelection(file);
    });
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFileSelection(file);
    });

    document.getElementById('clearFile').addEventListener('click', clearFileSelection);
    document.getElementById('submitUpload').addEventListener('click', submitUpload);

    // Query submission
    document.getElementById('queryBtn').addEventListener('click', submitQuery);
    document.getElementById('queryInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            submitQuery();
        }
    });

    // Example queries
    document.querySelectorAll('.btn-example').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const query = e.target.dataset.query;
            document.getElementById('queryInput').value = query;
            submitQuery();
        });
    });
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
    
    // Reset upload form
    if (modalId === 'uploadModal') {
        clearFileSelection();
        document.getElementById('textInput').value = '';
        document.getElementById('textFileName').value = '';
    }
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

// File handling
function handleFileSelection(file) {
    selectedFile = file;
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('fileInfo').style.display = 'flex';
    document.getElementById('fileName').textContent = file.name;
}

function clearFileSelection() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('fileInfo').style.display = 'none';
}

// Upload document
async function submitUpload() {
    const activeTab = document.querySelector('.tab-content.active').id;
    
    try {
        let formData = new FormData();
        
        if (activeTab === 'fileTab') {
            if (!selectedFile) {
                showNotification('Please select a file', 'error');
                return;
            }
            formData.append('file', selectedFile);
        } else {
            const text = document.getElementById('textInput').value.trim();
            const filename = document.getElementById('textFileName').value.trim();
            
            if (!text || !filename) {
                showNotification('Please provide both filename and text', 'error');
                return;
            }
            
            formData.append('text', text);
            formData.append('filename', filename);
        }

        const response = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showNotification(`Document uploaded: ${result.chunks} chunks created`, 'success');
            closeModal('uploadModal');
            loadDocuments();
            loadStats();
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Failed to upload document', 'error');
    }
}

// Load documents
async function loadDocuments() {
    try {
        const response = await fetch('/api/documents');
        const data = await response.json();

        if (data.success) {
            currentDocuments = data.documents;
            renderDocuments(data.documents);
        }
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

// Render documents
function renderDocuments(documents) {
    const container = document.getElementById('documentList');

    if (documents.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open"></i>
                <p>No documents uploaded yet</p>
                <p class="help-text">Upload a text document to get started</p>
            </div>
        `;
        return;
    }

    container.innerHTML = documents.map(doc => `
        <div class="document-item">
            <div class="document-header">
                <div class="document-name">
                    <i class="fas fa-file-alt"></i>
                    ${escapeHtml(doc.filename)}
                </div>
                <div class="document-actions">
                    <button class="btn-icon" onclick="openDeleteModal('${doc.id}', '${escapeHtml(doc.filename)}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="document-meta">
                <div class="meta-item">
                    <i class="fas fa-layer-group"></i>
                    ${doc.chunk_count} chunks
                </div>
                <div class="meta-item">
                    <i class="fas fa-font"></i>
                    ${doc.word_count.toLocaleString()} words
                </div>
                <div class="meta-item">
                    <i class="fas fa-clock"></i>
                    ${formatDate(doc.uploaded_at)}
                </div>
            </div>
        </div>
    `).join('');
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success) {
            currentStats = data.stats;
            renderStats(data.stats);
            updateModelInfo(data.stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Render stats
function renderStats(stats) {
    document.getElementById('docCount').textContent = stats.total_documents;
    document.getElementById('chunkCount').textContent = stats.total_chunks;
    document.getElementById('wordCount').textContent = stats.total_words.toLocaleString();
}

// Update model info
function updateModelInfo(stats) {
    const modelElement = document.getElementById('currentModel');
    const embeddingElement = document.getElementById('embeddingModel');
    
    if (stats.foundry_connected && stats.current_model) {
        modelElement.textContent = stats.current_model;
        updateStatus('connected', 'Foundry Connected');
    } else {
        modelElement.textContent = 'No model loaded';
        updateStatus('disconnected', 'Embeddings Only');
    }
    
    embeddingElement.textContent = stats.embedding_model;
}

// Update status indicator
function updateStatus(status, text) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    indicator.className = `status-indicator ${status}`;
    statusText.textContent = text;
}

// Submit query
async function submitQuery() {
    const query = document.getElementById('queryInput').value.trim();
    const mode = document.querySelector('input[name="searchMode"]:checked').value;

    if (!query) {
        showNotification('Please enter a question', 'error');
        return;
    }

    if (currentDocuments.length === 0) {
        showNotification('Please upload documents first', 'error');
        return;
    }

    // Show loading state
    showLoadingState();

    const startTime = Date.now();

    try {
        if (mode === 'rag') {
            await performRAGQuery(query, startTime);
        } else {
            await performSemanticSearch(query, startTime);
        }
    } catch (error) {
        console.error('Query error:', error);
        showErrorState(error.message);
    }
}

// Perform RAG query
async function performRAGQuery(query, startTime) {
    const response = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, max_chunks: 3 })
    });

    const result = await response.json();
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);

    if (result.success) {
        displayRAGResults(result, elapsedTime);
    } else {
        showErrorState(result.error || 'Query failed');
    }
}

// Perform semantic search
async function performSemanticSearch(query, startTime) {
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 })
    });

    const result = await response.json();
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);

    if (result.success) {
        displaySearchResults(result, elapsedTime);
    } else {
        showErrorState(result.error || 'Search failed');
    }
}

// Display RAG results
function displayRAGResults(result, elapsedTime) {
    hideAllResults();
    
    const answerContainer = document.getElementById('answerContainer');
    const answerContent = document.getElementById('answerContent');
    const sourcesSection = document.getElementById('sourcesSection');
    const sourcesList = document.getElementById('sourcesList');
    const responseTime = document.getElementById('responseTime');

    answerContent.textContent = result.answer;
    responseTime.textContent = `${elapsedTime}s`;

    // Display sources
    if (result.sources && result.sources.length > 0) {
        sourcesList.innerHTML = result.sources.map((source, idx) => `
            <div class="source-item">
                <div class="source-header">
                    <span class="source-filename">
                        [${idx + 1}] ${escapeHtml(source.filename)}
                    </span>
                    <span class="source-similarity">
                        ${(source.similarity * 100).toFixed(1)}% match
                    </span>
                </div>
            </div>
        `).join('');
        sourcesSection.style.display = 'block';
    } else {
        sourcesSection.style.display = 'none';
    }

    answerContainer.style.display = 'block';
}

// Display search results
function displaySearchResults(result, elapsedTime) {
    hideAllResults();
    
    const searchResults = document.getElementById('searchResults');
    const responseTime = document.getElementById('responseTime');

    responseTime.textContent = `${elapsedTime}s`;

    if (result.results.length === 0) {
        searchResults.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <p>No results found</p>
                <p class="help-text">Try a different search query</p>
            </div>
        `;
    } else {
        searchResults.innerHTML = result.results.map((item, idx) => `
            <div class="search-result-item">
                <div class="result-header">
                    <span class="result-filename">
                        ${escapeHtml(item.filename)}
                    </span>
                    <span class="result-similarity">
                        ${(item.similarity * 100).toFixed(1)}% match
                    </span>
                </div>
                <div class="result-content">
                    ${escapeHtml(item.chunk_text)}
                </div>
            </div>
        `).join('');
    }

    searchResults.style.display = 'flex';
}

// Show loading state
function showLoadingState() {
    hideAllResults();
    document.getElementById('resultsLoading').style.display = 'flex';
}

// Show error state
function showErrorState(message) {
    hideAllResults();
    const errorSection = document.getElementById('resultsError');
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'flex';
}

// Hide all result sections
function hideAllResults() {
    document.getElementById('resultsEmpty').style.display = 'none';
    document.getElementById('resultsLoading').style.display = 'none';
    document.getElementById('resultsError').style.display = 'none';
    document.getElementById('answerContainer').style.display = 'none';
    document.getElementById('searchResults').style.display = 'none';
}

// Open delete modal
function openDeleteModal(docId, filename) {
    deleteDocId = docId;
    document.getElementById('deleteDocumentName').textContent = filename;
    openModal('deleteModal');
}

// Delete document
async function deleteDocument() {
    if (!deleteDocId) return;

    try {
        const response = await fetch(`/api/documents/${deleteDocId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Document deleted successfully', 'success');
            closeModal('deleteModal');
            loadDocuments();
            loadStats();
            deleteDocId = null;
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showNotification('Failed to delete document', 'error');
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    
    return date.toLocaleDateString();
}

function showNotification(message, type = 'info') {
    // Simple notification - could be enhanced with a toast library
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}

// Auto-refresh stats periodically
setInterval(() => {
    loadStats();
}, 30000); // Every 30 seconds
