import os
from pathlib import Path
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class UserRole(str, Enum):
    ADMIN = "Admin"
    AI_TEAM = "AI Team"
    BACKEND_TEAM = "Backend Team"

class ConfidentialityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Settings:
    """Centralized configuration management"""
    
    def __init__(self):
        self.environment = Environment(os.getenv('ENVIRONMENT', Environment.DEVELOPMENT))
        self._load_config()
    
    def _load_config(self):
        """Load configuration based on environment"""
        # Base paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.DOCUMENTS_DIR = self.BASE_DIR / "documents"
        self.SESSIONS_DIR = self.BASE_DIR / "sessions"
        self.CHROMA_DIR = self.BASE_DIR / "chroma_db"
        
        # Ensure directories exist
        for dir_path in [self.DATA_DIR, self.DOCUMENTS_DIR, self.SESSIONS_DIR, self.CHROMA_DIR]:
            dir_path.mkdir(exist_ok=True)
        
        # API Configuration
        self.GOOGLE_API_KEY = self._get_api_key()
        
        # Flask Configuration
        self.SECRET_KEY = os.getenv('SECRET_KEY', '4936c2cb893552fe458ac3494735e7396718dbf12ba1a8314209065686bdc182')
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
        
        # Server Configuration
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 8000))
        self.DEBUG = self.environment == Environment.DEVELOPMENT
        
        # AI Configuration
        self.EMBEDDING_MODEL = "models/embedding-001"
        self.LLM_MODEL = "gemini-1.5-flash"
        self.LLM_TEMPERATURE = 0.7
        self.RETRIEVER_K = 4
        self.CHUNK_SIZE = 1000
        self.CHUNK_OVERLAP = 200
        
        # Database Configuration
        self.USERS_DB = self.DATA_DIR / "users.json"
        self.DOCUMENTS_DB = self.DATA_DIR / "document_metadata.json"
    
    def _get_api_key(self):
        """Get Google API key from various sources"""
        # Try environment variable first
        api_key = os.getenv('GOOGLE_API_KEY')
        
        # Try secrets file
        if not api_key:
            secrets_path = self.BASE_DIR / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                try:
                    import toml
                    secrets = toml.load(secrets_path)
                    api_key = secrets.get('GOOGLE_API_KEY')
                except ImportError:
                    pass
        
        return api_key
    
    def validate(self):
        """Validate critical configuration"""
        errors = []
        
        if not self.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY not found")
        
        if self.environment == Environment.PRODUCTION and self.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY must be changed in production")
        
        return errors

# Global settings instance
settings = Settings()