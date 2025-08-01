#!/usr/bin/env python3
"""
Get full ChromaDB diagnostic response
"""
import requests
import json

url = "https://cucov2-production.up.railway.app/debug/chromadb"

try:
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Failed: {e}")
