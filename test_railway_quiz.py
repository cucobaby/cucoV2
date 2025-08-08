#!/usr/bin/env python3
"""
Test quiz functionality on Railway deployment
"""
import requests
import json

def test_quiz_on_railway():
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Testing Quiz Functionality on Railway Deployment")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   API Version: {health_data.get('version', 'unknown')}")
            print(f"   Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test 2: Quiz request
    print("\n2. Testing quiz detection with 'quiz me on glycolysis'...")
    try:
        response = requests.post(
            f"{base_url}/query",
            json={"question": "quiz me on glycolysis"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {data.get('sections', {}).get('quiz_mode', 'Not quiz mode')}")
            
            # Check if it's a quiz response
            sections = data.get('sections', {})
            if sections.get('quiz_mode'):
                print("   ✅ Quiz mode detected!")
                quiz_data = sections.get('quiz_data', {})
                print(f"   Quiz type: {quiz_data.get('awaiting_config', 'unknown')}")
                print(f"   Available topics: {quiz_data.get('available_topics', [])}")
            else:
                print("   ❌ Still getting normal Q&A response")
                print(f"   Answer preview: {data.get('answer', '')[:200]}...")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Quiz test failed: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_quiz_on_railway()
