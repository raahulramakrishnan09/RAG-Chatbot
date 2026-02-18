from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from pathlib import Path

from config.settings import settings, ConfidentialityLevel

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload a document"""
    try:
        # Import here to avoid circular imports
        from ai.chatbot import ChatbotService
        chatbot_service = ChatbotService()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        confidentiality = request.form.get('confidentiality')
        
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not confidentiality:
            return jsonify({'error': 'Confidentiality level is required'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        try:
            conf_level = ConfidentialityLevel(confidentiality)
        except ValueError:
            return jsonify({'error': f'Invalid confidentiality level. Must be one of: {[level.value for level in ConfidentialityLevel]}'}), 400
        
        filename = secure_filename(file.filename)
        file_path = settings.DOCUMENTS_DIR / filename
        
        file.save(str(file_path))
        
        success, msg = chatbot_service.upload_document(
            str(file_path),
            current_user.username,
            conf_level
        )
        
        if success:
            return jsonify({'message': msg, 'filename': filename}), 201
        else:
            return jsonify({'error': msg}), 400
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500