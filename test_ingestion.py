#!/usr/bin/env python3
"""
Test script for content ingestion functionality
"""

import requests
import json

# Test the new content ingestion endpoint
def test_content_ingestion():
    try:
        # Test data mimicking what the Chrome extension would send
        test_content = {
            "title": "Test Canvas Assignment",
            "content": "This is a test assignment content for testing the ingestion pipeline.",
            "source": "canvas_link",
            "url": "https://canvas.test.edu/courses/123/assignments/456",
            "content_type": "assignment",
            "context": "Module 1: Introduction",
            "course_id": "123",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # For local testing (when running locally)
        base_url = "http://localhost:8000"
        
        print("🧪 Testing content ingestion endpoint...")
        print(f"📤 Sending request to: {base_url}/ingest-content")
        print(f"📋 Content: {test_content['title']}")
        
        response = requests.post(
            f"{base_url}/ingest-content",
            json=test_content,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Content ingestion successful!")
            print(f"📊 Processing time: {result.get('processing_time', 'Unknown')}s")
            print(f"🆔 Content ID: {result.get('content_id', 'Unknown')}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("🔌 Connection failed - make sure the API server is running on localhost:8000")
        print("📝 To start the server, run: python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Canvas AI Assistant - Content Ingestion Test")
    print("=" * 50)
    
    success = test_content_ingestion()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("📚 Content should now be available in the knowledge base")
    else:
        print("💥 Test failed - check the error messages above")
        print("🔧 Make sure the API server is running and accessible")
