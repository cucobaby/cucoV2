#!/usr/bin/env python3
import requests

# Test specific photosynthesis query
response = requests.post(
    'https://cucov2-production.up.railway.app/ask-question',
    json={'question': 'Tell me about Calvin cycle and ATP from my photosynthesis materials'}
)

if response.status_code == 200:
    result = response.json()
    print("Photosynthesis Query Result:")
    print(result['answer'])
    print(f"\nSources: {result['sources']}")
else:
    print(f"Error: {response.status_code}")
