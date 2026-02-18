#  RAG-Chatbot

A powerful, enterprise-ready chatbot API that enables intelligent conversations about uploaded documents. Built with Flask, LangChain, Groq LLM, and ChromaDB for scalable, production-grade deployments.

##  Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
  
##  Features

### Core Capabilities
-  **Document Processing**: Upload and process PDF documents with intelligent chunking
-  **Context-Aware Chat**: Ask questions about your documents with conversational context
-  **Role-Based Access Control**: Admin, Manager, and Employee roles with granular permissions
-  **Document Confidentiality**: Three-tier security (Low, Medium, High) for sensitive documents
-  **Session Management**: Multiple chat sessions per user with persistent history

### Advanced Features
-  **Fast Inference**: Powered by Groq's LLaMA-3.3-70B model for ultra-fast responses
-  **Semantic Search**: HuggingFace embeddings with ChromaDB vector database
-  **JWT Authentication**: Secure token-based authentication with encryption
-  **CORS Support**: Configure allowed origins for web applications
-  **Intelligent Retrieval**: Context-aware document retrieval for accurate answers

---

##  Technology Stack

### Backend Framework
- **Flask 3.0+**: Web application framework
- **Flask-CORS**: Cross-origin resource sharing
- **PyJWT**: JSON Web Token authentication
- **Cryptography**: Token encryption and security

### AI & NLP
- **Groq API**: LLaMA-3.3-70B for fast LLM inference
- **LangChain 0.2+**: AI application framework with Runnable patterns
- **HuggingFace**: Sentence transformers for embeddings
- **ChromaDB**: Vector database for semantic search

### Document Processing
- **PyPDF2/pypdf**: PDF text extraction
- **NLTK**: Natural language processing
- **sentence-transformers**: Text embeddings

### Performance & Optimization
- **torch**: Deep learning framework
- **accelerate**: Model optimization
- **psutil**: System monitoring
- **diskcache**: Caching layer

---

##  System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 5GB minimum (8GB recommended)
- **Disk Space**: 5GB for models and dependencies
- **OS**: Linux, macOS, or Windows
- **Internet**: Required for Groq API and model downloads

### API Keys Required
- **Groq API Key**: Sign up at [console.groq.com](https://console.groq.com/keys)

---

##  Installation

### Clone the Repository
```bash
git clone https://github.com/raahulramakrishnan09/RAG-Chatbot.git
cd chatbot-api
```

##  Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# === REQUIRED: API Keys ===
GROQ_API_KEY=your_groq_api_key_here

# === APPLICATION SETTINGS ===
ENVIRONMENT=development  # development, testing, or production
SECRET_KEY=your_secret_key_here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
HOST=0.0.0.0
PORT=8000

# === AI MODEL CONFIGURATION ===
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_TEMPERATURE=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVER_K=4

# === SECURITY SETTINGS ===
JWT_EXPIRATION_HOURS=24
JWT_ALGORITHM=HS256
MAX_CONTENT_LENGTH=16777216  # 16MB

# === CORS SETTINGS ===
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Confidentiality Levels & Role Permissions

| Role | Low | Medium | High |
|------|-----|--------|------|
| **Employee** | ✅ | ❌ | ❌ |
| **Manager** | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ |

##  Project Structure

```
Project/
├── config/
│   ├── __init__.py
│   └── settings.py                 # Centralized configuration
├── backend/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── documents.py            # Document management
│   │   ├── sessions.py             # Session management
│   │   ├── chat.py                 # Chat endpoints
│   │   └── dropdown.py             # Dropdown/utility endpoints
│   └── models/
│       ├── __init__.py
│       ├── user.py                 # User model and management
│       └── session.py              # Session model
├── ai/
│   ├── __init__.py
│   ├── chatbot.py                  # Main chatbot service
│   ├── document_manager.py         # Document processing
│   └── chains/
│       ├── __init__.py
│       └── qa_chain.py             # QA chain with LangChain 1.0
├── data/
│   ├── document_metadata.json      # Document metadata
│   └── users.json                  # User profile & User's chat sessions
├── documents/                      # PDF storage
├── chroma_db/                      # Vector database
├── app.py                          # Main Flask application
├── client.py                       # Testing files
├── debug_chatbot.py                # Testing files
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

###  Version History

**v1.0.0**: Initial release
  - Core chatbot functionality
  - Role-based access control
  - Document confidentiality
  - Session management

---
