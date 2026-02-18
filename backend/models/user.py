import hashlib
import json
import datetime
import uuid
import time
from typing import Optional, Tuple
from flask_login import UserMixin

from config.settings import settings, UserRole, ConfidentialityLevel

class User(UserMixin):
    def __init__(self, username: str, role: UserRole, login_id: str = None, created_at: str = None):
        self.id = username  # Flask-Login requires this
        self.username = username
        self.role = role
        self.login_id = login_id or self._generate_login_id()
        self.created_at = created_at or datetime.datetime.now().isoformat()
    
    def _generate_login_id(self) -> str:
        """Generate a unique LoginID for the user"""
        return str(uuid.uuid4())
    
    @property
    def safe_login_id(self):
        """Safely get login_id, generate if missing"""
        if not hasattr(self, 'login_id') or not self.login_id:
            self.login_id = self._generate_login_id()
        return self.login_id

class UserManager:
    def __init__(self):
        self.db_path = settings.USERS_DB
        self._init_db()

    def _init_db(self):
        """Initialize the user database if it doesn't exist"""
        if not self.db_path.exists():
            with open(self.db_path, "w") as f:
                json.dump({"users": {}}, f)

    def _hash_password(self, password: str) -> str:
        """Hash a password for storing"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _load_users(self) -> dict:
        """Load users from the database"""
        with open(self.db_path) as f:
            return json.load(f)

    def _save_users(self, users_data: dict):
        """Save users to the database"""
        with open(self.db_path, "w") as f:
            json.dump(users_data, f, indent=4)

    def _generate_unique_login_id(self, username: str, users_data: dict) -> str:
        """Generate a unique LoginID that doesn't already exist"""
        max_attempts = 10
        existing_ids = set()
        
        # Collect existing LoginIDs
        for user_data in users_data["users"].values():
            if user_data.get('login_id'):
                existing_ids.add(user_data['login_id'])
        
        for attempt in range(max_attempts):
            login_id = str(uuid.uuid4())
            if login_id not in existing_ids:
                return login_id
        
        # Fallback: timestamp-based ID if UUID fails
        timestamp = str(int(time.time() * 1000000))  # microseconds for uniqueness
        username_hash = hashlib.md5(username.encode()).hexdigest()[:8]
        return f"LID_{timestamp}_{username_hash}"

    def register_user(self, username: str, password: str, role: UserRole) -> Tuple[bool, str]:
        """Register a new user with auto-generated LoginID"""
        users_data = self._load_users()
        
        if username in users_data["users"]:
            return False, "Username already exists"

        # Generate unique LoginID
        login_id = self._generate_unique_login_id(username, users_data)
        created_at = datetime.datetime.now().isoformat()

        users_data["users"][username] = {
            "password": self._hash_password(password),
            "role": role.value,
            "login_id": login_id,
            "created_at": created_at
        }
        
        self._save_users(users_data)
        return True, f"User registered successfully with LoginID: {login_id}"

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[UserRole]]:
        """Authenticate a user"""
        if not username.strip():
            return False, "Username cannot be empty", None

        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "Invalid username or password", None

        user = users_data["users"][username]
        if user["password"] != self._hash_password(password):
            return False, "Invalid username or password", None

        return True, None, UserRole(user["role"])

    def get_user_role(self, username: str) -> Optional[UserRole]:
        """Get the role of a user"""
        users_data = self._load_users()
        if username in users_data["users"]:
            return UserRole(users_data["users"][username]["role"])
        return None

    def get_user(self, username: str) -> Optional[User]:
        """Get a User object with LoginID support"""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return None
        
        user_data = users_data["users"][username]
        role = UserRole(user_data["role"])
        
        # Handle missing login_id for existing users
        login_id = user_data.get('login_id')
        if not login_id:
            # Generate LoginID for existing user and save it
            login_id = self._generate_unique_login_id(username, users_data)
            user_data['login_id'] = login_id
            
            # Add created_at if missing
            if 'created_at' not in user_data:
                user_data['created_at'] = datetime.datetime.now().isoformat()
            
            # Save the updated user data
            try:
                self._save_users(users_data)
            except Exception as e:
                print(f"Warning: Could not save LoginID for user {username}: {e}")
        
        return User(
            username=username, 
            role=role,
            login_id=login_id,
            created_at=user_data.get('created_at', datetime.datetime.now().isoformat())
        )

    def get_user_by_login_id(self, login_id: str) -> Optional[User]:
        """Get user object by LoginID"""
        users_data = self._load_users()
        
        for username, user_data in users_data["users"].items():
            if user_data.get('login_id') == login_id:
                role = UserRole(user_data["role"])
                return User(
                    username=username, 
                    role=role,
                    login_id=login_id,
                    created_at=user_data.get('created_at', datetime.datetime.now().isoformat())
                )
        return None

    def get_all_users(self) -> list[dict]:
        """Get all users with their LoginIDs (admin function)"""
        users_data = self._load_users()
        users_list = []
        
        for username, user_data in users_data["users"].items():
            users_list.append({
                'username': username,
                'role': user_data.get('role'),
                'login_id': user_data.get('login_id'),
                'created_at': user_data.get('created_at'),
                'has_login_id': bool(user_data.get('login_id'))
            })
        
        return users_list

    def migrate_existing_users(self) -> int:
        """Migrate existing users to add LoginID if missing"""
        users_data = self._load_users()
        migrated_count = 0
        
        for username, user_data in users_data["users"].items():
            user_updated = False
            
            # Add LoginID if missing
            if 'login_id' not in user_data or not user_data['login_id']:
                login_id = self._generate_unique_login_id(username, users_data)
                user_data['login_id'] = login_id
                migrated_count += 1
                user_updated = True
            
            # Add created_at if missing
            if 'created_at' not in user_data:
                user_data['created_at'] = datetime.datetime.now().isoformat()
                user_updated = True
        
        if migrated_count > 0:
            self._save_users(users_data)
        
        return migrated_count

    @staticmethod
    def can_access_document(user_role: UserRole, doc_level: ConfidentialityLevel) -> bool:
        """Check if a user can access a document"""
        access_matrix = {
            UserRole.ADMIN: [ConfidentialityLevel.LOW, ConfidentialityLevel.MEDIUM, ConfidentialityLevel.HIGH],
            UserRole.AI_TEAM: [ConfidentialityLevel.LOW, ConfidentialityLevel.MEDIUM],
            UserRole.BACKEND_TEAM: [ConfidentialityLevel.LOW]
        }
        return doc_level in access_matrix[user_role]

    @staticmethod
    def can_upload_document(user_role: UserRole, doc_level: ConfidentialityLevel) -> bool:
        """Check if a user can upload a document"""
        if user_role == UserRole.ADMIN:
            return True
        elif user_role == UserRole.AI_TEAM:
            return doc_level in [ConfidentialityLevel.LOW, ConfidentialityLevel.MEDIUM]
        elif user_role == UserRole.BACKEND_TEAM:
            return doc_level == ConfidentialityLevel.LOW
        return False

    @staticmethod
    def get_allowed_confidentiality_levels(role: UserRole) -> list[str]:
        """Get allowed confidentiality levels based on user role"""
        if role == UserRole.ADMIN:
            return [level.value for level in ConfidentialityLevel]
        elif role == UserRole.AI_TEAM:
            return [ConfidentialityLevel.LOW.value, ConfidentialityLevel.MEDIUM.value]
        else:
            return [ConfidentialityLevel.LOW.value]