# 📚 RAG Document Search Demo

An intelligent document search and question-answering system powered by Retrieval-Augmented Generation (RAG) and Windows AI Foundry Local. Upload documents, ask questions, and get AI-generated answers with source citations.

**Port**: http://localhost:5005

## ⚡ Quick Start

### Prerequisites

**Windows AI Foundry Local MUST be running** for full RAG functionality:

```bash
# Start Foundry service
foundry service start

# Verify it's running (should show http://127.0.0.1:XXXXX)
foundry service status
```

The app will automatically detect the Foundry port and connect to it.

### Automated Setup (Recommended)

From the main workspace directory:
```bash
./start_all_demos.sh
```

The script will automatically:
- Check if Foundry Local service is running
- Create virtual environment and install dependencies
- Launch the demo on http://localhost:5005

### Manual Setup

1. **Ensure Foundry Local is running** (see Prerequisites above)

2. **Navigate to demo folder**
   ```bash
   cd edge-ai-rag-document-search
   ```

3. **Create and activate virtual environment** (if not already created)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

4. **Install dependencies** (if not already installed)
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the demo**
   ```bash
   # Windows
   venv\Scripts\python.exe rag_document_app.py
   
   # Linux/macOS
   venv/bin/python rag_document_app.py
   ```

6. **Access the demo**
   Open http://localhost:5005 in your browser

## 🎮 Usage

### Uploading Documents

1. Click "Upload Document" button
2. Choose to upload a file or paste text directly
3. Documents are automatically processed and embeddings generated
4. View your documents in the left panel

### Semantic Search

1. Enter your query in the search box
2. Click "Semantic Search" to find relevant document chunks
3. Results show similarity scores and matching text

### RAG Question Answering

1. Enter your question in the search box
2. Click "RAG Answer" to get AI-generated responses
3. Answers include source citations showing which documents were used
4. Response time is shown for performance monitoring

**Note**: Semantic search works even without Foundry. RAG answers require Windows AI Foundry Local to be running.

## 🚀 Features

### Core Capabilities

- **📄 Document Upload**: Upload text documents (.txt, .md, .log, .json, .csv) or paste text directly
- **🔍 Semantic Search**: Find relevant information using natural language queries
- **🤖 RAG Question Answering**: Get AI-generated answers based on your documents
- **📊 Source Citations**: See which documents were used to generate answers
- **🧩 Intelligent Chunking**: Automatically split documents into overlapping chunks for better context
- **💾 Persistent Storage**: Documents and embeddings saved to disk for future sessions
- **⚡ Real-time Processing**: Immediate embedding generation and search capabilities

### Technical Highlights

- **Embedding Model**: Uses `all-MiniLM-L6-v2` for high-quality semantic embeddings
- **Vector Search**: Cosine similarity-based search across all document chunks
- **Context Building**: Automatically selects the most relevant chunks for answering questions
- **Windows AI Foundry Integration**: Leverages local AI models for answer generation
- **Graceful Degradation**: Works with embeddings-only mode if Foundry isn't available

## 🎯 How It Works

### The RAG Pipeline

1. **Document Ingestion**
   - Upload documents through the web interface
   - Text is automatically split into overlapping chunks (500 chars with 50 char overlap)
   - Each chunk is converted to a vector embedding using the sentence transformer model

2. **Semantic Search**
   - User asks a question in natural language
   - Question is converted to a vector embedding
   - Cosine similarity is calculated between the question and all document chunks
   - Top 3-5 most relevant chunks are retrieved

3. **Answer Generation**
   - Retrieved chunks are combined into context
   - Context and question are sent to Windows AI Foundry Local
   - AI model generates a comprehensive answer based only on the provided context
   - Answer is returned with source citations

### Document Chunking Strategy

Documents are split into overlapping chunks to preserve context:
- **Chunk Size**: 500 characters per chunk
- **Overlap**: 50 characters between chunks
- **Sentence Boundaries**: Splits occur at sentence boundaries when possible
- **Overlap Strategy**: Last 2 sentences of previous chunk overlap with next chunk

This ensures that important information isn't lost at chunk boundaries and provides better context for retrieval.

