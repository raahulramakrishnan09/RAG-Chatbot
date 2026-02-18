import requests
import json
import sys
import os
from pathlib import Path
import getpass
import time

class ChatbotAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_user = None
        # Enable cookies for session management
        self.session.cookies.clear()
    
    def _handle_response(self, response):
        """Handle response and safely extract JSON"""
        try:
            if response.status_code == 200:
                return True, response.json()
            else:
                # Try to get JSON error message
                try:
                    error_data = response.json()
                    return False, error_data
                except:
                    # If JSON parsing fails, create error response
                    return False, {
                        "error": f"HTTP {response.status_code}: {response.text[:100]}...",
                        "status_code": response.status_code,
                        "raw_response": response.text[:200] if response.text else "Empty response"
                    }
        except Exception as e:
            return False, {"error": f"Response handling error: {str(e)}"}
    
    def health_check(self):
        """Check if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            return False, {"error": "Cannot connect to the API. Make sure the server is running."}
        except Exception as e:
            return False, {"error": str(e)}
    
    def register_user(self, username, password, confirm_password, role):
        """Register a new user"""
        data = {
            "username": username,
            "password": password,
            "confirm_password": confirm_password,
            "role": role
        }
        try:
            response = self.session.post(f"{self.base_url}/api/users/register", json=data)
            success = response.status_code in [200, 201]
            if success:
                return True, response.json()
            else:
                return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Registration error: {str(e)}"}
    
    def login(self, username, password, role=None):
        """Login user - role is now optional"""
        data = {
            "username": username,
            "password": password
        }
        if role:
            data["role"] = role
        
        try:
            response = self.session.post(f"{self.base_url}/api/users/login", json=data)
            success = response.status_code == 200
            if success:
                try:
                    self.current_user = response.json()
                    return True, self.current_user
                except:
                    self.current_user = {"username": username}
                    return True, {"username": username, "message": "Login successful"}
            else:
                return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Login error: {str(e)}"}
    
    def logout(self):
        """Logout user"""
        try:
            response = self.session.post(f"{self.base_url}/api/users/logout")
            success = response.status_code == 200
            if success:
                self.current_user = None
                self.session.cookies.clear()
                return True, {"message": "Logged out successfully"}
            else:
                return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Logout error: {str(e)}"}
    
    def upload_document(self, file_path, confidentiality_level):
        """Upload a document"""
        if not os.path.exists(file_path):
            return False, {"error": "File not found"}
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'confidentiality': confidentiality_level}
                response = self.session.post(f"{self.base_url}/api/documents/upload", files=files, data=data)
            
            success = response.status_code in [200, 201]
            if success:
                return True, response.json()
            else:
                return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Upload error: {str(e)}"}
    
    def send_message(self, message, session_id=None):
        """Send a message to the chatbot"""
        data = {
            "message": message,
            "session_id": session_id
        }
        try:
            response = self.session.post(f"{self.base_url}/api/chat/send", json=data)
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Send message error: {str(e)}"}
    
    def get_sessions(self):
        """Get user sessions"""
        try:
            response = self.session.get(f"{self.base_url}/api/sessions")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get sessions error: {str(e)}"}
    
    def get_session_messages(self, session_id):
        """Get messages for a specific session"""
        try:
            response = self.session.get(f"{self.base_url}/api/sessions/{session_id}")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get session messages error: {str(e)}"}
    
    def delete_session(self, session_id):
        """Delete a session"""
        try:
            response = self.session.delete(f"{self.base_url}/api/sessions/{session_id}")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Delete session error: {str(e)}"}
    
    def get_user_info(self):
        """Get current user information"""
        try:
            response = self.session.get(f"{self.base_url}/api/users/info")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get user info error: {str(e)}"}
    
    def get_user_profile(self):
        """Get current user profile"""
        try:
            response = self.session.get(f"{self.base_url}/api/users/profile")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get user profile error: {str(e)}"}
    
    # Dropdown methods
    def get_available_roles(self):
        """Get available user roles for dropdown"""
        try:
            response = self.session.get(f"{self.base_url}/api/dropdown/roles")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get roles error: {str(e)}"}
    
    def get_confidentiality_levels(self):
        """Get all confidentiality levels for dropdown"""
        try:
            response = self.session.get(f"{self.base_url}/api/dropdown/confidentiality-levels")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get confidentiality levels error: {str(e)}"}
    
    def get_user_allowed_confidentiality(self):
        """Get confidentiality levels allowed for current user"""
        try:
            response = self.session.get(f"{self.base_url}/api/dropdown/user-allowed-confidentiality")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get user allowed confidentiality error: {str(e)}"}
    
    def get_role_permissions(self):
        """Get detailed role permissions information"""
        try:
            response = self.session.get(f"{self.base_url}/api/dropdown/role-permissions")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get role permissions error: {str(e)}"}
    
    # Admin methods
    def get_all_users(self):
        """Get all users with LoginIDs (admin only)"""
        try:
            response = self.session.get(f"{self.base_url}/api/users/all-users")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Get all users error: {str(e)}"}
    
    def lookup_by_login_id(self, login_id):
        """Lookup user by LoginID (admin only)"""
        try:
            response = self.session.get(f"{self.base_url}/api/users/lookup-by-login-id/{login_id}")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Lookup by login ID error: {str(e)}"}
    
    def migrate_users(self):
        """Migrate existing users to add LoginIDs (admin only)"""
        try:
            response = self.session.post(f"{self.base_url}/api/users/migrate-users")
            return self._handle_response(response)
        except Exception as e:
            return False, {"error": f"Migrate users error: {str(e)}"}

def print_response(success, data, operation="Operation"):
    """Helper function to print API responses"""
    if success:
        print(f"✅ {operation} successful!")
        if 'message' in data:
            print(f"   {data['message']}")
        if 'response' in data:
            print(f"   Response: {data['response']}")
        if 'username' in data and 'role' in data:
            print(f"   User: {data['username']} ({data['role']})")
            if 'login_id' in data:
                print(f"   LoginID: {data['login_id']}")
        if 'login_id' in data and 'username' not in data:
            print(f"   LoginID: {data['login_id']}")
        if 'created_at' in data:
            print(f"   Created: {data['created_at']}")
    else:
        print(f"❌ {operation} failed!")
        if 'error' in data:
            print(f"   Error: {data['error']}")
        if 'status_code' in data:
            print(f"   Status Code: {data['status_code']}")
        if 'raw_response' in data:
            print(f"   Raw Response: {data['raw_response']}")

def test_dropdown_endpoints():
    """Test all dropdown endpoints - the main focus"""
    client = ChatbotAPIClient()
    
    print("\n🔽 Testing Dropdown Endpoints")
    print("=" * 50)
    
    # Test public dropdown endpoints (no auth required)
    print("\n1. Testing Available Roles...")
    success, data = client.get_available_roles()
    if success:
        print("✅ Available roles:")
        for role in data.get('roles', []):
            print(f"   - {role['value']} (label: {role['label']})")
        print(f"   Default: {data.get('default')}")
    else:
        print_response(success, data, "Get roles")
    
    print("\n2. Testing Confidentiality Levels...")
    success, data = client.get_confidentiality_levels()
    if success:
        print("✅ Available confidentiality levels:")
        for level in data.get('levels', []):
            print(f"   - {level['value']} (label: {level['label']})")
        print(f"   Default: {data.get('default')}")
    else:
        print_response(success, data, "Get confidentiality levels")
    
    print("\n3. Testing Role Permissions...")
    success, data = client.get_role_permissions()
    if success:
        print("✅ Role permissions:")
        for role, perms in data.get('role_permissions', {}).items():
            print(f"   {role}:")
            print(f"     - Can upload: {perms['can_upload']}")
            print(f"     - Allowed levels: {perms['allowed_confidentiality_levels']}")
    else:
        print_response(success, data, "Get role permissions")
    
    # Now test the protected endpoint that was failing
    print("\n4. Testing User-Allowed Confidentiality (PROTECTED - requires login)...")
    
    # First try without login (should fail)
    print("\n   4a. Testing without login (should fail)...")
    success, data = client.get_user_allowed_confidentiality()
    if not success:
        print("✅ Correctly blocked unauthorized access")
        print(f"   Error: {data.get('error', 'Unknown error')}")
        if data.get('status_code'):
            print(f"   HTTP Status: {data.get('status_code')}")
    else:
        print("⚠️  Unexpected: Endpoint allowed access without login")
    
    # Now login and try again
    print("\n   4b. Testing with login...")
    
    # Try to login with common test users
    test_credentials = [
        ("testuser", "testpass123", "AI Team"),
        ("demo_user", "demo_password", "AI Team"),
        ("admin", "admin123", "Admin"),
        ("test", "test", "AI Team")
    ]
    
    login_successful = False
    for username, password, role in test_credentials:
        print(f"      - Trying to login as {username}...")
        success, login_data = client.login(username, password, role)
        if success:
            print(f"      ✅ Login successful as {username}")
            login_successful = True
            break
        else:
            print(f"      ❌ Login failed: {login_data.get('error', 'Unknown error')}")
            
            # Try to register the user if login failed
            print(f"      📝 Trying to register {username}...")
            reg_success, reg_data = client.register_user(username, password, password, role)
            if reg_success:
                print(f"      ✅ Registration successful for {username}")
                # Try login again
                success, login_data = client.login(username, password, role)
                if success:
                    print(f"      ✅ Login successful after registration")
                    login_successful = True
                    break
    
    if login_successful:
        # Now test the problematic endpoint
        print("      - Testing user-allowed confidentiality...")
        success, data = client.get_user_allowed_confidentiality()
        
        if success:
            print("🎉 SUCCESS! User-allowed confidentiality endpoint is working!")
            print(f"   User role: {data.get('user_role')}")
            print(f"   Allowed levels: {[level['value'] for level in data.get('allowed_levels', [])]}")
            print(f"   All levels info:")
            for level in data.get('all_levels', []):
                status = "✅" if level['allowed'] else "❌"
                print(f"     {status} {level['value']} (allowed: {level['allowed']})")
            
            print("\n🔧 AUTHENTICATION ISSUE IS FIXED! 🎉")
            
        else:
            print("❌ User-allowed confidentiality endpoint still failing!")
            print_response(success, data, "Get user-allowed confidentiality")
            
            # Additional debugging
            print(f"\n🔍 Debug Info:")
            print(f"   Session cookies: {dict(client.session.cookies)}")
            print(f"   Current user: {client.current_user}")
            
            # Try other protected endpoints to see if it's a general issue
            print(f"\n   Testing other protected endpoints for comparison...")
            
            info_success, info_data = client.get_user_info()
            print(f"   User info endpoint: {'✅' if info_success else '❌'}")
            if not info_success:
                print(f"   User info error: {info_data.get('error', 'Unknown')}")
            
            sessions_success, sessions_data = client.get_sessions()
            print(f"   Sessions endpoint: {'✅' if sessions_success else '❌'}")
            if not sessions_success:
                print(f"   Sessions error: {sessions_data.get('error', 'Unknown')}")
    else:
        print("❌ Could not login to test protected endpoint")
        print("   Tried multiple users but none worked")
        print("   You may need to register a user manually first")
    
    return True

def quick_auth_test():
    """Quick test focused on the authentication issue"""
    client = ChatbotAPIClient()
    
    print("⚡ Quick Authentication Test")
    print("=" * 40)
    
    # Health check
    success, data = client.health_check()
    if not success:
        print("❌ Server not running")
        print_response(success, data, "Health Check")
        return
    
    print("✅ Server is running")
    
    # Try to login with existing user or create one
    test_users = [
        ("testuser", "testpass123", "AI Team"),
        ("admin", "admin123", "Admin"),
        ("demo_user", "demo_password", "AI Team")
    ]
    
    logged_in = False
    for username, password, role in test_users:
        print(f"\n🔑 Trying to login as {username}...")
        success, data = client.login(username, password, role)
        if success:
            print(f"✅ Logged in as {username}")
            logged_in = True
            break
        else:
            print(f"❌ Failed: {data.get('error', 'Unknown error')}")
            # Try to register this user
            print(f"📝 Trying to register {username}...")
            reg_success, reg_data = client.register_user(username, password, password, role)
            if reg_success:
                print(f"✅ Registered {username}")
                success, data = client.login(username, password, role)
                if success:
                    print(f"✅ Logged in as {username} after registration")
                    logged_in = True
                    break
    
    if not logged_in:
        print("❌ Could not login or register any user")
        return
    
    # Test the problematic endpoint
    print(f"\n🎯 Testing the problematic endpoint...")
    success, data = client.get_user_allowed_confidentiality()
    
    if success:
        print("🎉 SUCCESS! The endpoint is working!")
        print(f"User role: {data.get('user_role')}")
        print(f"Allowed levels: {[l['value'] for l in data.get('allowed_levels', [])]}")
        print("\n✅ AUTHENTICATION ISSUE IS RESOLVED! ✅")
    else:
        print(f"❌ Still failing: {data.get('error', 'Unknown error')}")
        
        # Debug info
        print(f"\n🔍 Debug Info:")
        print(f"Session cookies: {dict(client.session.cookies)}")
        print(f"Current user: {client.current_user}")
        print(f"Status code: {data.get('status_code', 'Unknown')}")
        print(f"Raw response: {data.get('raw_response', 'None')}")
        
        # Try user info to see if session is valid
        info_success, info_data = client.get_user_info()
        print(f"User info test: {'✅' if info_success else '❌'}")
        if not info_success:
            print(f"User info error: {info_data.get('error', 'Unknown')}")

# ... [Include all the other functions from the previous version: 
# test_authentication_endpoints, test_all_endpoints, demo_workflow, 
# interactive_chat, register_user, upload_document, test_admin_features, 
# debug_session_state, and main function] ...

def test_authentication_endpoints():
    """Test all authentication-related endpoints"""
    client = ChatbotAPIClient()
    
    print("🔐 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Health check first
    print("\n1. Health Check...")
    success, data = client.health_check()
    print_response(success, data, "Health check")
    
    if not success:
        print("Server is not running. Please start the API server first.")
        return False
    
    # Test registration
    print("\n2. Testing User Registration...")
    test_username = f"testuser_{int(time.time())}"  # Unique username
    test_password = "testpass123"
    test_role = "AI Team"
    
    success, data = client.register_user(test_username, test_password, test_password, test_role)
    print_response(success, data, "User Registration")
    
    if not success:
        print("Registration failed - trying with existing user for login test")
        test_username = "existing_user"  # Fallback to existing user
    
    # Test login without role
    print("\n3. Testing Login (without role)...")
    success, data = client.login(test_username, test_password)
    print_response(success, data, "Login without role")
    login_success_no_role = success
    
    if success:
        # Test protected endpoints while logged in
        print("\n4. Testing User Info...")
        success, data = client.get_user_info()
        print_response(success, data, "Get User Info")
        
        print("\n5. Testing User Profile...")
        success, data = client.get_user_profile()
        print_response(success, data, "Get User Profile")
    
    # Logout
    print("\n6. Testing Logout...")
    success, data = client.logout()
    print_response(success, data, "Logout")
    
    # Test login with role
    print("\n7. Testing Login (with role)...")
    success, data = client.login(test_username, test_password, test_role)
    print_response(success, data, "Login with role")
    login_success_with_role = success
    
    return login_success_no_role or login_success_with_role

def demo_workflow():
    """Demo workflow showcasing the API"""
    client = ChatbotAPIClient()
    
    print("Chatbot API Demo Workflow")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check...")
    success, data = client.health_check()
    print_response(success, data, "Health check")
    
    if not success:
        print("Server is not running. Please start the API server first.")
        return
    
    # Test dropdown endpoints
    print("\n2. Testing dropdown endpoints...")
    
    print("\n   Available roles:")
    success, data = client.get_available_roles()
    if success:
        for role in data.get('roles', []):
            print(f"     - {role['value']}")
    
    print("\n   Available confidentiality levels:")
    success, data = client.get_confidentiality_levels()
    if success:
        for level in data.get('levels', []):
            print(f"     - {level['value']}")
    
    print("\n   Role permissions:")
    success, data = client.get_role_permissions()
    if success:
        for role, perms in data.get('role_permissions', {}).items():
            print(f"     {role}: {perms['allowed_confidentiality_levels']}")
    
    # Register user
    print("\n3. Registering demo user...")
    success, data = client.register_user("demo_user", "demo_password", "demo_password", "AI Team")
    print_response(success, data, "User registration")
    
    # Login
    print("\n4. Logging in...")
    success, data = client.login("demo_user", "demo_password", "AI Team")
    print_response(success, data, "Login")
    
    if not success:
        return
    
    # Get user info
    print("\n5. Getting user info...")
    success, data = client.get_user_info()
    print_response(success, data, "Get user info")
    
    # Get user-specific confidentiality levels
    print("\n6. Getting user allowed confidentiality levels...")
    success, data = client.get_user_allowed_confidentiality()
    if success:
        print(f"   User role: {data.get('user_role')}")
        print(f"   Allowed levels: {[level['value'] for level in data.get('allowed_levels', [])]}")
    else:
        print_response(success, data, "Get user allowed confidentiality")
    
    # Upload document (if sample PDF exists)
    print("\n7. Uploading document (if sample.pdf exists)...")
    if os.path.exists("sample.pdf"):
        success, data = client.upload_document("sample.pdf", "Low")
        print_response(success, data, "Document upload")
    else:
        print("   No sample.pdf found. Skipping document upload.")
    
    # Send messages
    print("\n8. Sending chat messages...")
    messages = [
        "Hello! Can you help me?",
        "What information do you have available?",
        "Tell me about the uploaded documents."
    ]
    
    session_id = None
    for i, message in enumerate(messages, 1):
        print(f"\n   Message {i}: {message}")
        success, data = client.send_message(message, session_id)
        if success:
            session_id = data.get('session_id')
            print(f"   Bot: {data.get('response', 'No response')}")
        else:
            print_response(success, data, f"Message {i}")
    
    # Get sessions
    print("\n9. Getting user sessions...")
    success, data = client.get_sessions()
    if success:
        sessions = data.get('sessions', [])
        print(f"   Found {len(sessions)} session(s)")
        for session in sessions[:3]:  # Show first 3
            print(f"   - {session['id']}: {session['title']} ({session['message_count']} messages)")
    else:
        print_response(success, data, "Get sessions")
    
    # Logout
    print("\n10. Logging out...")
    success, data = client.logout()
    print_response(success, data, "Logout")
    
    print("\nDemo completed!")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <command>")
        print("\nAvailable commands:")
        print("  demo           - Run basic workflow demo")
        print("  chat           - Start interactive chat")
        print("  register       - Register new user")
        print("  upload         - Document upload demo")
        print("  dropdowns      - Test dropdown endpoints")
        print("  admin          - Test admin LoginID features")
        print("  health         - Check API health")
        print("  test-auth      - Test authentication endpoints")
        print("  quick-auth     - Quick authentication test (focus on the bug)")
        return
    
    command = sys.argv[1].lower()
    
    if command == "demo":
        demo_workflow()
    elif command == "dropdowns":
        test_dropdown_endpoints()
    elif command == "quick-auth":
        quick_auth_test()
    elif command == "test-auth":
        test_authentication_endpoints()
    elif command == "health":
        client = ChatbotAPIClient()
        success, data = client.health_check()
        print_response(success, data, "Health check")
        if success:
            print("✅ API server is running and healthy!")
        else:
            print("❌ API server is not responding properly.")
    else:
        print(f"Unknown command: {command}")
        print("\nAvailable commands:")
        print("  demo           - Run basic workflow demo")
        print("  dropdowns      - Test dropdown endpoints")
        print("  quick-auth     - Quick authentication test (focus on the bug)")
        print("  test-auth      - Test authentication endpoints")
        print("  health         - Check API health")

if __name__ == "__main__":
    main()