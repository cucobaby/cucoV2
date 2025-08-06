#!/usr/bin/env python3
"""
Test the protein structure question with current system
"""
import requests
import json

def test_protein_question():
    url = 'https://cucov2-production.up.railway.app/query'
    question = 'What are the four levels of protein structure?'
    
    print(f"Testing question: {question}")
    print("="*50)
    
    try:
        response = requests.post(url, json={'question': question}, timeout=15)
        result = response.json()
        
        print(f"Response length: {len(result['answer'])} characters")
        print(f"Sources: {len(result['sources'])}")
        print("\nAnswer:")
        print("-" * 30)
        print(result['answer'])
        print("-" * 30)
        
        # Analyze response quality
        answer_lower = result['answer'].lower()
        
        # Check for conciseness (should be under 800 chars for good quality)
        is_concise = len(result['answer']) < 800
        print(f"\n✅ Concise response: {'YES' if is_concise else 'NO'} ({len(result['answer'])} chars)")
        
        # Check for directness
        has_direct_answer = any(level in answer_lower for level in ['primary', 'secondary', 'tertiary', 'quaternary'])
        print(f"✅ Contains protein levels: {'YES' if has_direct_answer else 'NO'}")
        
        # Check for educational formatting
        has_good_format = 'based on' in answer_lower or 'course' in answer_lower
        print(f"✅ Educational formatting: {'YES' if has_good_format else 'NO'}")
        
        overall_quality = "GOOD" if (is_concise and has_direct_answer and has_good_format) else "NEEDS IMPROVEMENT"
        print(f"\n🎯 Overall Quality: {overall_quality}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_protein_question()
