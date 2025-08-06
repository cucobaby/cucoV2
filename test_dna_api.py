#!/usr/bin/env python3
import requests
import json

def test_dna_question():
    url = "https://cucov2-production.up.railway.app/query"
    data = {"question": "explain DNA replication"}
    
    print("Testing: 'explain DNA replication'")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer found')
            sources = result.get('sources', [])
            
            print(f"\nAnswer Length: {len(answer)} characters")
            print(f"Sources: {sources}")
            print("\n=== RESPONSE ===")
            print(answer)
            print("=" * 50)
            
            # Check for quality indicators
            if "Based on your course materials:" in answer and len(answer) < 500:
                print("\n❌ ISSUE: Getting fragmented fallback response")
            elif "DNA replication" in answer and len(answer) > 300:
                print("\n✅ GOOD: Comprehensive response detected")
            else:
                print("\n⚠️  UNKNOWN: Response pattern unclear")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dna_question()
