import datetime
from typing import Dict, List, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

from config.settings import settings
from .document_manager import DocumentManager
from .chains.qa_chain import create_qa_chain

class ChatbotService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Initialize components
        self.document_manager = DocumentManager()
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            convert_system_message_to_human=True
        )
    
    def process_message(self, message: str, chat_history: List[Tuple[str, str]], username: str) -> Tuple[str, List]:
        """Process a user message and return bot response"""
        try:
            # Get retriever with user access control
            retriever = self.document_manager.get_retriever(username=username)
            
            # Create QA chain
            qa_chain = create_qa_chain(self.llm, retriever)
            
            # Process the message
            result = qa_chain({
                "question": message,
                "chat_history": chat_history
            })
            
            # Post-process answer
            answer = result['answer'].strip()
            
            # Check for common "not found" patterns and standardize
            not_found_phrases = [
                "cannot find", "don't have information", "not mentioned", 
                "cannot answer", "no information", "not available"
            ]
            
            if any(phrase in answer.lower() for phrase in not_found_phrases) and "couldn't find relevant information" not in answer:
                answer = f'I couldn\'t find relevant information for "{message}". Feel free to rephrase or try a different topic.'
            
            return answer, result.get('source_documents', [])
            
        except Exception as e:
            return f'I couldn\'t find relevant information for "{message}". Feel free to rephrase or try a different topic.', []
    
    def upload_document(self, pdf_path: str, username: str, confidentiality_level) -> Tuple[bool, str]:
        """Upload a document through the document manager"""
        return self.document_manager.add_document(pdf_path, username, confidentiality_level)