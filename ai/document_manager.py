import json
import datetime
from typing import Optional, Tuple, Dict
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from config.settings import settings, ConfidentialityLevel
from backend.models.user import UserManager

class DocumentMetadataManager:
    def __init__(self):
        self.db_path = settings.DOCUMENTS_DB
        self._init_db()

    def _init_db(self):
        """Initialize the document metadata database"""
        if not self.db_path.exists():
            with open(self.db_path, "w") as f:
                json.dump({"documents": {}}, f)

    def _load_metadata(self) -> Dict:
        """Load document metadata"""
        with open(self.db_path) as f:
            return json.load(f)

    def _save_metadata(self, metadata: Dict):
        """Save document metadata"""
        with open(self.db_path, "w") as f:
            json.dump(metadata, f, indent=4)

    def add_document(self, doc_path: str, confidentiality_level: ConfidentialityLevel, uploaded_by: str) -> None:
        """Add document metadata"""
        metadata = self._load_metadata()
        
        metadata["documents"][doc_path] = {
            "confidentiality_level": confidentiality_level.value,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.datetime.now().isoformat(),
            "last_modified": datetime.datetime.now().isoformat()
        }
        
        self._save_metadata(metadata)

    def get_document_level(self, doc_path: str) -> Optional[ConfidentialityLevel]:
        """Get document confidentiality level"""
        metadata = self._load_metadata()
        if doc_path in metadata["documents"]:
            return ConfidentialityLevel(metadata["documents"][doc_path]["confidentiality_level"])
        return None

class DocumentManager:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        self.user_manager = UserManager()
        self.doc_metadata = DocumentMetadataManager()
        
        from pydantic import SecretStr

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=SecretStr(settings.GOOGLE_API_KEY)
        )
        
        self.db = Chroma(
            persist_directory=str(settings.CHROMA_DIR),
            embedding_function=self.embeddings
        )
        
    def get_retriever(self, k: Optional[int] = None, username: Optional[str] = None):
        """Get a retriever with access control"""
        if k is None:
            k = settings.RETRIEVER_K
        
        search_kwargs = {
            "k": k,
            "score_threshold": 0.3,  # Lower threshold for better recall
            "fetch_k": 30,  # Fetch more documents for better results
        }
        
        if username:
            user_role = self.user_manager.get_user_role(username)
            if user_role:
                # Determine allowed levels
                allowed_levels = set([ConfidentialityLevel.LOW.value])
                
                if user_role.value in ["AI Team", "Admin"]:
                    allowed_levels.add(ConfidentialityLevel.MEDIUM.value)
                
                if user_role.value == "Admin":
                    allowed_levels.add(ConfidentialityLevel.HIGH.value)
                
                search_kwargs["filter"] = {
                    "confidentiality_level": {"$in": list(allowed_levels)}
                }
        
        return self.db.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs
        )
        
    def add_document(self, pdf_path: str, username: str, confidentiality_level: ConfidentialityLevel) -> Tuple[bool, str]:
        """Add a document to the system"""
        try:
            # Check permissions
            user_role = self.user_manager.get_user_role(username)
            if not user_role:
                return False, "User not found"
                
            if not self.user_manager.can_upload_document(user_role, confidentiality_level):
                return False, f"User does not have permission to upload {confidentiality_level.value} confidentiality documents"

            # Load and process document
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            texts = text_splitter.split_documents(pages)
            
            # Add metadata
            current_time = datetime.datetime.now().isoformat()
            for text in texts:
                text.metadata.update({
                    'creationdate': current_time,
                    'moddate': current_time,
                    'confidentiality_level': confidentiality_level.value,
                    'uploaded_by': username,
                    'document_id': str(hash(pdf_path)),
                    'searchable': True
                })
            
            # Store in vector database
            self.db.add_documents(texts)
            self.db.persist()
            
            # Store metadata
            self.doc_metadata.add_document(pdf_path, confidentiality_level, username)
            
            return True, f"Successfully added {pdf_path}"
            
        except Exception as e:
            return False, f"Error adding document: {str(e)}"