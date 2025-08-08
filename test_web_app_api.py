import requests
import json

# Test your API connection for the web app
API_BASE_URL = "https://cucov2-production.up.railway.app"

def test_api_endpoints():
    """Test all the endpoints your web app will use"""
    
    print("🧪 Testing API Connection for Web App")
    print("=" * 50)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
        else:
            print(f"❌ Health Check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
    
    # Test 2: Stats Endpoint (for Dashboard)
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats Endpoint: PASSED")
            print(f"   📊 Total Content: {data.get('totalContent', 0)}")
            print(f"   📝 Total Chunks: {data.get('totalChunks', 0)}")
        else:
            print(f"❌ Stats Endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Stats Endpoint: ERROR - {e}")
    
    # Test 3: Content List (for Content Manager)
    try:
        response = requests.get(f"{API_BASE_URL}/api/content/list", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Content List: PASSED")
            print(f"   📚 Documents: {data.get('total', 0)}")
        else:
            print(f"❌ Content List: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Content List: ERROR - {e}")
    
    # Test 4: Search Endpoint
    try:
        search_data = {
            "query": "protein structure",
            "filters": {"contentType": "all"}
        }
        response = requests.post(
            f"{API_BASE_URL}/api/content/search", 
            json=search_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Search Endpoint: PASSED")
            print(f"   🔍 Results: {data.get('total', 0)}")
        else:
            print(f"❌ Search Endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Search Endpoint: ERROR - {e}")
    
    # Test 5: Query Endpoint (main AI functionality)
    try:
        query_data = {"question": "What is protein structure?"}
        response = requests.post(
            f"{API_BASE_URL}/query", 
            json=query_data,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Query Endpoint: PASSED")
            print(f"   🤖 Answer Length: {len(data.get('answer', ''))}")
            print(f"   📖 Sources: {len(data.get('sources', []))}")
        else:
            print(f"❌ Query Endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Query Endpoint: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Test Complete!")
    print("\n📝 Next Steps:")
    print("1. Install Node.js from https://nodejs.org/")
    print("2. Restart VS Code after installation")
    print("3. Run: cd web-app && npm install")
    print("4. Run: npm run dev")
    print("5. Open http://localhost:3000")

if __name__ == "__main__":
    test_api_endpoints()
