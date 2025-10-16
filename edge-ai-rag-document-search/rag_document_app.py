"""
RAG Document Search Demo - Windows AI Foundry Local
Demonstrates Retrieval-Augmented Generation with document search and semantic search capabilities
"""

import os
import json
import logging
import subprocess
import requests
import time
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sentence_transformers import SentenceTransformer
import threading

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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'rag-document-demo-secret')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Document storage directory
DOCUMENTS_DIR = Path(__file__).parent / 'documents'
DOCUMENTS_DIR.mkdir(exist_ok=True)

class RAGDocumentManager:
    """Manages documents, embeddings, and RAG queries using Windows AI Foundry Local"""
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}  # Document metadata and chunks
        self.embeddings: Dict[str, np.ndarray] = {}  # Document chunk embeddings
        self.embedding_model = None
        self.foundry_endpoint = None
        self.base_url = None
        self.available_models = []
        self.current_model = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = threading.Lock()
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        # Initialize Windows AI Foundry connection
        self._initialize_foundry_connection()
        
        # Load existing documents
        self._load_existing_documents()
        
    def _initialize_embedding_model(self):
        """Initialize sentence transformer for embeddings"""
        try:
            # Use a lightweight, fast embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise Exception("Failed to load embedding model")
            
    def _initialize_foundry_connection(self):
        """Initialize connection to Windows AI Foundry service"""
        try:
            # First, try to get the actual port from foundry service
            try:
                result = subprocess.run(['foundry', 'service', 'status'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Extract port from status output (e.g., "http://127.0.0.1:60102")
                    import re
                    port_match = re.search(r'http://127\.0\.0\.1:(\d+)', result.stdout)
                    if port_match:
                        port = port_match.group(1)
                        endpoint = f'http://127.0.0.1:{port}'
                        try:
                            response = requests.get(f"{endpoint}/v1/models", timeout=5)
                            if response.status_code == 200:
                                self.foundry_endpoint = endpoint
                                self.base_url = endpoint
                                logger.info(f"✅ Connected to Windows AI Foundry at {endpoint}")
                                self._load_available_models()
                                return
                        except requests.exceptions.RequestException:
                            pass
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Fallback: Check common AI service endpoints
            endpoints = [
                ('http://localhost:60632', '/v1/models'),
                ('http://localhost:60102', '/v1/models'),
                ('http://localhost:52009', '/v1/models'),
                ('http://localhost:3928', '/v1/models'),
                ('http://localhost:1234', '/v1/models'),
                ('http://localhost:11434', '/api/tags'),
                ('http://localhost:8080', '/health')
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
                result = subprocess.run(['foundry', 'service', 'status'], 
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
            logger.info("📋 Running in limited mode - embeddings only")
            
        except Exception as e:
            logger.error(f"Error initializing Windows AI Foundry: {e}")
            logger.info("📋 Continuing in limited mode")
            
    def _load_available_models(self):
        """Load available models from Windows AI Foundry"""
        try:
            if self.base_url:
                response = requests.get(f"{self.base_url}/v1/models", timeout=10)
                if response.status_code == 200:
                    models_data = response.json()
                    self.available_models = [model['id'] for model in models_data.get('data', [])]
                    if self.available_models:
                        # Prefer fast models for RAG
                        fast_models = [m for m in self.available_models if 'qwen2.5-0.5b' in m or 'phi' in m.lower()]
                        self.current_model = fast_models[0] if fast_models else self.available_models[0]
                        logger.info(f"📋 Loaded {len(self.available_models)} models")
                        logger.info(f"🎯 Using model: {self.current_model}")
                        return
                        
            logger.warning("⚠️  No models loaded from Foundry")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            
    def _load_existing_documents(self):
        """Load documents that were previously uploaded"""
        try:
            # Load document metadata from JSON file
            metadata_file = DOCUMENTS_DIR / 'documents_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"📄 Loaded {len(self.documents)} existing documents")
                
            # Load embeddings from numpy file
            embeddings_file = DOCUMENTS_DIR / 'embeddings.npz'
            if embeddings_file.exists():
                data = np.load(embeddings_file, allow_pickle=True)
                self.embeddings = {key: data[key] for key in data.files}
                logger.info(f"🔢 Loaded {len(self.embeddings)} embedding sets")
                
        except Exception as e:
            logger.error(f"Error loading existing documents: {e}")
            
    def _save_documents_metadata(self):
        """Save document metadata to disk"""
        try:
            metadata_file = DOCUMENTS_DIR / 'documents_metadata.json'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving documents metadata: {e}")
            
    def _save_embeddings(self):
        """Save embeddings to disk"""
        try:
            embeddings_file = DOCUMENTS_DIR / 'embeddings.npz'
            np.savez_compressed(embeddings_file, **self.embeddings)
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
            
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) >= 2 else ''
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
                
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def add_document(self, filename: str, content: str) -> Dict:
        """Add a document to the RAG system"""
        try:
            with self.lock:
                # Generate document ID
                doc_id = hashlib.md5(f"{filename}{datetime.now().isoformat()}".encode()).hexdigest()
                
                # Chunk the document
                chunks = self.chunk_text(content)
                
                # Generate embeddings for chunks
                logger.info(f"Generating embeddings for {len(chunks)} chunks...")
                chunk_embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
                
                # Store document metadata
                self.documents[doc_id] = {
                    'id': doc_id,
                    'filename': filename,
                    'content': content,
                    'chunks': chunks,
                    'chunk_count': len(chunks),
                    'uploaded_at': datetime.now().isoformat(),
                    'char_count': len(content),
                    'word_count': len(content.split())
                }
                
                # Store embeddings
                self.embeddings[doc_id] = chunk_embeddings
                
                # Save to disk
                self._save_documents_metadata()
                self._save_embeddings()
                
                logger.info(f"✅ Document '{filename}' added with {len(chunks)} chunks")
                
                return {
                    'success': True,
                    'doc_id': doc_id,
                    'filename': filename,
                    'chunks': len(chunks),
                    'message': f'Document processed into {len(chunks)} chunks'
                }
                
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_document(self, doc_id: str) -> Dict:
        """Delete a document from the RAG system"""
        try:
            with self.lock:
                if doc_id not in self.documents:
                    return {'success': False, 'error': 'Document not found'}
                
                filename = self.documents[doc_id]['filename']
                
                # Remove from memory
                del self.documents[doc_id]
                if doc_id in self.embeddings:
                    del self.embeddings[doc_id]
                
                # Save updated data
                self._save_documents_metadata()
                self._save_embeddings()
                
                logger.info(f"✅ Document '{filename}' deleted")
                
                return {
                    'success': True,
                    'message': f'Document "{filename}" deleted'
                }
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {'success': False, 'error': str(e)}
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Perform semantic search across all documents"""
        try:
            if not self.documents:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], show_progress_bar=False)[0]
            
            # Calculate cosine similarity with all chunks
            results = []
            
            for doc_id, doc_embeddings in self.embeddings.items():
                doc = self.documents.get(doc_id)
                if not doc:
                    continue
                
                # Calculate similarities
                similarities = np.dot(doc_embeddings, query_embedding) / (
                    np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
                )
                
                # Get top chunks for this document
                top_indices = np.argsort(similarities)[-3:][::-1]  # Top 3 chunks per document
                
                for idx in top_indices:
                    if similarities[idx] > 0.1:  # Lower threshold for better recall
                        results.append({
                            'doc_id': doc_id,
                            'filename': doc['filename'],
                            'chunk_index': int(idx),
                            'chunk_text': doc['chunks'][idx],
                            'similarity': float(similarities[idx])
                        })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def rag_query(self, query: str, max_context_chunks: int = 3) -> Dict:
        """Perform RAG query: retrieve relevant chunks and generate answer"""
        try:
            start_time = time.time()
            
            # Step 1: Semantic search to find relevant chunks
            relevant_chunks = self.semantic_search(query, top_k=max_context_chunks)
            
            if not relevant_chunks:
                return {
                    'success': False,
                    'error': 'No relevant documents found',
                    'query': query
                }
            
            # Step 2: Build context from relevant chunks
            context_parts = []
            sources = []
            
            for i, chunk in enumerate(relevant_chunks):
                context_parts.append(f"[Source {i+1} - {chunk['filename']}]\n{chunk['chunk_text']}")
                sources.append({
                    'filename': chunk['filename'],
                    'chunk_index': chunk['chunk_index'],
                    'similarity': chunk['similarity']
                })
            
            context = "\n\n".join(context_parts)
            
            # Step 3: Generate answer using Foundry Local
            if self.base_url and self.current_model:
                try:
                    system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
Use ONLY the information from the context to answer the question.
If the answer is not in the context, say "I don't have enough information to answer that."
Be concise and cite the source numbers when possible."""

                    user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

                    response = requests.post(
                        f"{self.base_url}/v1/chat/completions",
                        json={
                            'model': self.current_model,
                            'messages': [
                                {'role': 'system', 'content': system_prompt},
                                {'role': 'user', 'content': user_prompt}
                            ],
                            'temperature': 0.3,
                            'max_tokens': 500,
                            'stream': False
                        },
                        timeout=180  # Increased timeout for slower models
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result['choices'][0]['message']['content']
                    else:
                        answer = f"Error generating answer: Status {response.status_code}"
                        
                except Exception as e:
                    logger.error(f"Error generating answer: {e}")
                    answer = "Error: Could not generate answer with AI model"
            else:
                # Fallback: Return context without generation
                answer = f"AI model not available. Here are the relevant excerpts:\n\n{context}"
            
            response_time = time.time() - start_time
            
            return {
                'success': True,
                'query': query,
                'answer': answer,
                'sources': sources,
                'context_chunks': len(relevant_chunks),
                'response_time': round(response_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def get_documents_list(self) -> List[Dict]:
        """Get list of all documents"""
        return [
            {
                'id': doc_id,
                'filename': doc['filename'],
                'chunk_count': doc['chunk_count'],
                'word_count': doc['word_count'],
                'uploaded_at': doc['uploaded_at']
            }
            for doc_id, doc in self.documents.items()
        ]
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        total_chunks = sum(doc['chunk_count'] for doc in self.documents.values())
        total_words = sum(doc['word_count'] for doc in self.documents.values())
        
        return {
            'total_documents': len(self.documents),
            'total_chunks': total_chunks,
            'total_words': total_words,
            'embedding_model': 'all-MiniLM-L6-v2',
            'foundry_connected': self.base_url is not None,
            'current_model': self.current_model,
            'available_models': self.available_models
        }
    
    def set_model(self, model_name: str) -> Dict:
        """Set the current model for RAG queries"""
        try:
            if model_name not in self.available_models:
                return {
                    'success': False,
                    'error': 'Model not available'
                }
            
            # Test model availability
            if self.base_url:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        'model': model_name,
                        'messages': [{'role': 'user', 'content': 'test'}],
                        'max_tokens': 5,
                        'stream': False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.current_model = model_name
                    logger.info(f"✅ Switched to model: {model_name}")
                    return {
                        'success': True,
                        'model': model_name,
                        'message': f'Successfully switched to {model_name}'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Model test failed with status {response.status_code}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Foundry not connected'
                }
                
        except Exception as e:
            logger.error(f"Error setting model: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.available_models
    
    def check_connection_status(self) -> bool:
        """Check if Foundry is connected"""
        return self.base_url is not None

# Initialize the RAG manager
rag_manager = RAGDocumentManager()

# Routes
@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of documents"""
    try:
        documents = rag_manager.get_documents_list()
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload a new document"""
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                content = file.read().decode('utf-8', errors='ignore')
                result = rag_manager.add_document(file.filename, content)
                return jsonify(result)
        elif 'text' in request.form and 'filename' in request.form:
            content = request.form['text']
            filename = request.form['filename']
            result = rag_manager.add_document(filename, content)
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': 'No file or text provided'
            }), 400
            
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document"""
    try:
        result = rag_manager.delete_document(doc_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Perform semantic search"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        results = rag_manager.semantic_search(query, top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rag/query', methods=['POST'])
def rag_query():
    """Perform RAG query"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_chunks = data.get('max_chunks', 3)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        result = rag_manager.rag_query(query, max_chunks)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = rag_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    try:
        return jsonify({
            'success': True,
            'models': rag_manager.get_available_models(),
            'current_model': rag_manager.current_model,
            'foundry_connected': rag_manager.check_connection_status()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/model/set', methods=['POST'])
def set_model():
    """Set current AI model"""
    try:
        data = request.get_json()
        model_name = data.get('model')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'No model specified'
            }), 400
        
        result = rag_manager.set_model(model_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error setting model: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/connection/status', methods=['GET'])
def get_connection_status():
    """Check Windows AI Foundry connection status"""
    try:
        is_connected = rag_manager.check_connection_status()
        return jsonify({
            'success': True,
            'connected': is_connected,
            'service': 'Windows AI Foundry Local',
            'base_url': rag_manager.base_url if is_connected else None,
            'current_model': rag_manager.current_model
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    logger.info(f"🚀 Starting RAG Document Search Demo on port {port}")
    logger.info(f"📄 Documents directory: {DOCUMENTS_DIR}")
    logger.info(f"🔍 Visit http://localhost:{port} to access the demo")
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=port, debug=ENABLE_FLASK_DEBUG, allow_unsafe_werkzeug=True)
