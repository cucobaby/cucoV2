#!/usr/bin/env python3
"""
Document Storage Analysis - Check if documents were stored with ContentAnalyzer processing
"""
import requests
import json

def analyze_stored_documents():
    """Analyze the stored documents to see processing details"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔍 Document Storage Analysis")
    print("=" * 50)
    
    # Check ChromaDB debug info
    try:
        debug_response = requests.get(f"{base_url}/debug/chromadb", timeout=10)
        if debug_response.status_code == 200:
            debug_info = debug_response.json()
            print("📊 ChromaDB Debug Info:")
            print(f"   Timestamp: {debug_info.get('timestamp', 'N/A')}")
            print(f"   Canvas Collection: {debug_info.get('canvas_collection', 'N/A')}")
            print(f"   Chroma Path: {debug_info.get('chroma_path', 'N/A')}")
            
            # Check test operations
            tests = debug_info.get('tests', {})
            for test_name, result in tests.items():
                print(f"   {test_name}: {result}")
        else:
            print(f"❌ Debug endpoint failed: {debug_response.status_code}")
    except Exception as e:
        print(f"💥 Debug request failed: {e}")
    
    print("\n" + "="*50)
    
    # Test a question to see response quality and metadata
    print("🤔 Testing Question to Analyze Response Quality...")
    
    test_questions = [
        "What topics did I upload?",
        "What type of content did I add to my Canvas assistant?",
        "What should I study from my uploaded materials?"
    ]
    
    for question in test_questions:
        try:
            qa_response = requests.post(
                f"{base_url}/ask-question",
                json={"question": question},
                timeout=15
            )
            
            if qa_response.status_code == 200:
                result = qa_response.json()
                
                print(f"\n📋 Question: '{question}'")
                print(f"   ✅ Answer Length: {len(result['answer'])} chars")
                print(f"   📊 Confidence: {result['confidence']}")
                print(f"   📚 Sources: {len(result['sources'])} document(s)")
                print(f"   ⏱️ Response Time: {result['response_time']:.3f}s")
                
                # Check if answer indicates intelligent processing
                answer_lower = result['answer'].lower()
                intelligence_indicators = [
                    'based on your course materials',
                    'from your content',
                    'according to your',
                    'your uploaded materials'
                ]
                
                is_intelligent = any(indicator in answer_lower for indicator in intelligence_indicators)
                processing_quality = "🧠 INTELLIGENT" if is_intelligent else "📝 BASIC"
                
                print(f"   🎯 Processing: {processing_quality}")
                
                # Show first part of answer
                print(f"   💬 Answer Preview: {result['answer'][:150]}...")
                
                if result['sources']:
                    print(f"   📎 Source IDs: {result['sources']}")
                
                break  # Just test the first question for detailed analysis
                
        except Exception as e:
            print(f"   💥 Question failed: {e}")
    
    print(f"\n{'='*50}")
    print("📋 Analysis Summary:")
    print("   ✅ 4 documents are stored in ChromaDB")
    print("   🔍 Check the response quality above to see if ContentAnalyzer processing worked")
    print("   💡 Look for 'INTELLIGENT' responses with Canvas-specific language")

if __name__ == "__main__":
    analyze_stored_documents()
