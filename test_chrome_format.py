#!/usr/bin/env python3
"""
Test exact Chrome extension request format
"""
import requests
import json

def test_chrome_extension_format():
    """Test with exact Chrome extension request format"""
    
    url = "https://cucov2-production.up.railway.app/upload-content"
    
    # This should match exactly what the Chrome extension sends
    chrome_data = {
        "title": "Test Canvas Page",
        "content": "This is test content from a Canvas page about protein structure levels.",
        "source": "canvas_chrome_extension",
        "url": "https://canvas.example.com/courses/123/pages/test",
        "content_type": "page",
        "timestamp": "2025-08-06T05:30:00.000Z"
    }
    
    print("🧪 Testing Chrome Extension Format")
    print("=" * 40)
    print(f"📤 URL: {url}")
    print(f"📋 Data: {json.dumps(chrome_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=chrome_data,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(json.dumps(result, indent=2))
        elif response.status_code == 422:
            print("❌ HTTP 422 - Validation Error (This is your issue):")
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2))
            
            # Show what field is causing the issue
            if 'detail' in error_detail and isinstance(error_detail['detail'], list):
                for error in error_detail['detail']:
                    if 'loc' in error and 'msg' in error:
                        field = ' -> '.join(str(x) for x in error['loc'])
                        print(f"\n🚨 Field '{field}': {error['msg']}")
                        print(f"   Type: {error.get('type', 'unknown')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            print("Response body:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chrome_extension_format()
