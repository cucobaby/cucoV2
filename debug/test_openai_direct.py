#!/usr/bin/env python3
"""
Direct OpenAI integration test to identify the exact issue
"""
import os
import requests
import json

def test_openai_direct():
    """Test OpenAI integration directly"""
    
    print("🔍 Testing OpenAI Integration")
    print("=" * 40)
    
    # Test 1: Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OPENAI_API_KEY environment variable found")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test 2: Check if openai module can be imported
    try:
        import openai
        print("✅ OpenAI module imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI module import failed: {e}")
        return False
    
    # Test 3: Test client initialization
    try:
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
    except Exception as e:
        print(f"❌ OpenAI client initialization failed: {e}")
        return False
    
    # Test 4: Test simple API call
    try:
        print("🔄 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful: '{result}'")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Detailed error analysis
        error_str = str(e).lower()
        if "api key" in error_str or "unauthorized" in error_str:
            print("🔍 Issue: Invalid API key")
        elif "quota" in error_str or "billing" in error_str:
            print("🔍 Issue: API quota exceeded or billing problem")  
        elif "rate limit" in error_str:
            print("🔍 Issue: Rate limit exceeded")
        elif "network" in error_str or "connection" in error_str:
            print("🔍 Issue: Network connectivity problem")
        else:
            print(f"🔍 Unknown issue: {e}")
        
        return False

def test_railway_environment():
    """Test the deployed Railway environment"""
    print("\n🌐 Testing Railway Environment")
    print("=" * 40)
    
    try:
        # Test query endpoint with logging
        url = "https://cucov2-production.up.railway.app/query"
        data = {"question": "test openai integration"}
        
        print(f"🔄 Sending request to: {url}")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            if 'OpenAI' in answer and 'error' in answer:
                print(f"❌ OpenAI error detected in response: {answer[:200]}...")
            elif 'fallback' in answer.lower() or 'compiled directly' in answer:
                print("⚠️  Using fallback response - OpenAI integration failed")
            else:
                print("✅ Appears to be using OpenAI successfully")
                
            print(f"📝 Response preview: {answer[:150]}...")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Railway test failed: {e}")

if __name__ == "__main__":
    # Test local environment
    local_success = test_openai_direct()
    
    # Test Railway deployment
    test_railway_environment()
    
    print(f"\n🏁 Local OpenAI test: {'✅ PASSED' if local_success else '❌ FAILED'}")
