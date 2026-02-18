import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.models.session import SessionManager

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
session_manager = SessionManager()

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a message to the chatbot"""
    try:
        # Import here to avoid circular imports
        from ai.chatbot import ChatbotService
        chatbot_service = ChatbotService()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        message = data.get('message')
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not session_id:
            # Create new session
            title = session_manager.create_title_from_prompt(message)
            session_name = f"{title}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session_id = session_manager.create_session(
                name=session_name,
                title=title,
                username=current_user.username
            )
        
        # Get messages and add new message
        messages = session_manager.get_session_messages(session_id, current_user.username)
        messages.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Convert messages to chat history format for the AI
        chat_history = []
        for i in range(0, len(messages)-1, 2):
            if i+1 < len(messages)-1:
                chat_history.append((messages[i]['content'], messages[i+1]['content']))
        
        # Get AI response
        answer, source_docs = chatbot_service.process_message(
            message, 
            chat_history, 
            current_user.username
        )
        
        # Add AI response to messages
        messages.append({
            'role': 'assistant',
            'content': answer,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Save updated messages
        session_manager.save_session_messages(
            session_id,
            messages,
            current_user.username
        )
        
        return jsonify({
            'message': 'Message sent successfully',
            'response': answer,
            'session_id': session_id,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500