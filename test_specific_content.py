"""
Diagnostic tool to inspect the actual content stored in ChromaDB chunks
"""
import requests
import json

def test_specific_content():
    """Test what specific content chunks contain"""
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔍 Testing specific content retrieval...")
    print("=" * 60)
    
    # Test with very specific terms that should be in Study Guide 4
    specific_tests = [
        "primary secondary tertiary quaternary",
        "disulfide bridge", 
        "denaturation renaturation",
        "enzyme substrate",
        "Michaelis-Menten",
        "Study Guide 4",
        "Lectures 6-8",
        "cysteine disulfide",
        "alpha-helix beta-turn",
        "chaperonins"
    ]
    
    print("Testing specific terms from the study guide content...")
    
    for i, term in enumerate(specific_tests, 1):
        print(f"\n{i}. Testing: '{term}'")
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": f"Tell me about {term}"},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['answer']
                sources = len(data['sources'])
                
                if "cannot find" in answer.lower():
                    print(f"   ❌ Not found: {answer[:100]}...")
                else:
                    print(f"   ✅ Found: {answer[:150]}...")
                    print(f"   📊 Sources: {sources}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print(f"\n{'=' * 60}")

if __name__ == "__main__":
    test_specific_content()
