#!/usr/bin/env python3
"""
Test what content is actually stored in the Canvas AI Assistant
"""
import requests
import json

def test_stored_content():
    """Test what content is stored and accessible"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔍 Testing Stored Content Accessibility")
    print("=" * 50)
    
    # Test questions related to the study guide content I can see
    test_questions = [
        "What topics are in my study guide?",
        "Tell me about photosynthesis from my materials",
        "What are the learning objectives in my uploaded content?",
        "What vocabulary terms are defined in my materials?",
        "Explain cellular respiration from my course content"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🤔 Test {i}: {question}")
        
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": question},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Status: Success")
                print(f"   📊 Confidence: {result['confidence']}")
                print(f"   📚 Sources: {len(result['sources'])}")
                print(f"   💬 Answer Preview: {result['answer'][:200]}...")
                
                # Check if the answer seems relevant
                answer_lower = result['answer'].lower()
                question_lower = question.lower()
                
                # Look for key terms from the question in the answer
                relevance_indicators = []
                if 'photosynthesis' in question_lower and 'photosynthesis' in answer_lower:
                    relevance_indicators.append('photosynthesis match')
                if 'cellular respiration' in question_lower and 'cellular' in answer_lower:
                    relevance_indicators.append('cellular respiration match')
                if 'learning objectives' in question_lower and ('objective' in answer_lower or 'learn' in answer_lower):
                    relevance_indicators.append('learning objectives match')
                if 'vocabulary' in question_lower and ('vocabulary' in answer_lower or 'term' in answer_lower):
                    relevance_indicators.append('vocabulary match')
                
                if relevance_indicators:
                    print(f"   🎯 Relevance: ✅ GOOD - {', '.join(relevance_indicators)}")
                else:
                    print(f"   ⚠️ Relevance: POOR - doesn't match question topic")
                    
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

if __name__ == "__main__":
    test_stored_content()
