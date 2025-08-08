import requests

print("🧪 Testing Glycolysis Query")
print("=" * 40)

try:
    response = requests.post(
        "https://cucov2-production.up.railway.app/query",
        json={"question": "what is glycolysis"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        answer = result['answer']
        
        print("📝 Response Length:", len(answer), "characters")
        print("📚 Sources:", result.get('sources', []))
        
        print("\n🔍 RAW CONTENT (with escape chars):")
        print("=" * 50)
        print(repr(answer[:600]))
        print("=" * 50)
        
        print("\n📄 FORMATTED CONTENT:")
        print("=" * 50)
        print(answer)
        print("=" * 50)
        
        # Analysis
        line_breaks = answer.count('\n')
        double_breaks = answer.count('\n\n')
        print(f"\n📊 ANALYSIS:")
        print(f"   Line breaks (\\n): {line_breaks}")
        print(f"   Double breaks (\\n\\n): {double_breaks}")
        print(f"   Has sections (##): {'##' in answer}")
        print(f"   Has learning objective: {'Learning Objective' in answer}")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Failed: {e}")
