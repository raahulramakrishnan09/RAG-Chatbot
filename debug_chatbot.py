#!/usr/bin/env python3
"""
Debug version of chatbot to troubleshoot response issues
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from ai.chatbot import ChatbotService
from backend.models.user import UserManager, UserRole

def debug_document_retrieval(username="test_user"):
    """Debug document retrieval"""
    print("🔍 Debug: Document Retrieval")
    print("-" * 40)
    
    try:
        chatbot = ChatbotService()
        retriever = chatbot.document_manager.get_retriever(username=username)
        
        # Test query
        test_query = "test document"
        docs = retriever.get_relevant_documents(test_query)
        
        print(f"Query: '{test_query}'")
        print(f"Retrieved {len(docs)} documents")
        
        for i, doc in enumerate(docs):
            print(f"\nDocument {i+1}:")
            print(f"  Content: {doc.page_content[:200]}...")
            print(f"  Metadata: {doc.metadata}")
            
        return len(docs) > 0
        
    except Exception as e:
        print(f"❌ Error in document retrieval: {str(e)}")
        return False

def debug_qa_chain(username="test_user", question="What is this document about?"):
    """Debug QA chain processing"""
    print(f"\n🤖 Debug: QA Chain Processing")
    print("-" * 40)
    
    try:
        chatbot = ChatbotService()
        
        # Test message processing
        print(f"Question: '{question}'")
        answer, docs = chatbot.process_message(question, [], username)
        
        print(f"Answer: {answer}")
        print(f"Source documents: {len(docs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in QA processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def debug_user_permissions(username="test_user"):
    """Debug user permissions and access"""
    print(f"\n👤 Debug: User Permissions")
    print("-" * 40)
    
    try:
        user_manager = UserManager()
        role = user_manager.get_user_role(username)
        
        if not role:
            print(f"❌ User '{username}' not found")
            return False
            
        print(f"User: {username}")
        print(f"Role: {role.value}")
        print(f"Allowed levels: {user_manager.get_allowed_confidentiality_levels(role)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking user permissions: {str(e)}")
        return False

def debug_vector_database():
    """Debug vector database status"""
    print(f"\n🗄️ Debug: Vector Database")
    print("-" * 40)
    
    try:
        chatbot = ChatbotService()
        db = chatbot.document_manager.db
        
        # Get collection info
        collection = db._collection
        count = collection.count()
        
        print(f"Documents in database: {count}")
        
        if count > 0:
            # Sample some documents
            sample = collection.peek(limit=3)
            print(f"Sample metadata: {sample.get('metadatas', [])}")
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Error checking vector database: {str(e)}")
        return False

def debug_configuration():
    """Debug configuration settings"""
    print(f"\n⚙️ Debug: Configuration")
    print("-" * 40)
    
    print(f"Environment: {settings.environment}")
    print(f"Google API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Missing'}")
    print(f"Data directory: {settings.DATA_DIR}")
    print(f"Documents directory: {settings.DOCUMENTS_DIR}")
    print(f"Chroma directory: {settings.CHROMA_DIR}")
    print(f"LLM Model: {settings.LLM_MODEL}")
    print(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    
    # Check if directories exist
    dirs_exist = all([
        settings.DATA_DIR.exists(),
        settings.DOCUMENTS_DIR.exists(),
        settings.CHROMA_DIR.exists()
    ])
    
    print(f"Directories exist: {'✅' if dirs_exist else '❌'}")
    
    return settings.GOOGLE_API_KEY is not None and dirs_exist

def main():
    """Run all debug tests"""
    print("🔧 CHATBOT DEBUG TOOL")
    print("=" * 50)
    
    # Test username (you might need to change this)
    test_username = "test_user"
    
    # Create test user if doesn't exist
    user_manager = UserManager()
    if not user_manager.get_user_role(test_username):
        print(f"Creating test user: {test_username}")
        user_manager.register_user(test_username, "test_password", UserRole.AI_TEAM)
    
    tests = [
        ("Configuration", debug_configuration),
        ("User Permissions", lambda: debug_user_permissions(test_username)),
        ("Vector Database", debug_vector_database),
        ("Document Retrieval", lambda: debug_document_retrieval(test_username)),
        ("QA Chain", lambda: debug_qa_chain(test_username, "What information is available?")),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 DEBUG SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n💡 SUGGESTIONS:")
        print("1. Make sure you have uploaded some documents")
        print("2. Check that GOOGLE_API_KEY is set correctly")
        print("3. Verify documents are being processed into the vector database")
        print("4. Try with a test user that has appropriate permissions")

if __name__ == "__main__":
    main()