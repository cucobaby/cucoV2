#!/usr/bin/env python3
"""
Quick verification that Chrome extension would work with updated endpoints
"""
import requests
import json

def test_chrome_extension_flow():
    """Test the complete Chrome extension flow"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Testing Complete Chrome Extension Flow")
    print("=" * 50)
    
    # Step 1: Test upload-content endpoint (what the updated extension should use)
    print("\n📤 Step 1: Testing upload-content endpoint")
    upload_data = {
        "title": "Cell Biology - Nucleus Function",
        "content": "The cell nucleus is the control center of the cell and contains the cell's DNA. Protein structures have primary, secondary, tertiary, and quaternary levels of organization.",
        "source": "canvas_chrome_extension",
        "url": "https://canvas.test.edu/courses/123/pages/cell-biology",
        "content_type": "page",
        "timestamp": "2025-08-06T05:45:00.000Z"
    }
    
    try:
        response = requests.post(
            f"{base_url}/upload-content",
            json=upload_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"✅ Upload successful: {upload_result['message']}")
            print(f"   Content ID: {upload_result.get('content_id', 'N/A')}")
            print(f"   Chunks created: {upload_result.get('chunks_created', 'N/A')}")
        else:
            print(f"❌ Upload failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Step 2: Test query endpoint
    print("\n❓ Step 2: Testing query endpoint")
    query_data = {
        "question": "What is the function of the cell nucleus?",
        "source": "canvas_chrome_extension"
    }
    
    try:
        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            query_result = response.json()
            answer = query_result.get('answer', query_result.get('response', 'No answer'))
            print(f"✅ Query successful!")
            print(f"   Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
        else:
            print(f"❌ Query failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False
    
    print("\n🎉 All tests passed! Chrome extension should work now.")
    print("\nNext steps:")
    print("1. Reload the Chrome extension")
    print("2. Navigate to a Canvas page")
    print("3. Click the '🤖 AI Assistant' button")
    print("4. Try uploading content and asking questions")
    
    return True

if __name__ == "__main__":
    test_chrome_extension_flow()
