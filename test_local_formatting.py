#!/usr/bin/env python3
"""
Test script to check local API response formatting
"""

import requests
import json
import time

def test_local_api():
    """Test the local API response to see raw formatting"""
    
    print("🧪 Testing Local API Response Formatting")
    print("=" * 60)
    
    # Test both endpoints
    endpoints = [
        ("Regular Query", "http://127.0.0.1:8001/query"),
        ("Parsed Query", "http://127.0.0.1:8001/query-parsed")
    ]
    
    test_question = {"question": "what is ATP"}
    
    for endpoint_name, url in endpoints:
        print(f"\n🔍 Testing {endpoint_name}: {url}")
        print("-" * 40)
        
        try:
            response = requests.post(
                url,
                json=test_question,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if endpoint_name == "Regular Query":
                    answer = result.get('answer', '')
                    print(f"📝 Response Length: {len(answer)} characters")
                    print(f"📋 Sources: {result.get('sources', [])}")
                    print("\n🔍 Raw Answer Content (first 500 chars):")
                    print("=" * 50)
                    print(repr(answer[:500]))  # Show raw string with escape chars
                    print("=" * 50)
                    
                    print("\n📄 Formatted Answer:")
                    print("=" * 50)
                    print(answer[:800])  # Show formatted version
                    print("=" * 50)
                    
                    # Check for line breaks
                    line_breaks = answer.count('\n')
                    double_breaks = answer.count('\n\n')
                    print(f"\n📊 Line Break Analysis:")
                    print(f"   - Single line breaks (\\n): {line_breaks}")
                    print(f"   - Double line breaks (\\n\\n): {double_breaks}")
                    print(f"   - Contains section headers (##): {'##' in answer}")
                    print(f"   - Contains learning objective: {'Learning Objective' in answer}")
                    
                else:  # Parsed Query
                    print(f"📝 Parsed Response Structure:")
                    for key, value in result.items():
                        if key == 'sources':
                            print(f"   📚 {key}: {value}")
                        elif isinstance(value, list):
                            print(f"   📋 {key}: {len(value)} items")
                        elif isinstance(value, str):
                            print(f"   📄 {key}: {len(value)} chars")
                        else:
                            print(f"   ❓ {key}: {type(value)}")
                            
                    # Show a sample of the content
                    if 'definition_overview' in result:
                        print(f"\n🔍 Sample Definition Content:")
                        print("=" * 50)
                        print(repr(result['definition_overview'][:200]))
                        print("=" * 50)
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the local server running?")
            print("   Try starting it with: python -m uvicorn src.railway_api:app --reload --port 8001")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_production_api():
    """Test the production API for comparison"""
    
    print("\n\n🌐 Testing Production API for Comparison")
    print("=" * 60)
    
    base_url = "https://cucov2-production.up.railway.app"
    test_question = {"question": "what is ATP"}
    
    try:
        response = requests.post(
            f"{base_url}/query",
            json=test_question,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            print(f"📝 Production Response Length: {len(answer)} characters")
            print(f"📋 Sources: {result.get('sources', [])}")
            
            # Check formatting
            line_breaks = answer.count('\n')
            double_breaks = answer.count('\n\n')
            print(f"\n📊 Production Line Break Analysis:")
            print(f"   - Single line breaks (\\n): {line_breaks}")
            print(f"   - Double line breaks (\\n\\n): {double_breaks}")
            print(f"   - Contains section headers (##): {'##' in answer}")
            
            print(f"\n🔍 Production Raw Content (first 300 chars):")
            print("=" * 50)
            print(repr(answer[:300]))
            print("=" * 50)
            
        else:
            print(f"❌ Production request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Production test error: {e}")

if __name__ == "__main__":
    # Test local first
    test_local_api()
    
    # Test production for comparison
    test_production_api()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("   - Check if line breaks are present in raw response")
    print("   - Compare local vs production formatting")
    print("   - Identify if issue is in generation or display")
