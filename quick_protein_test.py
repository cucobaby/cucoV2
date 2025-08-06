#!/usr/bin/env python3
"""
Quick test of protein structure response
"""
import requests

response = requests.post(
    'https://cucov2-production.up.railway.app/ask-question',
    json={'question': 'tell me the levels of protein structure'},
    timeout=15
)

if response.status_code == 200:
    result = response.json()
    print("PROTEIN STRUCTURE RESPONSE:")
    print("=" * 60)
    print(result['answer'])
    print("=" * 60)
    print(f"Confidence: {result['confidence']}")
    print(f"Sources: {len(result['sources'])}")
    print(f"Response Time: {result['response_time']:.3f}s")
    
    # Check quality indicators
    answer_lower = result['answer'].lower()
    indicators = [
        ("Has Primary", "primary" in answer_lower),
        ("Has Secondary", "secondary" in answer_lower),
        ("Has Tertiary", "tertiary" in answer_lower),
        ("Has Quaternary", "quaternary" in answer_lower),
        ("Mentions Alpha Helix", "alpha helix" in answer_lower),
        ("Mentions Beta Sheet", "beta sheet" in answer_lower)
    ]
    
    print("\nQuality Check:")
    for name, present in indicators:
        print(f"  {'✅' if present else '❌'} {name}")
else:
    print(f"Error: {response.status_code} - {response.text}")
