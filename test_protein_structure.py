#!/usr/bin/env python3
"""
Test the improved protein structure response
"""
import requests
import json

def test_protein_structure_question():
    """Test the specific protein structure question"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Testing Improved Protein Structure Response")
    print("=" * 60)
    
    question = "tell me the levels of protein structure"
    
    try:
        response = requests.post(
            f"{base_url}/ask-question",
            json={"question": question},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"📋 Question: '{question}'")
            print(f"✅ Status: SUCCESS")
            print(f"📊 Confidence: {result['confidence']}")
            print(f"📚 Sources: {len(result['sources'])} document(s)")
            print(f"⏱️ Response Time: {result['response_time']:.3f}s")
            print("\n" + "="*60)
            print("🤖 AI Response:")
            print(result['answer'])
            print("="*60)
            
            # Analyze response quality
            answer = result['answer']
            
            quality_indicators = [
                ("Contains 'Primary'", "primary" in answer.lower()),
                ("Contains 'Secondary'", "secondary" in answer.lower()), 
                ("Contains 'Tertiary'", "tertiary" in answer.lower()),
                ("Contains 'Quaternary'", "quaternary" in answer.lower()),
                ("Has structured format", "##" in answer),
                ("Educational tone", "study" in answer.lower() or "learning" in answer.lower()),
                ("Course materials only", "course materials" in answer.lower())
            ]
            
            print("\n📊 Response Quality Analysis:")
            for indicator, present in quality_indicators:
                status = "✅" if present else "❌"
                print(f"   {status} {indicator}")
            
            overall_score = sum(1 for _, present in quality_indicators if present)
            print(f"\n🎯 Overall Quality Score: {overall_score}/7")
            
            if overall_score >= 5:
                print("🎉 EXCELLENT - Response provides good educational content!")
            elif overall_score >= 3:
                print("👍 GOOD - Response is decent but could be improved")
            else:
                print("⚠️ NEEDS WORK - Response lacks key educational elements")
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Test failed: {e}")

if __name__ == "__main__":
    test_protein_structure_question()
