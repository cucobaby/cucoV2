"""
Test script to check API functionality and knowledge base content
"""
import os
import sys
import requests
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

API_BASE_URL = "https://cucov2-production.up.railway.app"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API Health Check:")
            print(f"   Status: {health_data.get('status')}")
            print(f"   ChromaDB: {health_data.get('services', {}).get('chromadb', 'Unknown')}")
            print(f"   OpenAI: {health_data.get('services', {}).get('openai', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_knowledge_base_content():
    """Check what's currently in the knowledge base"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
            doc_count = collection.count()
            print(f"\n📊 Knowledge Base Status:")
            print(f"   Documents: {doc_count}")
            
            if doc_count > 0:
                # Get a sample of documents to see what's in there
                results = collection.get(limit=5, include=['documents', 'metadatas'])
                print(f"\n📄 Sample Content (first 5 docs):")
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    print(f"   Doc {i+1}:")
                    print(f"     Title: {metadata.get('title', 'No title')}")
                    print(f"     Source: {metadata.get('source', 'Unknown')}")
                    print(f"     Content preview: {doc[:100]}...")
                    print()
            
            return doc_count
        except Exception as e:
            if "does not exist" in str(e).lower():
                print(f"📊 Knowledge Base Status: Empty (collection doesn't exist)")
                return 0
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Knowledge base check error: {str(e)}")
        return None

def clear_railway_knowledge_base():
    """Clear the knowledge base on Railway"""
    try:
        print(f"\n🧹 Clearing Railway Knowledge Base...")
        response = requests.delete(f"{API_BASE_URL}/clear-knowledge-base")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Knowledge base cleared')}")
            return True
        else:
            print(f"❌ Clear failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Clear error: {str(e)}")
        return False

def test_question_endpoint():
    """Test asking a question"""
    try:
        test_question = "What is oxidative phosphorylation?"
        print(f"\n🤔 Testing Question: '{test_question}'")
        
        response = requests.post(f"{API_BASE_URL}/ask-question", 
            json={"question": test_question},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Question Response:")
            print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"   Confidence: {result.get('confidence', 'Unknown')}")
            print(f"   Sources found: {len(result.get('sources', []))}")
            return result
        else:
            print(f"❌ Question failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Question test error: {str(e)}")
        return None

def analyze_api_issues():
    """Analyze potential API issues"""
    print("\n🔍 API Analysis:")
    
    # Check health
    health_ok = test_health_endpoint()
    
    # Clear Railway knowledge base first
    railway_cleared = clear_railway_knowledge_base()
    
    # Check knowledge base after clearing
    doc_count = test_knowledge_base_content()
    
    # Test question (should show no relevant content now)
    question_result = test_question_endpoint()
    
    print(f"\n📋 Summary:")
    print(f"   API Health: {'✅ OK' if health_ok else '❌ Issues'}")
    print(f"   Railway KB Cleared: {'✅ Success' if railway_cleared else '❌ Failed'}")
    print(f"   Local Knowledge Base: {doc_count if doc_count is not None else '❌ Error'} documents")
    print(f"   Question Response: {'✅ Working' if question_result else '❌ Issues'}")
    
    # Analysis
    print(f"\n🎯 Current Status:")
    if railway_cleared and doc_count == 0:
        print("   ✅ Knowledge base successfully cleared on both local and Railway")
        print("   ✅ Ready for fresh content upload with updated Chrome extension")
    elif question_result:
        answer = question_result.get('answer', '')
        if 'mitochondria are the powerhouse' in answer.lower():
            print("   ❌ AI still returning generic content - knowledge base not fully cleared")
        if 'no relevant information' in answer.lower() or 'don\'t have information' in answer.lower():
            print("   ✅ AI correctly reporting no relevant content found")
        if 'cell biology chapter' in answer.lower():
            print("   ❌ Still finding old generic textbook material")

if __name__ == "__main__":
    print("🔧 Testing Canvas AI Assistant API Functionality...")
    analyze_api_issues()
