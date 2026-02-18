import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from flask import Flask, jsonify, request, make_response                                # type: ignore
from flask_login import LoginManager                                                    # type: ignore
from flask_cors import CORS                                                             # type: ignore      

from config.settings import settings
from backend.models.user import UserManager
from backend.api.auth import auth_bp
from backend.api.documents import documents_bp
from backend.api.sessions import sessions_bp
from backend.api.chat import chat_bp
from backend.api.dropdown import dropdown_bp

def create_app():
    """Application factory with CORS support"""
    app = Flask(__name__)
    
    # Configure Flask
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    
    # Configure CORS - Enable credentials support
    CORS(app, 
         origins=[
             "http://localhost:3000",    # React default
             "http://127.0.0.1:3000",   # React alternative  
             "http://localhost:8080",    # Vue/other frameworks
             "http://127.0.0.1:8080",   # Vue alternative
             "http://localhost:5173",    # Vite default
             "http://127.0.0.1:5173",   # Vite alternative
             "http://localhost:4200",    # Angular default
             "http://127.0.0.1:4200",   # Angular alternative
             "https://localhost:3000",   # HTTPS variants
             "https://127.0.0.1:3000",
             # Add your production domain here when deploying
             # "https://yourdomain.com"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=[
             "Content-Type", 
             "Authorization", 
             "X-Requested-With",
             "Accept",
             "Origin",
             "Access-Control-Request-Method",
             "Access-Control-Request-Headers"
         ],
         supports_credentials=True,  # Critical for session cookies
         expose_headers=['Content-Range', 'X-Content-Range'])
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Set login view # type: ignore
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    user_manager = UserManager()
    
    @login_manager.user_loader
    def load_user(username):
        return user_manager.get_user(username)
    
    # Additional CORS handling for edge cases
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        allowed_origins = [
            "http://localhost:3000", "http://127.0.0.1:3000",
            "http://localhost:8080", "http://127.0.0.1:8080", 
            "http://localhost:5173", "http://127.0.0.1:5173",
            "http://localhost:4200", "http://127.0.0.1:4200",
            "https://localhost:3000", "https://127.0.0.1:3000"
        ]
        
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '86400'  # Cache preflight for 24 hours
        
        return response
    
    # Handle preflight OPTIONS requests explicitly
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            origin = request.headers.get('Origin')
            allowed_origins = [
                "http://localhost:3000", "http://127.0.0.1:3000",
                "http://localhost:8080", "http://127.0.0.1:8080",
                "http://localhost:5173", "http://127.0.0.1:5173", 
                "http://localhost:4200", "http://127.0.0.1:4200",
                "https://localhost:3000", "https://127.0.0.1:3000"
            ]
            
            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '86400'
            
            return response
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(dropdown_bp)
    
    # Root endpoint - API documentation
    @app.route('/', methods=['GET', 'OPTIONS'])
    def root():
        """Root endpoint showing available API endpoints"""
        return jsonify({
            "message": "Chatbot API Server",
            "version": "1.0.0",
            "status": "running",
            "cors_enabled": True,
            "allowed_origins": [
                "http://localhost:3000", "http://localhost:8080", 
                "http://localhost:5173", "http://localhost:4200"
            ],
            "endpoints": [
                "GET /api/health",
                "POST /api/users/register",
                "POST /api/users/login", 
                "POST /api/users/logout",
                "GET /api/users/info",
                "GET /api/users/all-users (admin)",
                "GET /api/users/lookup-by-login-id/<login_id> (admin)",
                "POST /api/users/migrate-users (admin)",
                "POST /api/documents/upload",
                "GET /api/sessions",
                "GET /api/sessions/<id>",
                "DELETE /api/sessions/<id>",
                "POST /api/chat/send",
                "GET /api/dropdown/roles",
                "GET /api/dropdown/confidentiality-levels",
                "GET /api/dropdown/user-allowed-confidentiality",
                "GET /api/dropdown/role-permissions"
            ],
            "documentation": {
                "authentication": "Use POST /api/users/login to authenticate",
                "file_upload": "Upload PDF files via POST /api/documents/upload",
                "chat": "Send messages via POST /api/chat/send",
                "sessions": "Manage chat sessions via /api/sessions endpoints",
                "dropdowns": "Get dropdown options via /api/dropdown endpoints",
                "admin": "Admin-only endpoints for user management with LoginIDs",
                "cors": "CORS enabled for frontend integration with credentials support"
            }
        }), 200

    # Health check endpoint
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def health_check():
        """Health check endpoint"""
        validation_errors = settings.validate()
        if validation_errors:
            return jsonify({
                'status': 'error', 
                'message': 'Configuration errors',
                'errors': validation_errors,
                'cors_enabled': True
            }), 500
        return jsonify({
            'status': 'ok', 
            'message': 'API is running',
            'cors_enabled': True,
            'timestamp': '2025-08-19T14:30:22Z'
        }), 200
    
    # Error handlers with CORS
    @app.errorhandler(404)
    def not_found_error(error):
        response = jsonify({'error': 'Endpoint not found'})
        return response, 404

    @app.errorhandler(500)
    def internal_error(error):
        response = jsonify({'error': 'Internal server error'})
        return response, 500

    @app.errorhandler(401)
    def unauthorized_error(error):
        response = jsonify({'error': 'Unauthorized. Please login first.'})
        return response, 401
    
    return app

# Create app instance
app = create_app()

# Check for initialization errors
validation_errors = settings.validate()
init_error = validation_errors[0] if validation_errors else None

if __name__ == '__main__':
    if init_error:
        print(f"❌ Error initializing application: {init_error}")
        print("Please check your configuration")
        if "GOOGLE_API_KEY" in init_error:
            print("Example: export GOOGLE_API_KEY='your-api-key-here'")
    else:
        print("🚀 Starting Flask API application with CORS enabled...")
        print("📡 CORS allowed origins:")
        print("   - http://localhost:3000 (React)")
        print("   - http://localhost:8080 (Vue/Others)")  
        print("   - http://localhost:5173 (Vite)")
        print("   - http://localhost:4200 (Angular)")
        print("🍪 Session cookies and credentials supported")
        print(f"🌐 Server running on http://{settings.HOST}:{settings.PORT}")
        app.run(
            debug=settings.DEBUG,
            host=settings.HOST,
            port=settings.PORT
        )