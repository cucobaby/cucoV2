#!/usr/bin/env python3
"""
Simulate fixing the Chrome extension content capture issue
"""
import requests
import json
from datetime import datetime

def simulate_proper_content_upload():
    """Test uploading proper content to verify the pipeline works"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🔧 Testing Proper Content Upload (Simulating Fixed Chrome Extension)")
    print("=" * 70)
    
    # Simulate what the Chrome extension SHOULD be sending
    proper_content = {
        "title": "Test Canvas Page - Proper Content Capture",
        "content": """
        Canvas Assignment: Research Methods in Biology
        
        Instructions:
        Complete a research project on one of the following topics:
        1. Gene expression analysis using PCR techniques
        2. Microscopic examination of plant cell structures  
        3. Enzyme kinetics in metabolic pathways
        
        Requirements:
        - 5-page research paper
        - Include at least 3 peer-reviewed sources
        - Discuss methodology and findings
        - Due date: Next Friday
        
        Grading Rubric:
        - Content accuracy: 40%
        - Scientific method application: 30% 
        - Writing quality: 20%
        - Citations: 10%
        
        Resources:
        - Lab manual Chapter 7
        - Online database access via library
        - Office hours: Tuesdays 2-4 PM
        """,
        "content_type": "canvas_assignment",
        "source": "canvas_chrome_extension_fixed",
        "course_id": "BIOL_301", 
        "url": "https://canvas.university.edu/courses/123/assignments/456",
        "timestamp": datetime.now().isoformat()
    }
    
    print("📤 Uploading proper Canvas content...")
    
    try:
        response = requests.post(
            f"{base_url}/ingest-content",
            json=proper_content,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Status: {result['status']}")
            print(f"   Content ID: {result['content_id']}")
            print(f"   Chunks: {result['chunks_created']}")
            
            # Test if this content is now accessible
            print(f"\n🧪 Testing accessibility of new content...")
            
            test_questions = [
                "What assignment do I have in biology?",
                "When is my research project due?", 
                "What are the grading criteria?",
                "What topics can I research?"
            ]
            
            for question in test_questions:
                try:
                    qa_response = requests.post(
                        f"{base_url}/ask-question",
                        json={"question": question},
                        timeout=10
                    )
                    
                    if qa_response.status_code == 200:
                        qa_result = qa_response.json()
                        
                        answer_lower = qa_result['answer'].lower()
                        
                        # Check if it found the new content
                        if any(word in answer_lower for word in ['research', 'assignment', 'friday', 'biology']):
                            print(f"   ✅ '{question}' → Found NEW content!")
                        elif 'mitochondria' in answer_lower or 'cell biology chapter' in answer_lower:
                            print(f"   ❌ '{question}' → Still returning OLD content")
                        else:
                            print(f"   ❓ '{question}' → Unknown content type")
                            
                except Exception as e:
                    print(f"   💥 Question failed: {e}")
                    
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"💥 Upload error: {e}")
    
    print(f"\n{'=' * 70}")
    print("🔍 Diagnosis:")
    print("   If the NEW content is accessible, the pipeline works fine.")
    print("   The issue is the Chrome extension capturing JavaScript errors")
    print("   instead of actual Canvas page content.")
    print("   ")
    print("   💡 Solution: Fix Chrome extension content detection!")

if __name__ == "__main__":
    simulate_proper_content_upload()
