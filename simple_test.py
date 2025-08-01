#!/usr/bin/env python3
"""
Simple focused test for Canvas AI Assistant content ingestion
"""
import requests
import json
import time

def test_content_ingestion_only():
    """Test just the content ingestion to verify it works"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Simple Content Ingestion Test")
    print("=" * 40)
    
    # Simple biology content
    test_content = {
        "title": "Biology Test Content",
        "content": "Mitochondria are the powerhouse of the cell. They produce ATP through cellular respiration.",
        "content_type": "canvas_page",
        "source": "canvas_chrome_extension",
        "course_id": "BIOL101", 
        "url": "https://canvas.university.edu/test",
        "timestamp": "2025-07-31T07:00:00Z"
    }
    
    print("📝 Submitting content...")
    
    try:
        response = requests.post(
            f"{base_url}/ingest-content", 
            json=test_content, 
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Result: {result}")
            
            if 'content_id' in result:
                print("🎉 Content successfully ingested!")
                
                # Wait a moment
                time.sleep(3)
                
                # Test a simple question
                print("\n🤔 Testing simple question...")
                question_response = requests.post(
                    f"{base_url}/ask-question",
                    json={"question": "What are mitochondria?", "course_id": "BIOL101"},
                    timeout=15
                )
                
                if question_response.status_code == 200:
                    qa_result = question_response.json()
                    print(f"✅ Answer: {qa_result['answer'][:200]}...")
                    print(f"Confidence: {qa_result['confidence']}")
                    print(f"Sources: {len(qa_result['sources'])}")
                else:
                    print(f"❌ Question failed: {question_response.text}")
            
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_content_ingestion_only()
