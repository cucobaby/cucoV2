import requests
import json

# Test the improved API
API_URL = "https://cucov2-production.up.railway.app"

def test_protein_question():
    """Test the four levels of protein structure question"""
    
    print("🧪 Testing improved response system...")
    
    # Test the query
    query_data = {
        "question": "what are the four levels of protein structure"
    }
    
    try:
        print(f"📤 Sending query: {query_data['question']}")
        
        response = requests.post(
            f"{API_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS - Improved Response:")
            print("=" * 60)
            print(result['answer'])
            print("=" * 60)
            print(f"📚 Sources: {result.get('sources', [])}")
            print(f"🕐 Response Length: {len(result['answer'])} characters")
            
            # Check if it's concise (under 800 characters as target)
            if len(result['answer']) < 800:
                print("✅ Response is appropriately concise!")
            else:
                print("⚠️  Response might still be too long")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_protein_question()
