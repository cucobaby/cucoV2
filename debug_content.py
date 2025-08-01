"""
Debug tool to inspect what content is actually stored in the knowledge base
"""
import requests
import json

def test_content_search():
    """Test what content is actually searchable"""
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔍 Testing content search and retrieval...")
    print("=" * 50)
    
    # Test 1: Check health and document count
    print("1. Checking health status...")
    health_response = requests.get(f"{base_url}/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"   Status: {health_data['status']}")
        print(f"   ChromaDB: {health_data['services']['chromadb']}")
    else:
        print(f"   Error: {health_response.status_code}")
        return
    
    # Test 2: Try very broad questions to see what the AI can access
    test_questions = [
        "What topics are covered in the uploaded documents?",
        "What information is available?",
        "Summarize the content you have access to",
        "List the main topics in the documents",
        "What can you tell me about the uploaded content?"
    ]
    
    print("\n2. Testing broad content questions...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n   Question {i}: {question}")
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Answer: {data['answer'][:200]}...")
                print(f"   Sources found: {len(data['sources'])}")
                if data['sources']:
                    for j, source in enumerate(data['sources'][:2]):
                        print(f"      Source {j+1}: {source.get('title', 'Unknown title')}")
            else:
                print(f"   Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   Exception: {str(e)}")
        
        if i == 2:  # Just test first 2 to avoid overwhelming
            break
    
    print(f"\n{'=' * 50}")
    print("Debug complete!")

if __name__ == "__main__":
    test_content_search()
