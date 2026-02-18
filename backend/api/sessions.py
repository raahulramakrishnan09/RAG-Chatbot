import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.models.session import SessionManager

sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')
session_manager = SessionManager()

@sessions_bp.route('', methods=['GET'])
@login_required
def get_sessions():
    """Get user sessions"""
    try:
        sessions = session_manager.get_sessions(current_user.username)
        return jsonify({'sessions': sessions}), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@sessions_bp.route('/<session_id>', methods=['GET'])
@login_required
def get_session_messages(session_id):
    """Get messages for a specific session"""
    try:
        user_sessions = session_manager.get_sessions(current_user.username)
        if not any(s['id'] == session_id for s in user_sessions):
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        messages = session_manager.get_session_messages(session_id, current_user.username)
        return jsonify({'session_id': session_id, 'messages': messages}), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@sessions_bp.route('/<session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Delete a session"""
    try:
        success = session_manager.delete_session(session_id, current_user.username)
        
        if success:
            return jsonify({'message': 'Session deleted successfully'}), 200
        else:
            return jsonify({'error': 'Session not found or could not be deleted'}), 404
            
    except Exception as e:
        error_msg = str(e)
        if "process cannot access the file" in error_msg or "WinError 32" in error_msg:
            return jsonify({'error': 'Session is currently in use. Please try again in a moment.'}), 409
        else:
            return jsonify({'error': f'Error deleting session: {error_msg}'}), 500