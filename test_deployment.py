import requests
import json

def test_deployment():
    """Test if the formatting improvements are deployed"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    # Test 1: Basic health check
    print("🔍 Testing deployment status...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ API Status: {response.json()}")
    except Exception as e:
        print(f"❌ API Status Error: {e}")
        return
    
    # Test 2: Check if we have content in the database
    print("\n📊 Testing database content...")
    try:
        response = requests.get(f"{base_url}/list-documents")
        doc_info = response.json()
        print(f"✅ Database has {doc_info.get('count', 0)} documents")
        if doc_info.get('documents'):
            for doc in doc_info['documents'][:3]:  # Show first 3
                print(f"   - {doc.get('title', 'Unknown')} ({doc.get('chunk_count', 0)} chunks)")
    except Exception as e:
        print(f"❌ Database check error: {e}")
    
    # Test 3: Test the enhanced formatting with a biology question
    print("\n🧬 Testing enhanced formatting with 'explain glycolysis'...")
    try:
        test_question = {"question": "explain glycolysis"}
        
        # Test parsed endpoint
        response = requests.post(
            f"{base_url}/query-parsed",
            json=test_question,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Parsed Response Structure:")
            print(f"   📝 Title: {result.get('title', 'Not found')}")
            print(f"   🎯 Learning Objective: {result.get('learning_objective', 'Not found')}")
            print(f"   📊 Study Info: {result.get('study_info', 'Not found')}")
            print(f"   📋 Quick Summary: {len(result.get('quick_summary', ''))} chars")
            print(f"   🔍 Definition: {len(result.get('definition_overview', ''))} chars")
            print(f"   🔬 Key Concepts: {len(result.get('key_concepts', []))} items")
            print(f"   💡 Key Terms: {len(result.get('key_terms', []))} items")
            print(f"   🤔 Think About: {len(result.get('think_about', []))} items")
            print(f"   🔗 Related Topics: {len(result.get('related_topics', []))} items")
            print(f"   📚 Sources: {result.get('sources', [])}")
            
            # Check if we have proper formatting
            if result.get('title') and result.get('learning_objective'):
                print("🎉 Enhanced formatting is DEPLOYED and working!")
            else:
                print("⚠️ Enhanced formatting structure not detected")
                
        else:
            print(f"❌ Query failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Query test error: {e}")
    
    # Test 4: Test regular endpoint for comparison
    print("\n📝 Testing regular endpoint...")
    try:
        response = requests.post(
            f"{base_url}/query",
            json={"question": "explain glycolysis"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            answer_length = len(result.get('answer', ''))
            print(f"✅ Regular endpoint: {answer_length} char response")
            
            # Check if the answer contains enhanced formatting elements
            answer = result.get('answer', '')
            has_emojis = any(emoji in answer for emoji in ['🧬', '📚', '🎯', '🔍', '💡'])
            has_sections = '##' in answer and 'Learning Objective' in answer
            
            if has_emojis and has_sections:
                print("✅ Enhanced formatting detected in regular response!")
            else:
                print("⚠️ Enhanced formatting not detected in regular response")
        else:
            print(f"❌ Regular query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Regular query error: {e}")

if __name__ == "__main__":
    test_deployment()
