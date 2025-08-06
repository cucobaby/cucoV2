#!/usr/bin/env python3
import requests

# Test the improved protein structure response
try:
    response = requests.post(
        'https://cucov2-production.up.railway.app/ask-question',
        json={'question': 'what are the levels of protein structure'},
        timeout=10
    )
    
    result = response.json()
    
    print("RESPONSE ANALYSIS:")
    print("=" * 60)
    print(f"Status: {response.status_code}")
    print(f"Confidence: {result.get('confidence', 0)}")
    print(f"Sources Found: {len(result.get('sources', []))}")
    print(f"Response Time: {result.get('response_time', 0):.3f}s")
    
    answer = result.get('answer', '')
    print(f"\nAnswer Length: {len(answer)} characters")
    
    # Quality check
    quality_indicators = [
        ('Contains Primary', 'primary' in answer.lower()),
        ('Contains Secondary', 'secondary' in answer.lower()),
        ('Contains Tertiary', 'tertiary' in answer.lower()),
        ('Contains Quaternary', 'quaternary' in answer.lower()),
        ('Mentions Alpha Helix', 'alpha helix' in answer.lower()),
        ('Educational Format', '##' in answer or '#' in answer)
    ]
    
    print("\nQuality Analysis:")
    score = 0
    for indicator, present in quality_indicators:
        status = "✅" if present else "❌"
        print(f"  {status} {indicator}")
        if present:
            score += 1
    
    print(f"\nQuality Score: {score}/6")
    
    if score >= 4:
        print("🎉 EXCELLENT - Response quality is good!")
    elif score >= 2:
        print("👍 DECENT - Response has some good elements")
    else:
        print("⚠️ NEEDS WORK - Response quality could be better")
    
    print("\n" + "="*60)
    print("FULL ANSWER:")
    print("="*60)
    print(answer)
    print("="*60)
    
except Exception as e:
    print(f"ERROR: {e}")