## 💡 Usage Guide

### Uploading Documents

**Option 1: File Upload**
1. Click the "Upload" button
2. Select "Upload File" tab
3. Drag and drop a file or click to browse
4. Click "Upload & Process"

**Option 2: Paste Text**
1. Click the "Upload" button
2. Select "Paste Text" tab
3. Enter a filename (e.g., "my-notes.txt")
4. Paste your text content
5. Click "Upload & Process"

**Supported Formats**: .txt, .md, .log, .json, .csv (Max 16MB)

### Asking Questions

**RAG Mode (Recommended)**
- Select "RAG Answer" radio button
- Type your question (e.g., "What are the main topics discussed?")
- Press "Submit" or Ctrl+Enter
- Get an AI-generated answer with source citations

**Semantic Search Mode**
- Select "Semantic Search" radio button
- Type your query
- Press "Submit"
- View matching document chunks ranked by relevance

### Example Questions

- "What are the main topics in these documents?"
- "Summarize the key points"
- "What are the most important facts mentioned?"
- "Who are the key people or entities discussed?"
- "What recommendations are provided?"

### Managing Documents

- **View Documents**: See all uploaded documents in the left panel
- **Document Info**: View chunk count, word count, and upload date
- **Delete Documents**: Click the trash icon to remove a document
- **Statistics**: Monitor total documents, chunks, and words at the top

## 🛠️ Technical Architecture

### Backend Components

**Flask Application**
- RESTful API for document management and queries
- WebSocket support via Flask-SocketIO
- Async request handling with ThreadPoolExecutor

**RAG Manager**
- Document storage and retrieval
- Embedding generation and caching
- Vector similarity search
- Context building and answer generation

**Embedding System**
- Uses Sentence Transformers library
- Model: `all-MiniLM-L6-v2` (lightweight, fast, high-quality)
- Generates 384-dimensional embeddings
- Cached on disk for persistence

**Storage**
- Documents metadata: JSON file
- Embeddings: Compressed NumPy arrays (.npz)
- Location: `documents/` directory

### Frontend Components

**Modern Web Interface**
- Responsive design (mobile-friendly)
- Real-time updates
- Drag-and-drop file upload
- Modal dialogs for user interactions

**Interactive Features**
- Live statistics dashboard
- Document list with metadata
- Query input with mode selection
- Results display with source citations

## 📊 API Endpoints

### Document Management

```
GET  /api/documents           - List all documents
POST /api/documents/upload    - Upload a new document
DELETE /api/documents/{id}    - Delete a document
```

### Search & Query

```
POST /api/search             - Semantic search
POST /api/rag/query          - RAG question answering
GET  /api/stats              - System statistics
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the demo directory:

```bash
# Logging
ENABLE_DEBUG_LOGGING=false
ENABLE_FLASK_DEBUG=false

# Server
PORT=5005

