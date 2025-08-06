#!/usr/bin/env python3
"""
Test the new upload-content endpoint
"""
import requests
import json

def test_upload_endpoint():
    """Test the new JSON-based content upload endpoint"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Testing New Upload-Content Endpoint")
    print("=" * 50)
    
    # Test data (simulating Chrome extension upload)
    test_content = {
        "title": "Test Biology Content - Protein Structure",
        "content": """
        Protein Structure Levels:
        
        1. Primary Structure: The linear sequence of amino acids in a protein chain. This sequence is determined by the genetic code and forms the foundation for all higher levels of protein structure.
        
        2. Secondary Structure: Regular, recurring arrangements in space of adjacent amino acid residues in a polypeptide chain. The most common types are alpha helices and beta sheets, which are stabilized by hydrogen bonds.
        
        3. Tertiary Structure: The overall three-dimensional arrangement of all atoms in a protein. This structure is stabilized by various interactions including hydrogen bonds, ionic bonds, van der Waals forces, and disulfide bonds.
        
        4. Quaternary Structure: The arrangement of multiple polypeptide chains (subunits) in a multi-subunit protein. This level of structure only applies to proteins with more than one polypeptide chain.
        
        Each level builds upon the previous one, and all are crucial for proper protein function.
        """,
        "source": "test_script",
        "url": "https://test.com/biology",
        "content_type": "educational_content",
        "timestamp": "2025-08-06T05:00:00Z"
    }
    
    try:
        print("📤 Sending test upload...")
        print(f"   Title: {test_content['title']}")
        print(f"   Content Length: {len(test_content['content'])} characters")
        
        response = requests.post(
            f"{base_url}/upload-content",
            json=test_content,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS - Upload Response:")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Content ID: {result.get('content_id')}")
            print(f"   Chunks Created: {result.get('chunks_created')}")
            
            # Test query to verify upload worked
            print("\n🔍 Testing Query Against Uploaded Content...")
            
            query_response = requests.post(
                f"{base_url}/query",
                json={"question": "what are the four levels of protein structure"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if query_response.status_code == 200:
                query_result = query_response.json()
                print("✅ Query Test SUCCESS:")
                print(f"   Answer Length: {len(query_result.get('answer', ''))} characters")
                print(f"   Answer Preview: {query_result.get('answer', '')[:200]}...")
                print(f"   Sources: {len(query_result.get('sources', []))}")
            else:
                print(f"❌ Query Test Failed: {query_response.status_code}")
                print(f"   Response: {query_response.text[:200]}...")
                
        elif response.status_code == 422:
            print("❌ HTTP 422 - Validation Error:")
            try:
                error_detail = response.json()
                print(f"   Error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Raw Response: {response.text}")
        else:
            print(f"❌ Upload Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - server may be slow")
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_upload_endpoint()
