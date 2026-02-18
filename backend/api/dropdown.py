from flask import Blueprint, jsonify                                                        # type: ignore
from flask_login import login_required, current_user                                        # type: ignore

from config.settings import UserRole, ConfidentialityLevel
from backend.models.user import UserManager

# Create a new blueprint for dropdown/utility endpoints
dropdown_bp = Blueprint('dropdown', __name__, url_prefix='/api/dropdown')
user_manager = UserManager()

@dropdown_bp.route('/roles', methods=['GET'])
def get_available_roles():
    """Get all available user roles for dropdown"""
    try:
        roles = [{'value': role.value, 'label': role.value} for role in UserRole]
        return jsonify({
            'roles': roles,
            'default': 'Select'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@dropdown_bp.route('/confidentiality-levels', methods=['GET'])
def get_confidentiality_levels():
    """Get all confidentiality levels for dropdown"""
    try:
        levels = [{'value': level.value, 'label': level.value} for level in ConfidentialityLevel]
        return jsonify({
            'levels': levels,
            'default': 'Select'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@dropdown_bp.route('/user-allowed-confidentiality', methods=['GET'])
@login_required
def get_user_allowed_confidentiality():
    """Get confidentiality levels allowed for current user"""
    try:
        # Debug: Check if user is properly authenticated
        if not current_user or not hasattr(current_user, 'role'):
            return jsonify({'error': 'User session invalid. Please login again.'}), 401
        
        # Handle both enum and string role values
        if hasattr(current_user.role, 'value'):
            user_role = current_user.role
        else:
            # If role is stored as string, convert to enum
            try:
                user_role = UserRole(current_user.role)
            except ValueError:
                return jsonify({'error': 'Invalid user role. Please contact administrator.'}), 400
        
        allowed_levels = user_manager.get_allowed_confidentiality_levels(user_role)
        
        # Convert to dropdown format with additional info
        levels_info = []
        for level in ConfidentialityLevel:
            is_allowed = level.value in allowed_levels
            levels_info.append({
                'value': level.value,
                'label': level.value,
                'allowed': is_allowed,
                'disabled': not is_allowed
            })
        
        # Also provide just the allowed ones for easier use
        allowed_only = [
            {'value': level, 'label': level} 
            for level in allowed_levels
        ]
        
        return jsonify({
            'all_levels': levels_info,
            'allowed_levels': allowed_only,
            'user_role': user_role.value,
            'default': 'Select'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@dropdown_bp.route('/role-permissions', methods=['GET'])
def get_role_permissions():
    """Get detailed role permissions information"""
    try:
        role_permissions = {}
        
        for role in UserRole:
            allowed_levels = user_manager.get_allowed_confidentiality_levels(role)
            role_permissions[role.value] = {
                'role': role.value,
                'allowed_confidentiality_levels': allowed_levels,
                'can_upload': len(allowed_levels) > 0,
                'permissions': {
                    'low': 'Low' in allowed_levels,
                    'medium': 'Medium' in allowed_levels,
                    'high': 'High' in allowed_levels
                }
            }
        
        return jsonify({
            'role_permissions': role_permissions,
            'confidentiality_hierarchy': ['Low', 'Medium', 'High']
        }), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500