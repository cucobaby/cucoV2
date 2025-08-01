#!/usr/bin/env python3
import requests

# Test what specific content you have
response = requests.post(
    'https://cucov2-production.up.railway.app/ask-question',
    json={'question': 'What specific topics or subjects are covered in my study materials?'}
)

if response.status_code == 200:
    result = response.json()
    print("🎓 Your Study Materials Summary:")
    print("=" * 50)
    print(result['answer'])
    print(f"\nConfidence: {result['confidence']}")
    print(f"Sources: {len(result['sources'])}")
    print(f"Source IDs: {result['sources'][:3]}")  # Show first 3 source IDs
else:
    print(f"Error: {response.status_code}")
