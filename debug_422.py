#!/usr/bin/env python3
"""
Test different scenarios that might cause HTTP 422 validation errors
"""
import requests
import json

def test_scenarios():
    """Test different input scenarios that might cause validation errors"""
    
    url = "https://cucov2-production.up.railway.app/upload-content"
    
    test_cases = [
        {
            "name": "Valid case (should work)",
            "data": {
                "title": "Test Canvas Page",
                "content": "This is test content about protein structure levels",
                "source": "canvas_chrome_extension",
                "url": "https://canvas.example.com/courses/123/pages/test",
                "content_type": "page",
                "timestamp": "2025-08-05T10:00:00.000Z"
            }
        },
        {
            "name": "Missing content_type (might cause 422)",
            "data": {
                "title": "Test Canvas Page",
                "content": "This is test content about protein structure levels",
                "source": "canvas_chrome_extension",
                "url": "https://canvas.example.com/courses/123/pages/test",
                "timestamp": "2025-08-05T10:00:00.000Z"
                # missing content_type
            }
        },
        {
            "name": "Empty content (should cause 422)",
            "data": {
                "title": "Test Canvas Page",
                "content": "",  # Empty content
                "source": "canvas_chrome_extension",
                "url": "https://canvas.example.com/courses/123/pages/test",
                "content_type": "page",
                "timestamp": "2025-08-05T10:00:00.000Z"
            }
        },
        {
            "name": "Short content (should cause 422)",
            "data": {
                "title": "Test Canvas Page",
                "content": "Hi",  # Too short
                "source": "canvas_chrome_extension",
                "url": "https://canvas.example.com/courses/123/pages/test",
                "content_type": "page",
                "timestamp": "2025-08-05T10:00:00.000Z"
            }
        },
        {
            "name": "Invalid timestamp format",
            "data": {
                "title": "Test Canvas Page",
                "content": "This is test content about protein structure levels",
                "source": "canvas_chrome_extension",
                "url": "https://canvas.example.com/courses/123/pages/test",
                "content_type": "page",
                "timestamp": "invalid-timestamp"
            }
        },
        {
            "name": "Missing required title",
            "data": {
                # "title": "Test Canvas Page",  # Missing title
                "content": "This is test content about protein structure levels",
                "source": "canvas_chrome_extension",
                "url": "https://canvas.example.com/courses/123/pages/test",
                "content_type": "page",
                "timestamp": "2025-08-05T10:00:00.000Z"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {test_case['name']}")
        print(f"📋 Data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                url,
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS: {result}")
            elif response.status_code == 422:
                error_detail = response.json()
                print(f"❌ VALIDATION ERROR (422): {json.dumps(error_detail, indent=2)}")
                
                # Show specific field errors
                if 'detail' in error_detail and isinstance(error_detail['detail'], list):
                    for error in error_detail['detail']:
                        if 'loc' in error and 'msg' in error:
                            field = ' -> '.join(str(x) for x in error['loc'])
                            print(f"   🚨 Field '{field}': {error['msg']}")
            else:
                print(f"❌ Other Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_scenarios()
