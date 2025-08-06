#!/usr/bin/env python3
"""
Quick test script to verify OpenAI client initialization fix
"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_openai_client():
    """Test OpenAI client initialization"""
    try:
        import openai
        
        # Test with dummy API key
        os.environ["OPENAI_API_KEY"] = "sk-test123"
        
        print("Testing OpenAI client initialization...")
        
        # This should not fail on client creation anymore
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ OpenAI client initialized successfully!")
        
        # Test the actual call (will fail due to fake key, but client creation should work)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            print("✅ API call successful (unexpected with test key)")
        except Exception as api_error:
            if "api key" in str(api_error).lower() or "unauthorized" in str(api_error).lower():
                print("✅ Client works - API key error as expected")
            else:
                print(f"❌ Unexpected API error: {api_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
        return False

if __name__ == "__main__":
    print("OpenAI Client Test")
    print("=" * 20)
    test_openai_client()
