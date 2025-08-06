#!/usr/bin/env python3
"""
Analyze search results for protein structure questions
"""
import requests
import json

def analyze_search_quality():
    """Test different search strategies for protein structure content"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    # Test different search queries
    test_queries = [
        "levels of protein structure",
        "protein structure primary secondary tertiary quaternary", 
        "amino acid sequence protein folding",
        "protein structure",
        "primary structure",
        "secondary structure alpha helix beta sheet",
        "tertiary structure protein folding",
        "quaternary structure"
    ]
    
    print("🔍 Search Quality Analysis")
    print("=" * 60)
    
    for query in test_queries:
        try:
            # Use the internal search to see what content is found
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": query},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                sources = result.get('sources', [])
                
                print(f"\n📋 Query: '{query}'")
                print(f"   📚 Sources Found: {len(sources)}")
                print(f"   📊 Confidence: {result['confidence']}")
                
                # Show what content was actually retrieved
                if sources:
                    for i, source in enumerate(sources[:2]):  # Show first 2 sources
                        print(f"   📄 Source {i+1}: {source.get('title', 'Unknown')}")
                        content_preview = source.get('content', '')[:200]
                        print(f"      Content: {content_preview}...")
                else:
                    print("   ❌ No sources found")
                    
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Query error: {e}")
    
    print(f"\n{'='*60}")
    print("🎯 Search Analysis Complete")

if __name__ == "__main__":
    analyze_search_quality()
