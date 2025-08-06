#!/usr/bin/env python3
"""
Test the fixed Chrome extension by simulating its exact request
"""
import requests
import json

def test_fixed_extension():
    """Test with the exact format the clean extension should send"""
    
    url = "https://cucov2-production.up.railway.app/upload-content"
    
    # This matches the clean extension format exactly
    test_data = {
        "title": "Test Canvas Assignment - Protein Structure",
        "content": "Protein structure has four levels: primary (amino acid sequence), secondary (alpha helices and beta sheets), tertiary (3D folding), and quaternary (multiple subunits). The cell nucleus contains DNA which codes for these proteins.",
        "source": "canvas_chrome_extension",
        "url": "https://canvas.example.com/courses/123/assignments/456",
        "content_type": "assignment",
        "timestamp": "2025-08-05T12:00:00.000Z"
    }
    
    print("🧪 Testing Clean Chrome Extension Format")
    print("=" * 50)
    print(f"📤 URL: {url}")
    print(f"📋 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📝 Response: {json.dumps(result, indent=2)}")
            
            # Test a query too
            print("\n" + "="*50)
            print("🤖 Testing Query Endpoint")
            
            query_response = requests.post(
                "https://cucov2-production.up.railway.app/query",
                json={"question": "What are the levels of protein structure?"},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            print(f"📊 Query Status: {query_response.status_code}")
            if query_response.status_code == 200:
                query_result = query_response.json()
                print("✅ QUERY SUCCESS!")
                print(f"🤖 Answer: {query_result.get('answer', 'No answer')}")
            else:
                print(f"❌ Query failed: {query_response.status_code}")
                print(f"   Response: {query_response.text}")
                
        elif response.status_code == 422:
            error_detail = response.json()
            print("❌ HTTP 422 - VALIDATION ERROR:")
            print(json.dumps(error_detail, indent=2))
            
            # Show specific field errors
            if 'detail' in error_detail and isinstance(error_detail['detail'], list):
                print("\n🚨 Validation Issues:")
                for error in error_detail['detail']:
                    if 'loc' in error and 'msg' in error:
                        field = ' -> '.join(str(x) for x in error['loc'])
                        print(f"   Field '{field}': {error['msg']}")
                        print(f"   Type: {error.get('type', 'unknown')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            print("Response body:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - API might be slow")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_extension()
