#!/usr/bin/env python3
"""
Test script to verify the API server works locally
"""
import requests
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API endpoints...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Analyze content
    test_content = """
    Photosynthesis is the process by which plants convert light energy into chemical energy.
    It occurs in chloroplasts and involves two main stages: light-dependent reactions and the Calvin cycle.
    The products are glucose and oxygen.
    """
    
    try:
        response = requests.post(
            f"{base_url}/analyze-content",
            json={
                "content": test_content,
                "title": "Test Photosynthesis Content"
            },
            timeout=30
        )
        print(f"✅ Content analysis: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Subject: {result['subject_area']}")
            print(f"   Topics: {result['main_topics']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Content analysis failed: {e}")
    
    # Test 3: Ask question
    try:
        response = requests.post(
            f"{base_url}/ask-question",
            json={
                "question": "What is photosynthesis?",
                "context_limit": 3
            },
            timeout=30
        )
        print(f"✅ Question answering: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Answer: {result['answer'][:100]}...")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Question answering failed: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 API Server Test Script")
    print("=" * 40)
    print("Make sure the server is running first:")
    print("python src/api_server.py")
    print("=" * 40)
    
    input("Press Enter when server is ready...")
    test_api_endpoints()
