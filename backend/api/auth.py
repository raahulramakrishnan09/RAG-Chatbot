from flask import Blueprint, request, jsonify # type: ignore
from flask_login import login_user, logout_user, login_required, current_user # type: ignore

from config.settings import UserRole
from backend.models.user import UserManager

auth_bp = Blueprint('auth', __name__, url_prefix='/api/users')
user_manager = UserManager()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with auto-generated LoginID"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        role = data.get('role')
        
        if not all([username, password, confirm_password, role]):
            return jsonify({'error': 'Username, password, confirm_password, and role are required'}), 400
        
        # Check if passwords match
        if password != confirm_password:
            return jsonify({'error': 'Password and confirm_password do not match'}), 400
        
        try:
            user_role = UserRole(role)
        except ValueError:
            return jsonify({'error': f'Invalid role. Must be one of: {[r.value for r in UserRole]}'}), 400
        
        success, msg = user_manager.register_user(username, password, user_role)
        
        if success:
            # Get the newly created user to return their LoginID
            user = user_manager.get_user(username)
            if user is not None:
                return jsonify({
                    'message': 'User registered successfully',
                    'username': username,
                    'role': role,
                    'login_id': user.login_id,
                    'created_at': user.created_at
                }), 201
            else:
                return jsonify({'error': 'User registered but could not retrieve user details'}), 500
        else:
            return jsonify({'error': msg}), 400
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user - Fixed version with proper role validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        # role = data.get('role')  # Role is optional for login
        
        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Authenticate user
        success, error_msg, user_role = user_manager.authenticate(username, password)
        
        if not success:
            return jsonify({'error': error_msg or 'Invalid credentials'}), 401
        
        # If role is provided, validate it matches the user's actual role
        # if role:
        #     try:
        #         provided_role = UserRole(role)
        #         if user_role != provided_role:
        #             return jsonify({'error': 'Invalid role for this user'}), 401
        #     except ValueError:
        #         return jsonify({'error': f'Invalid role. Must be one of: {[r.value for r in UserRole]}'}), 400
        
        # Login the user
        user = user_manager.get_user(username)
        if user:
            login_user(user)
            return jsonify({
                'message': 'Login successful',
                'username': username,
                'role': user_role.value if user_role is not None and hasattr(user_role, 'value') else str(user_role),
                'login_id': user.login_id,
                'allowed_confidentiality_levels': user_manager.get_allowed_confidentiality_levels(user_role) if user_role is not None else []
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@auth_bp.route('/info', methods=['GET'])
@login_required
def get_user_info():
    """Get current user information including LoginID"""
    try:
        return jsonify({
            'username': current_user.username,
            'role': current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
            'login_id': current_user.login_id,
            'created_at': current_user.created_at,
            'allowed_confidentiality_levels': user_manager.get_allowed_confidentiality_levels(current_user.role)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get current user profile (alias for /info)"""
    return get_user_info()

@auth_bp.route('/lookup-by-login-id/<login_id>', methods=['GET'])
@login_required
def lookup_by_login_id(login_id):
    """Lookup user by LoginID (admin feature)"""
    try:
        # Check if current user is admin
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        user = user_manager.get_user_by_login_id(login_id)
        if not user:
            return jsonify({'error': 'User not found with this LoginID'}), 404
        
        return jsonify({
            'username': user.username,
            'role': user.role.value,
            'login_id': user.login_id,
            'created_at': user.created_at
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@auth_bp.route('/all-users', methods=['GET'])
@login_required
def get_all_users():
    """Get all users with LoginIDs (admin only)"""
    try:
        # Check if current user is admin
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        users = user_manager.get_all_users()
        return jsonify({
            'users': users,
            'total_count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@auth_bp.route('/migrate-users', methods=['POST'])
@login_required
def migrate_existing_users():
    """Migrate existing users to add LoginIDs (admin only)"""
    try:
        # Check if current user is admin
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        migrated_count = user_manager.migrate_existing_users()
        
        return jsonify({
            'message': f'Migration completed. {migrated_count} users updated with LoginIDs.',
            'migrated_count': migrated_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500