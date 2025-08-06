#!/usr/bin/env python3
import requests
import json

def test_openai_integration():
    """Test if OpenAI integration is working on Railway"""
    
    print("🧪 Testing OpenAI Integration on Railway...")
    
    # Test with a simple question
    test_payload = {
        "question": "test openai integration",
        "source": "test"
    }
    
    try:
        response = requests.post(
            'https://cucov2-production.up.railway.app/ask-question',
            json=test_payload,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            
            # Check for OpenAI failure indicators
            if "OpenAI integration needs to be configured" in answer:
                print("❌ OpenAI NOT working - API key missing or invalid")
                return False
            elif "OpenAI helps format responses but adds no external knowledge" in answer:
                print("✅ OpenAI IS working - response formatted by OpenAI")
                return True
            else:
                print("⚠️  Unclear OpenAI status - checking response:")
                print(f"Response: {answer[:200]}...")
                return "unclear"
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    result = test_openai_integration()
    
    if result == False:
        print("\n📋 To fix OpenAI integration:")
        print("1. Go to Railway dashboard")
        print("2. Open your project")
        print("3. Go to Variables tab")
        print("4. Add: OPENAI_API_KEY = your_openai_api_key")
        print("5. Redeploy the service")
    elif result == True:
        print("\n✅ OpenAI integration is working correctly!")
    else:
        print("\n⚠️  Need to investigate further...")
