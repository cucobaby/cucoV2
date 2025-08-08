#!/usr/bin/env python3
"""
Quick test for quiz intent detection
"""
import re

def test_quiz_detection():
    """Test the quiz detection patterns"""
    
    test_phrases = [
        "quiz me on glycolysis",
        "Quiz me about photosynthesis", 
        "create a quiz on DNA",
        "What is glycolysis?",
        "test my knowledge of biology",
        "practice questions about cells",
        "give me a quiz",
        "quiz on metabolism"
    ]
    
    quiz_keywords = [
        'quiz', 'test', 'questions', 'practice', 'assess', 'evaluate',
        'exam', 'review', 'study', 'flashcard', 'multiple choice', 
        'fill in blank', 'true false'
    ]
    
    quiz_patterns = [
        r'(create|generate|make|give me|start) (a |an )?(quiz|test)',
        r'quiz me (on|about)',
        r'quiz.*me.*on',  # More flexible pattern for "quiz me on X"
        r'(test|assess) my (knowledge|understanding)',
        r'practice (questions|problems)',
        r'(multiple choice|fill.in.blank|flashcard) (questions|quiz)',
        r'(\d+) questions? (about|on)',
        r'study (with|using) (questions|quiz|flashcards)',
        r'^quiz\s+.*',  # Any sentence starting with "quiz"
        r'quiz.*about',  # Quiz about something
    ]
    
    print("🧪 Testing Quiz Intent Detection")
    print("=" * 50)
    
    for phrase in test_phrases:
        phrase_lower = phrase.lower()
        
        # Check keywords
        has_keywords = any(keyword in phrase_lower for keyword in quiz_keywords)
        
        # Check patterns
        matched_patterns = []
        for pattern in quiz_patterns:
            if re.search(pattern, phrase_lower):
                matched_patterns.append(pattern)
        
        has_patterns = bool(matched_patterns)
        is_quiz = has_keywords or has_patterns
        
        print(f"\n'{phrase}'")
        print(f"  Keywords: {'✅' if has_keywords else '❌'}")
        print(f"  Patterns: {'✅' if has_patterns else '❌'}")
        if matched_patterns:
            for pattern in matched_patterns:
                print(f"    - {pattern}")
        print(f"  Result: {'🎯 QUIZ' if is_quiz else '❓ Q&A'}")

if __name__ == "__main__":
    test_quiz_detection()
