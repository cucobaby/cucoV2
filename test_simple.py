#!/usr/bin/env python3
"""
Test ChromaDB access and search functionality
"""
import requests

def test_simple_search():
    """Test with a simple question that worked before"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    # Test with simple questions that used to work
    test_questions = [
        "what topics did I upload",
        "protein",
        "biology",
        "study guide"
    ]
    
    print("🧪 Testing Simple Search Functionality")
    print("=" * 50)
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": question},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n📋 Question: '{question}'")
                print(f"   ✅ Status: SUCCESS")
                print(f"   📊 Confidence: {result['confidence']}")
                print(f"   📚 Sources: {len(result['sources'])}")
                print(f"   📝 Answer Length: {len(result['answer'])} chars")
                
                if result['sources']:
                    print("   🎯 FOUND CONTENT!")
                    break
                else:
                    print("   ❌ No sources found")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
    
    print(f"\n{'='*50}")

if __name__ == "__main__":
    test_simple_search()
