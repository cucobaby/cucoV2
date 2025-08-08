#!/usr/bin/env python3
"""
Comprehensive test of Railway quiz functionality
"""
import requests
import json
import time

def test_railway_quiz_comprehensive():
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Comprehensive Railway Quiz Test")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ API Status: {health.get('status')}")
            print(f"   ✅ CoreAssistant: {health.get('core_assistant', 'Unknown')}")
            print(f"   ✅ Quiz Functionality: {health.get('quiz_functionality', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test 2: Simple query first
    print("\n2. Simple Query Test:")
    try:
        response = requests.post(
            f"{base_url}/query",
            json={"question": "What is photosynthesis?"},
            timeout=20
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Simple query works")
        else:
            print(f"   ❌ Simple query failed: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Simple query error: {e}")
    
    # Test 3: Quiz detection
    print("\n3. Quiz Detection Test:")
    quiz_queries = [
        "quiz me on glycolysis",
        "I want a quiz about photosynthesis",
        "create a quiz on DNA replication"
    ]
    
    for query in quiz_queries:
        print(f"\n   Testing: '{query}'")
        try:
            response = requests.post(
                f"{base_url}/query",
                json={"question": query},
                timeout=25
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                sections = data.get('sections', {})
                quiz_mode = sections.get('quiz_mode', False)
                
                if quiz_mode:
                    print("   ✅ Quiz mode detected!")
                    quiz_data = sections.get('quiz_data', {})
                    print(f"   Quiz type: {quiz_data.get('awaiting_config', False)}")
                    topics = quiz_data.get('available_topics', [])
                    print(f"   Available topics: {len(topics)} topics")
                    if topics:
                        print(f"   First few topics: {topics[:3]}")
                else:
                    print("   ❌ Normal Q&A response (not quiz mode)")
                    answer_preview = data.get('answer', '')[:150]
                    print(f"   Answer: {answer_preview}...")
            else:
                print(f"   ❌ Error response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("   ❌ Request timed out (25s)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_railway_quiz_comprehensive()
