#!/usr/bin/env python3
"""
Test script for the Question-Answering API
Tests if AI assistant can access and use ingested content
"""
import requests
import json
import time

def test_question_answering():
    """Test the /ask-question endpoint with content that should be in the knowledge base"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🧪 Testing Question-Answering Pipeline...")
    print("=" * 50)
    
    # First, ingest some test content to make sure we have something to query
    print("📤 Step 1: Ingesting test content...")
    
    ingest_payload = {
        "title": "Biology Cell Structure Test Content",
        "content": """
        Cell Structure and Function
        
        Cells are the basic units of life. There are two main types of cells:
        
        1. Prokaryotic Cells:
        - No membrane-bound nucleus
        - DNA freely floating in cytoplasm
        - Examples: bacteria, archaea
        - Simpler internal structure
        
        2. Eukaryotic Cells:
        - Membrane-bound nucleus containing DNA
        - Complex organelles like mitochondria, endoplasmic reticulum
        - Examples: plant cells, animal cells, fungi
        - More complex internal organization
        
        Key Organelles:
        - Nucleus: Controls cell activities, contains DNA
        - Mitochondria: Powerhouse of the cell, produces ATP energy
        - Ribosomes: Protein synthesis
        - Endoplasmic Reticulum: Transport system within cell
        - Golgi Apparatus: Processes and packages proteins
        
        Cell Membrane:
        The cell membrane is selectively permeable and controls what enters and exits the cell.
        It's made of a phospholipid bilayer with embedded proteins.
        """,
        "content_type": "biology_lesson",
        "source": "qa_test",
        "course_id": "BIOL101",
        "url": "https://test.canvas.edu/biology/cells"
    }
    
    try:
        ingest_response = requests.post(
            f"{base_url}/ingest-content", 
            json=ingest_payload, 
            timeout=30
        )
        
        if ingest_response.status_code == 200:
            ingest_result = ingest_response.json()
            print(f"✅ Content ingested: {ingest_result['status']}")
            print(f"   Content ID: {ingest_result['content_id']}")
        else:
            print(f"⚠️ Ingestion status: {ingest_response.status_code}")
            print(f"   Response: {ingest_response.text}")
            
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
    
    # Wait a moment for content to be processed
    print("\n⏳ Waiting for content processing...")
    time.sleep(3)
    
    # Now test question-answering
    print("\n❓ Step 2: Testing Question-Answering...")
    
    test_questions = [
        {
            "question": "What are the two main types of cells?",
            "expected_keywords": ["prokaryotic", "eukaryotic", "nucleus", "membrane"]
        },
        {
            "question": "What is the function of mitochondria?",
            "expected_keywords": ["powerhouse", "energy", "ATP", "cell"]
        },
        {
            "question": "What is the cell membrane made of?",
            "expected_keywords": ["phospholipid", "bilayer", "proteins", "selectively permeable"]
        },
        {
            "question": "Give me examples of prokaryotic cells",
            "expected_keywords": ["bacteria", "archaea"]
        }
    ]
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n🔍 Question {i}: {test_case['question']}")
        
        question_payload = {
            "question": test_case["question"],
            "course_id": "BIOL101"
        }
        
        try:
            qa_response = requests.post(
                f"{base_url}/ask-question",
                json=question_payload,
                timeout=30
            )
            
            print(f"   Status Code: {qa_response.status_code}")
            
            if qa_response.status_code == 200:
                qa_result = qa_response.json()
                
                print(f"   ✅ Answer received:")
                print(f"      {qa_result['answer'][:200]}{'...' if len(qa_result['answer']) > 200 else ''}")
                print(f"   📊 Confidence: {qa_result['confidence']}")
                print(f"   📚 Sources: {len(qa_result['sources'])} source(s)")
                print(f"   ⏱️ Response time: {qa_result['response_time']:.3f}s")
                
                # Check if answer contains expected keywords
                answer_lower = qa_result['answer'].lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] 
                                if kw.lower() in answer_lower]
                
                if found_keywords:
                    print(f"   🎯 Found keywords: {found_keywords}")
                else:
                    print(f"   ⚠️ Expected keywords not found: {test_case['expected_keywords']}")
                    
            else:
                print(f"   ❌ Error: {qa_response.text}")
                
        except Exception as e:
            print(f"   💥 Request failed: {e}")
    
    # Test edge cases
    print(f"\n🧪 Step 3: Testing Edge Cases...")
    
    edge_cases = [
        {"question": "hi", "description": "Too short question"},
        {"question": "What is quantum mechanics?", "description": "Question about unrelated topic"},
        {"question": "", "description": "Empty question"}
    ]
    
    for edge_case in edge_cases:
        print(f"\n🔍 Edge Case: {edge_case['description']}")
        print(f"   Question: '{edge_case['question']}'")
        
        try:
            edge_payload = {"question": edge_case["question"]}
            edge_response = requests.post(
                f"{base_url}/ask-question",
                json=edge_payload,
                timeout=15
            )
            
            print(f"   Status: {edge_response.status_code}")
            if edge_response.status_code == 200:
                edge_result = edge_response.json()
                print(f"   Response: {edge_result['answer'][:100]}...")
            else:
                print(f"   Error: {edge_response.text}")
                
        except Exception as e:
            print(f"   Failed: {e}")

if __name__ == "__main__":
    test_question_answering()
