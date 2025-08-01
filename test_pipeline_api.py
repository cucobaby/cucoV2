#!/usr/bin/env python3
"""
Test script for the Pipeline API
"""
import requests
import json

def test_ingest_content():
    """Test the /ingest-content endpoint"""
    
    url = "https://cucov2-production.up.railway.app/ingest-content"
    
    payload = {
        "title": "Test Canvas Content",
        "content": "This is a test Canvas page content for pipeline processing. It contains important information about biology concepts.",
        "content_type": "canvas_page", 
        "source": "test_script",
        "url": "https://canvas.test.edu/courses/123/pages/test",
        "course_id": "BIOL101",
        "timestamp": "2025-01-31T06:00:00Z"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing /ingest-content endpoint...")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"🔥 Request failed: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    test_ingest_content()
