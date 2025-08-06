#!/usr/bin/env python3
"""
Test the restored upload endpoint
"""
import requests

def test_upload():
    """Test uploading biology content"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    # Sample biology content about protein structure
    test_content = {
        "title": "Biology Study Guide - Protein Structure",
        "content": """Protein Structure Levels:

Primary Structure: The amino acid sequence of a protein chain. This is the most basic level and determines all higher structural levels.

Secondary Structure: Regular folding patterns including:
- Alpha helixes: spiral structures stabilized by hydrogen bonds
- Beta sheets: extended structures with parallel or antiparallel chains

Tertiary Structure: The overall 3D folding of a single protein chain. Determined by interactions between R-groups of amino acids.

Quaternary Structure: The arrangement of multiple protein subunits. Not all proteins have quaternary structure - only those with multiple polypeptide chains.

Key Points:
- Primary structure is the foundation for all other levels
- Hydrogen bonds are important in secondary structure
- Tertiary structure involves R-group interactions
- Quaternary structure involves multiple chains""",
        "content_type": "study_guide",
        "source": "test_upload"
    }
    
    print("🧪 Testing Upload Endpoint")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{base_url}/upload-content",
            json=test_content,
            timeout=15
        )
        
        print(f"📤 Upload Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Message: {result['message']}")
            print(f"   Document Count: {result['document_count']}")
            print(f"   Total Documents: {result['total_documents']}")
        else:
            print("❌ FAILED!")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")
    
    print(f"\n{'='*50}")

if __name__ == "__main__":
    test_upload()
