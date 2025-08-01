#!/usr/bin/env python3
"""
Direct database inspection to see what's actually stored
"""
import requests
import json

def inspect_database_contents():
    """Look at what's actually in the database"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔍 Direct Database Content Inspection")
    print("=" * 50)
    
    # Try to get more information about what's stored
    print("1. Testing very broad queries to see all content types...")
    
    broad_queries = [
        "show me everything",
        "all content",
        "any information", 
        "documents",
        "text"
    ]
    
    for query in broad_queries:
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": query},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📋 Query: '{query}'")
                print(f"   Sources: {len(result['sources'])}")
                print(f"   Answer length: {len(result['answer'])} chars")
                
                # Look for unique content patterns
                answer_lower = result['answer'].lower()
                
                if 'javascript enabled' in answer_lower:
                    print("   📄 Contains: JavaScript error content")
                if 'cell biology chapter' in answer_lower:
                    print("   📄 Contains: Cell Biology Chapter content")
                if 'mitochondria' in answer_lower:
                    print("   📄 Contains: Mitochondria content")
                if 'photosynthesis' in answer_lower:
                    print("   📄 Contains: Photosynthesis content")
                if 'learning objectives' in answer_lower:
                    print("   📄 Contains: Learning objectives content")
                
                # Show source IDs to see variety
                print(f"   🆔 Source IDs: {result['sources']}")
                
        except Exception as e:
            print(f"   💥 Error with '{query}': {e}")
    
    print(f"\n{'=' * 50}")
    print("2. Checking database health and document count...")
    
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"   📊 ChromaDB: {health['services']['chromadb']}")
        
        debug_response = requests.get(f"{base_url}/debug/chromadb", timeout=10)
        if debug_response.status_code == 200:
            debug = debug_response.json()
            print(f"   📁 Path: {debug.get('chroma_path', 'unknown')}")
            print(f"   📄 Canvas Collection: {debug.get('canvas_collection', 'unknown')}")
            
    except Exception as e:
        print(f"   💥 Health check error: {e}")
    
    print(f"\n{'=' * 50}")
    print("🎯 Analysis:")
    print("   If we only see Cell Biology + JavaScript content,")
    print("   then either:")
    print("   1. New content isn't being stored properly")
    print("   2. New content is stored but search can't find it")
    print("   3. The 🤖 button content is getting corrupted/filtered")

if __name__ == "__main__":
    inspect_database_contents()
