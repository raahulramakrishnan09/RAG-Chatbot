import json
import datetime
import uuid
import time
import gc
from pathlib import Path
from typing import List, Dict, Optional

from config.settings import settings

class SessionManager:
    def __init__(self):
        self.sessions_dir = settings.SESSIONS_DIR
    
    def create_title_from_prompt(self, prompt: str) -> str:
        """Create a session title from user prompt"""
        title = prompt.strip().rstrip('.?!')
        if 'about' in title.lower():
            title = title.lower().split('about')[-1]
        title = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in title)
        title = ' '.join(title.split()).title()
        return title[:30].strip()

    def _get_user_sessions_dir(self, username: str) -> Path:
        """Get user-specific sessions directory"""
        user_dir = self.sessions_dir / username
        user_dir.mkdir(exist_ok=True)
        return user_dir
         
    def create_session(self, name: Optional[str] = None, title: Optional[str] = None, username: Optional[str] = None) -> str:
        """Create a new session"""
        if not username:
            raise ValueError("Username is required to create a session")
            
        if not name:
            name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
        user_sessions_dir = self._get_user_sessions_dir(username)
        session_path = user_sessions_dir / f"{name}.json"
        
        if not session_path.exists():
            with open(session_path, "w") as f:
                metadata = {
                    "messages": [],
                    "created_at": datetime.datetime.now().isoformat(),
                    "title": title or name,
                    "username": username
                }
                json.dump(metadata, f)
        return name
    
    def get_sessions(self, username: str) -> List[Dict]:
        """Get all sessions for a user"""
        sessions = []
        user_sessions_dir = self._get_user_sessions_dir(username)
        
        for f in user_sessions_dir.glob("*.json"):
            if f.name.startswith("deleted_"):
                continue
                
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if data.get("username") == username:
                        sessions.append({
                            "id": f.stem,
                            "title": data.get("title", f.stem),
                            "created_at": data.get("created_at"),
                            "updated_at": data.get("updated_at", data.get("created_at")),
                            "message_count": len(data.get("messages", []))
                        })
            except (json.JSONDecodeError, PermissionError, FileNotFoundError, UnicodeDecodeError):
                continue
        
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def get_session_messages(self, session_name: str, username: str) -> List[Dict]:
        """Get messages for a specific session"""
        user_sessions_dir = self._get_user_sessions_dir(username)
        session_path = user_sessions_dir / f"{session_name}.json"
        
        if session_path.exists():
            try:
                with open(session_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("username") != username:
                        return []
                    return data.get("messages", [])
            except (json.JSONDecodeError, PermissionError, FileNotFoundError):
                return []
        return []
        
    def save_session_messages(self, session_name: str, messages: List[Dict], username: str, title: Optional[str] = None):
        """Save messages to a session"""
        user_sessions_dir = self._get_user_sessions_dir(username)
        session_path = user_sessions_dir / f"{session_name}.json"
        
        try:
            if session_path.exists():
                with open(session_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("username") != username:
                        return
            else:
                data = {
                    "created_at": datetime.datetime.now().isoformat(),
                    "username": username
                }
                
            data.update(
                messages=messages, # type: ignore
                updated_at=datetime.datetime.now().isoformat(),
            )
            if title:
                data["title"] = title
            
            temp_path = session_path.with_suffix('.tmp')
            with open(temp_path, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            if session_path.exists():
                session_path.unlink()
            temp_path.rename(session_path)
            
        except Exception as e:
            temp_path = session_path.with_suffix('.tmp')
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            raise e
            
    def delete_session(self, session_name: str, username: str) -> bool:
        """Delete a session"""
        user_sessions_dir = self._get_user_sessions_dir(username)
        session_path = user_sessions_dir / f"{session_name}.json"
        
        if session_path.exists():
            try:
                # Verify ownership
                try:
                    with open(session_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("username") != username:
                            return False
                except (json.JSONDecodeError, PermissionError):
                    return False
                
                # Try to delete with retries
                max_retries = 10
                for attempt in range(max_retries):
                    try:
                        session_path.unlink()
                        return True
                    except PermissionError:
                        if attempt < max_retries - 1:
                            time.sleep(0.2)
                            gc.collect()
                            continue
                        else:
                            # Last resort: rename to deleted
                            try:
                                deleted_name = f"deleted_{uuid.uuid4().hex[:8]}_{session_name}.json"
                                deleted_path = user_sessions_dir / deleted_name
                                session_path.rename(deleted_path)
                                try:
                                    deleted_path.unlink()
                                except PermissionError:
                                    pass
                                return True
                            except Exception:
                                raise PermissionError("Cannot delete session file - it may be in use")
                                
            except Exception as e:
                raise Exception(f"Could not delete session: {str(e)}")
        return False