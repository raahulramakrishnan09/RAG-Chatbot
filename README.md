#  RAG-Chatbot

A powerful, enterprise-ready chatbot API that enables intelligent conversations about uploaded documents. Built with Flask, LangChain, Google LLM, and ChromaDB for scalable, production-grade deployments.

##  Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  
##  Features

### Core Capabilities
-  **Document Processing**: Upload and process PDF documents with intelligent chunking
-  **Context-Aware Chat**: Ask questions about your documents with conversational context
-  **Role-Based Access Control**: Admin, Manager, and Employee roles with granular permissions
-  **Document Confidentiality**: Three-tier security (Low, Medium, High) for sensitive documents
-  **Session Management**: Multiple chat sessions per user with persistent history

### Advanced Features
-  **Fast Inference**: Powered by Google's LLaMA-3.3-70B model for ultra-fast responses
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
- **Google API**: LLaMA-3.3-70B for fast LLM inference
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
- **Internet**: Required for Google API and model downloads

### API Keys Required
- **Google API Key**: Sign up at [aistudio.google.com](https://aistudio.google.com/app/api-keys)

---

##  Installation

### Clone the Repository
```bash
git clone https://github.com/raahulramakrishnan09/RAG-Chatbot.git
cd chatbot-api
```

##  Configuration

### Environment Variables

Create a `secrets.toml` file in the root directory with the following variables:

```env
# === REQUIRED: API Keys ===
GOOGLE_API_KEY = 'your-api-key-here'
# Optional: Enable admin panel for PDF uploads
ADMIN_MODE = "true"
# DEBUG = "true"  # Uncomment to enable debug mode
```

### Confidentiality Levels & Role Permissions

| Role | Low | Medium | High |
|------|-----|--------|------|
| **Employee** | ✅ | ❌ | ❌ |
| **Manager** | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ |

###  Version History

**v1.0.0**: Initial release
  - Core chatbot functionality
  - Role-based access control
  - Document confidentiality
  - Session management

---
