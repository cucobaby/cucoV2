#!/usr/bin/env python3
"""
Local Query Testing Tool for CucoV2
Rapid iteration tool for improving answer quality
"""

import requests
import json
import time
import sys
from datetime import datetime

# API Configuration
API_BASE_URL = "https://cucov2-production.up.railway.app"

class CucoTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
    
    def test_query(self, question, expected_keywords=None):
        """Test a single query and return detailed results"""
        print(f"\n🤖 Testing: {question}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/query",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results
                print(f"✅ SUCCESS ({response_time:.2f}s)")
                print(f"\n📋 ANSWER:")
                print(result.get('answer', 'No answer provided'))
                
                if result.get('sources'):
                    print(f"\n📚 SOURCES ({len(result['sources'])}):")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"  {i}. {source}")
                
                # Quality assessment
                answer_length = len(result.get('answer', ''))
                has_sources = len(result.get('sources', [])) > 0
                
                quality_score = self._assess_quality(result, expected_keywords)
                
                print(f"\n📊 QUALITY METRICS:")
                print(f"  • Answer length: {answer_length} characters")
                print(f"  • Sources found: {len(result.get('sources', []))}")
                print(f"  • Response time: {response_time:.2f}s")
                print(f"  • Quality score: {quality_score}/10")
                
                # Store result for analysis
                self.test_results.append({
                    'question': question,
                    'answer': result.get('answer'),
                    'sources': result.get('sources', []),
                    'response_time': response_time,
                    'quality_score': quality_score,
                    'timestamp': datetime.now().isoformat()
                })
                
                return True
                
            else:
                print(f"❌ ERROR {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return False
    
    def _assess_quality(self, result, expected_keywords=None):
        """Simple quality assessment (0-10)"""
        score = 0
        answer = result.get('answer', '').lower()
        
        # Length check (reasonable answer length)
        if 100 <= len(answer) <= 2000:
            score += 3
        elif len(answer) >= 50:
            score += 1
            
        # Sources check
        if result.get('sources'):
            score += 2
            
        # Keyword relevance check
        if expected_keywords:
            found_keywords = sum(1 for keyword in expected_keywords if keyword.lower() in answer)
            score += min(3, found_keywords)
            
        # Basic structure check (sentences, punctuation)
        if '.' in answer and len(answer.split('.')) > 1:
            score += 2
            
        return min(10, score)
    
    def run_test_suite(self):
        """Run a comprehensive test suite"""
        print("🚀 Starting CucoV2 Quality Test Suite")
        print("=" * 60)
        
        # Test cases with expected keywords
        test_cases = [
            {
                "question": "What are the main topics covered in this course?",
                "keywords": ["topic", "course", "subject", "material"]
            },
            {
                "question": "Summarize the key concepts from the uploaded content",
                "keywords": ["concept", "key", "important", "main"]
            },
            {
                "question": "What should I focus on for studying?",
                "keywords": ["study", "focus", "important", "exam", "review"]
            },
            {
                "question": "Explain the relationship between the different topics",
                "keywords": ["relationship", "connection", "related", "between"]
            },
            {
                "question": "Give me practice questions based on this material",
                "keywords": ["question", "practice", "test", "quiz", "example"]
            }
        ]
        
        success_count = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[TEST {i}/{total_tests}]")
            success = self.test_query(test_case["question"], test_case["keywords"])
            if success:
                success_count += 1
            
            time.sleep(1)  # Rate limiting
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 TEST SUMMARY: {success_count}/{total_tests} passed")
        
        if self.test_results:
            avg_quality = sum(r['quality_score'] for r in self.test_results) / len(self.test_results)
            avg_response_time = sum(r['response_time'] for r in self.test_results) / len(self.test_results)
            
            print(f"📊 Average quality score: {avg_quality:.1f}/10")
            print(f"⏱️  Average response time: {avg_response_time:.2f}s")
            
            # Identify improvement areas
            low_quality = [r for r in self.test_results if r['quality_score'] < 6]
            if low_quality:
                print(f"\n⚠️  {len(low_quality)} queries need improvement:")
                for result in low_quality:
                    print(f"   • \"{result['question'][:50]}...\" (score: {result['quality_score']}/10)")
    
    def interactive_mode(self):
        """Interactive testing mode"""
        print("🤖 CucoV2 Interactive Testing Mode")
        print("Type 'quit' to exit, 'suite' to run full test suite")
        print("-" * 50)
        
        while True:
            question = input("\n❓ Enter your question: ").strip()
            
            if question.lower() == 'quit':
                break
            elif question.lower() == 'suite':
                self.run_test_suite()
                continue
            elif not question:
                continue
            
            self.test_query(question)

def main():
    tester = CucoTester()
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        tester.test_query(question)
    else:
        # Interactive mode
        try:
            print("Choose mode:")
            print("1. Interactive testing")
            print("2. Run full test suite")
            choice = input("Enter choice (1 or 2): ").strip()
            
            if choice == "2":
                tester.run_test_suite()
            else:
                tester.interactive_mode()
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
