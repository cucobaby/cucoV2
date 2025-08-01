#!/usr/bin/env python3
"""
Diagnose and improve the ChromaDB search quality
"""
import requests
import json

def diagnose_search_quality():
    """Test different search strategies to improve content retrieval"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔍 ChromaDB Search Quality Diagnosis")
    print("=" * 50)
    
    # Test different types of queries to understand what's stored
    test_queries = [
        # Very general queries
        {"query": "content", "description": "General content search"},
        {"query": "biology", "description": "Subject-specific search"},
        {"query": "study guide", "description": "Content type search"},
        
        # Specific content queries  
        {"query": "photosynthesis calvin cycle", "description": "Specific topic search"},
        {"query": "ATP glucose energy", "description": "Key terms search"},
        {"query": "cellular respiration mitochondria", "description": "Process search"},
        
        # Learning-focused queries
        {"query": "learning objectives", "description": "Learning goals search"},
        {"query": "vocabulary terms definitions", "description": "Definitions search"},
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test['description']}")
        print(f"   Query: '{test['query']}'")
        
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": test["query"]},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Response received")
                print(f"   📊 Confidence: {result['confidence']}")
                print(f"   📚 Sources: {len(result['sources'])}")
                print(f"   ⏱️ Time: {result['response_time']:.3f}s")
                
                # Analyze what content is being returned
                answer_preview = result['answer'][:200].replace('\n', ' ')
                print(f"   📄 Content: {answer_preview}...")
                
                # Check if it's returning the old test content vs new content
                if 'mitochondria are the powerhouse' in result['answer'].lower():
                    print(f"   ⚠️ Content: OLD TEST CONTENT (cell biology)")
                elif 'calvin cycle' in result['answer'].lower() or 'chloroplast' in result['answer'].lower():
                    print(f"   ✅ Content: NEW PHOTOSYNTHESIS CONTENT")
                elif 'cell biology chapter 3' in result['answer'].lower():
                    print(f"   ⚠️ Content: OLD TEST CONTENT (chapter 3)")
                else:
                    print(f"   ❓ Content: UNKNOWN TYPE")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print(f"\n{'=' * 50}")
    print("📋 Analysis:")
    print("   If most queries return 'OLD TEST CONTENT', the vector search")
    print("   is finding the wrong documents. We need to:")
    print("   1. Improve the vector search ranking")
    print("   2. Clear old test content") 
    print("   3. Ensure new content has better embeddings")

if __name__ == "__main__":
    diagnose_search_quality()
