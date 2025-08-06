#!/usr/bin/env python3
"""
Quick test of the upload-content endpoint
"""
import requests
import json

def quick_test():
    """Quick test of the fixed endpoint"""
    
    url = "https://cucov2-production.up.railway.app/upload-content"
    
    data = {
        "title": "Biology Test - Protein Structure",
        "content": "Proteins have four levels of structure: primary (amino acid sequence), secondary (alpha helices and beta sheets), tertiary (3D folding), and quaternary (multiple subunits).",
        "source": "test_script",
        "content_type": "educational"
    }
    
    print("🧪 Testing upload-content endpoint...")
    print(f"📤 Uploading: {data['title']}")
    print(f"📏 Content length: {len(data['content'])} characters")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Content ID: {result.get('content_id')}")
            print(f"   Chunks: {result.get('chunks_created')}")
            
            # Test query
            print("\n🔍 Testing query...")
            query_response = requests.post(
                "https://cucov2-production.up.railway.app/query",
                json={"question": "what are the levels of protein structure"},
                timeout=30
            )
            
            if query_response.status_code == 200:
                query_result = query_response.json()
                print("✅ Query SUCCESS!")
                print(f"   Answer: {query_result['answer'][:200]}...")
            else:
                print(f"❌ Query failed: {query_response.status_code}")
                
        elif response.status_code == 422:
            print("❌ HTTP 422 - Validation Error:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:300])
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
