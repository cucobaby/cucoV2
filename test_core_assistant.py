#!/usr/bin/env python3
"""
Test script to verify CoreAssistant integration with quiz functionality
"""
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_core_assistant_import():
    """Test importing CoreAssistant"""
    try:
        from core_assistant import CoreAssistant
        print("✅ CoreAssistant import successful")
        return True
    except Exception as e:
        print(f"❌ CoreAssistant import failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def test_quiz_detection():
    """Test quiz detection functionality"""
    try:
        from core_assistant import CoreAssistant
        
        # Create minimal test (without requiring ChromaDB)
        print("Testing quiz detection patterns...")
        
        # Test the detection method directly
        assistant = CoreAssistant.__new__(CoreAssistant)  # Create instance without __init__
        
        # Test quiz detection
        test_question = "quiz me on glycolysis"
        result = assistant._detect_quiz_intent(test_question)
        
        print(f"Quiz detection result: {result}")
        print(f"Is quiz request: {result['is_quiz_request']}")
        print(f"Confidence: {result['confidence']}")
        
        return result['is_quiz_request']
        
    except Exception as e:
        print(f"❌ Quiz detection test failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def test_quiz_generator_import():
    """Test importing QuizGenerator"""
    try:
        from quiz_generator import QuizGenerator, QuizType, QuizFormat
        print("✅ QuizGenerator import successful")
        return True
    except Exception as e:
        print(f"❌ QuizGenerator import failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🧪 Testing CoreAssistant Quiz Integration")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing QuizGenerator import...")
    quiz_import_ok = test_quiz_generator_import()
    
    print("\n2. Testing CoreAssistant import...")
    core_import_ok = test_core_assistant_import()
    
    if quiz_import_ok and core_import_ok:
        print("\n3. Testing quiz detection...")
        quiz_detection_ok = test_quiz_detection()
        
        if quiz_detection_ok:
            print("\n✅ All tests passed! Quiz functionality should work.")
        else:
            print("\n❌ Quiz detection failed!")
    else:
        print("\n❌ Import failures detected!")
    
    print("\n" + "=" * 50)
