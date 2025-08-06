#!/usr/bin/env python3
"""
Clear all documents from knowledge base and verify clean state
"""
import requests

def clear_and_verify():
    """Clear all documents and verify the system is clean"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🗑️ Clearing Knowledge Base")
    print("=" * 50)
    
    # Step 1: Check current state
    print("📊 Checking current state...")
    try:
        debug_response = requests.get(f"{base_url}/debug/chromadb", timeout=10)
        if debug_response.status_code == 200:
            debug_info = debug_response.json()
            print(f"   Current documents: {debug_info.get('canvas_collection', 'Unknown')}")
        else:
            print(f"   Debug check failed: {debug_response.status_code}")
    except Exception as e:
        print(f"   Debug check error: {e}")
    
    # Step 2: Clear all documents
    print("\n🗑️ Clearing all documents...")
    try:
        clear_response = requests.delete(f"{base_url}/clear-documents", timeout=15)
        
        if clear_response.status_code == 200:
            result = clear_response.json()
            print("   ✅ SUCCESS!")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print(f"   Documents Removed: {result['documents_removed']}")
        else:
            print("   ❌ FAILED!")
            print(f"   Status: {clear_response.status_code}")
            print(f"   Response: {clear_response.text}")
            
    except Exception as e:
        print(f"   💥 Clear error: {e}")
    
    # Step 3: Verify clean state
    print("\n🔍 Verifying clean state...")
    try:
        debug_response = requests.get(f"{base_url}/debug/chromadb", timeout=10)
        if debug_response.status_code == 200:
            debug_info = debug_response.json()
            canvas_collection = debug_info.get('canvas_collection', '')
            
            if 'Found with 0 documents' in canvas_collection or 'Error:' in canvas_collection:
                print("   ✅ Knowledge base is now clean!")
            else:
                print(f"   ⚠️ Still has documents: {canvas_collection}")
                
            print(f"   Path exists: {debug_info.get('path_exists', False)}")
            print(f"   Test query: {debug_info.get('test_query', 'N/A')}")
        else:
            print(f"   Debug check failed: {debug_response.status_code}")
    except Exception as e:
        print(f"   Verification error: {e}")
    
    # Step 4: Test question with empty knowledge base
    print("\n🧪 Testing question with empty knowledge base...")
    try:
        qa_response = requests.post(
            f"{base_url}/ask-question",
            json={"question": "what are the levels of protein structure"},
            timeout=15
        )
        
        if qa_response.status_code == 200:
            result = qa_response.json()
            print("   ✅ Question processed successfully")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Sources: {len(result['sources'])}")
            print(f"   Answer preview: {result['answer'][:100]}...")
            
            if result['confidence'] == 0.0 and len(result['sources']) == 0:
                print("   🎯 Perfect! System correctly shows no content available")
            else:
                print("   ⚠️ Unexpected - system should show no content available")
        else:
            print(f"   ❌ Question test failed: {qa_response.status_code}")
            
    except Exception as e:
        print(f"   Question test error: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 Knowledge Base Reset Complete!")
    print("   Ready for fresh upload of your course materials")

if __name__ == "__main__":
    clear_and_verify()
