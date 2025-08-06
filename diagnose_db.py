#!/usr/bin/env python3
"""
Diagnose ChromaDB collection issues
"""
import requests

def diagnose_chromadb():
    """Check ChromaDB status and collection"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    # Test endpoints to see what's working
    endpoints = [
        "/health",
        "/debug/chromadb", 
        "/upload-status"
    ]
    
    print("🔍 ChromaDB Diagnostic")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"\n📍 {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {data}")
                except:
                    print(f"   Text: {response.text[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    print(f"\n{'='*50}")

if __name__ == "__main__":
    diagnose_chromadb()
