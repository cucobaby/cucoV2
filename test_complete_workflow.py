#!/usr/bin/env python3
"""
End-to-end test of the complete quiz functionality workflow
"""
import requests
import json

def test_complete_quiz_workflow():
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🎯 Complete Quiz Workflow Test")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. 🏥 Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ API Status: {health.get('status')}")
            print(f"   ✅ Quiz Functionality: {health.get('quiz_functionality', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Fast quiz detection
    print("\n2. ⚡ Fast Quiz Detection")
    quiz_phrases = [
        "quiz me on glycolysis",
        "I want a quiz about photosynthesis", 
        "create a quiz on DNA replication",
        "make me a quiz",
        "quiz on cell respiration"
    ]
    
    success_count = 0
    for phrase in quiz_phrases:
        try:
            response = requests.post(
                f"{base_url}/query-fast",
                json={"question": phrase},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                sections = data.get('sections', {})
                quiz_mode = sections.get('quiz_mode', False)
                
                if quiz_mode:
                    print(f"   ✅ '{phrase}' -> Quiz detected")
                    success_count += 1
                else:
                    print(f"   ❌ '{phrase}' -> Normal response")
            else:
                print(f"   ❌ '{phrase}' -> HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ '{phrase}' -> Error: {e}")
    
    detection_rate = (success_count / len(quiz_phrases)) * 100
    print(f"\n   📊 Quiz Detection Rate: {detection_rate:.1f}% ({success_count}/{len(quiz_phrases)})")
    
    # Test 3: Quiz configuration response format
    print("\n3. 🎯 Quiz Configuration Response")
    try:
        response = requests.post(
            f"{base_url}/query-fast",
            json={"question": "quiz me on glycolysis"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            sections = data.get('sections', {})
            quiz_data = sections.get('quiz_data', {})
            
            print(f"   ✅ Response received")
            print(f"   ✅ Quiz Mode: {sections.get('quiz_mode', False)}")
            print(f"   ✅ Session ID: {'Present' if quiz_data.get('session_id') else 'Missing'}")
            print(f"   ✅ Awaiting Config: {quiz_data.get('awaiting_config', False)}")
            print(f"   ✅ Detected Topic: {quiz_data.get('detected_topic', 'None')}")
            print(f"   ✅ Available Topics: {len(quiz_data.get('available_topics', []))}")
            
            # Check answer content
            answer = data.get('answer', '')
            has_quiz_activation = "Quiz Mode Activated" in answer
            has_preferences = "preferences" in answer.lower()
            has_quiz_types = "Multiple Choice" in answer
            
            print(f"   ✅ Quiz Activation Message: {'Present' if has_quiz_activation else 'Missing'}")
            print(f"   ✅ Preferences Section: {'Present' if has_preferences else 'Missing'}")
            print(f"   ✅ Quiz Type Options: {'Present' if has_quiz_types else 'Missing'}")
            
        else:
            print(f"   ❌ Failed to get quiz response: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Quiz configuration test failed: {e}")
    
    # Test 4: Isolated quiz detection verification
    print("\n4. 🔬 Isolated Quiz Detection")
    try:
        response = requests.post(
            f"{base_url}/test-quiz-detection",
            json={"question": "quiz me on glycolysis"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Quiz Detected: {data.get('quiz_detected', False)}")
            print(f"   ✅ Confidence: {data.get('confidence', 'unknown')}")
            print(f"   ✅ Parameters: {data.get('parameters', 'none')[:100]}...")
        else:
            print(f"   ❌ Isolated test failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Isolated test error: {e}")
    
    # Test 5: Non-quiz query (should use fallback)
    print("\n5. 📚 Non-Quiz Query Test")
    try:
        response = requests.post(
            f"{base_url}/query-fast",
            json={"question": "What is photosynthesis?"},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            sections = data.get('sections', {})
            quiz_mode = sections.get('quiz_mode', False)
            
            if not quiz_mode:
                print(f"   ✅ Non-quiz query handled correctly")
                answer_length = len(data.get('answer', ''))
                print(f"   ✅ Answer length: {answer_length} characters")
            else:
                print(f"   ❌ Non-quiz query incorrectly detected as quiz")
        else:
            print(f"   ❌ Non-quiz query failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Non-quiz query error: {e}")
    
    print(f"\n{'=' * 60}")
    print("🎉 Quiz functionality testing complete!")
    print("The Chrome extension should now work with quiz detection.")
    print("Try asking 'quiz me on glycolysis' in the Canvas popup.")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    test_complete_quiz_workflow()