# Security
SECRET_KEY=your-secret-key-here
```

### Model Configuration

**Embedding Model**
- Default: `all-MiniLM-L6-v2`
- Change in code: Modify `SentenceTransformer()` initialization
- Other options: `all-mpnet-base-v2`, `multi-qa-mpnet-base-cos-v1`

**Chunking Parameters**
- Chunk size: 500 characters (configurable in `chunk_text()` method)
- Overlap: 50 characters (configurable)
- Adjust based on your document types and average paragraph length

## 🔒 Privacy & Security

- **Local Processing**: All embeddings generated locally, no data sent to cloud
- **On-Device AI**: Answer generation uses local Windows AI Foundry models
- **Persistent Storage**: Documents stored locally in `documents/` directory
- **File Size Limits**: 16MB maximum per file upload
- **Input Validation**: File type checking and content sanitization

## 🧪 Performance Optimization

### Tips for Better Results

1. **Document Quality**: Upload well-structured documents with clear paragraphs
2. **Question Clarity**: Ask specific questions for better retrieval
3. **Context Size**: Adjust `max_context_chunks` for more/less context
4. **Model Selection**: Use faster models (Phi, Qwen) for quicker responses
5. **Batch Upload**: Upload related documents together for better context

### Performance Metrics

- **Embedding Generation**: ~50-100 chunks/second
- **Semantic Search**: <100ms for 1000 chunks
- **Answer Generation**: 2-10 seconds (depends on model and context size)
- **Storage Overhead**: ~4KB per chunk (embedding + metadata)

## 🐛 Troubleshooting

### Common Issues

**"Running in embeddings only mode" / No RAG Answers**
- **Cause**: Windows AI Foundry Local is not running
- **Solution**: 
  ```bash
  foundry service start
  foundry service status  # Should show http://127.0.0.1:XXXXX
  ```
- The app will automatically detect and connect to Foundry when it's running
- Restart the RAG demo after starting Foundry

**"No relevant documents found" / "No results found"**
- **Cause**: Either no documents uploaded or search threshold too strict
- **Solution**:
  1. Ensure you have uploaded documents (check left panel)
  2. Try rephrasing your query with different keywords
  3. Check the document content is relevant to your query
  4. The similarity threshold is now set to 0.1 (10%) for better recall

**Timeout Errors on RAG Queries**
- **Cause**: LLM taking longer than expected to generate response
- **Solution**: 
  - Timeout is set to 180 seconds (3 minutes)
  - Consider using faster models like `qwen2.5-0.5b` or `phi-3.5-mini`
  - Reduce context chunks (query with fewer documents)
  - Check Foundry service is running smoothly: `foundry service status`

**Slow First Startup**
- **Cause**: Downloading embedding model and loading libraries
- **Expected**: First startup takes 30-60 seconds
- **Solution**: Wait patiently - subsequent startups are much faster

**Module Import Errors**
- **Cause**: Dependencies not installed in virtual environment
- **Solution**:
  ```bash
  cd edge-ai-rag-document-search
  venv/Scripts/python.exe -m pip install -r requirements.txt
  ```

**Memory Issues**
- Large documents (>1MB) may take longer to process
- Reduce chunk size if running on low-memory systems
- Limit number of uploaded documents to <100 for optimal performance

## 📖 Use Cases

### Business Applications

- **Knowledge Base Search**: Search company documentation and policies
- **Customer Support**: Find relevant information from support documents
- **Research**: Query research papers and technical documentation
- **Legal**: Search through contracts and legal documents
- **Education**: Create Q&A systems for course materials

### Personal Use

- **Note Organization**: Search through personal notes and journals
- **Book Summaries**: Upload book chapters and ask questions
- **Meeting Notes**: Search across multiple meeting transcripts
- **Recipe Collection**: Find recipes by ingredients or cuisine
- **Travel Planning**: Search travel guides and itineraries

## 🔄 Future Enhancements

Potential features for future versions:

- [ ] PDF document support with text extraction
- [ ] Multi-language document support
- [ ] Document tagging and categorization
- [ ] Advanced filtering (by date, source, tag)
- [ ] Export search results and answers
- [ ] Chat history and saved queries
- [ ] Collaborative features (shared document libraries)
- [ ] Custom embedding model selection
- [ ] GPU acceleration for embeddings
- [ ] REST API authentication

## 📚 Learn More

### RAG Resources

- [Retrieval-Augmented Generation Paper](https://arxiv.org/abs/2005.11401)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Windows AI Foundry Documentation](https://learn.microsoft.com/en-us/windows/ai/)

### Related Technologies

- **Sentence Transformers**: Pre-trained models for semantic embeddings
- **FAISS**: Vector similarity search (alternative to NumPy)
- **LangChain**: Framework for LLM applications with RAG
- **ChromaDB**: Vector database for embeddings storage

## 🤝 Contributing

This demo is part of the AI on the Edge collection. Contributions are welcome!

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Update documentation for new features

## 📝 License

This demo is part of the AI on the Edge project. See the main repository LICENSE file for details.

## 🙏 Acknowledgments

- **Windows AI Foundry**: Local AI model serving
- **Sentence Transformers**: Semantic embedding generation
- **Flask**: Web framework
- **NumPy**: Efficient vector operations

---

**Need Help?** Check the main repository README or open an issue on GitHub.

**Want More?** Explore the other 5 demos in the AI on the Edge collection!
