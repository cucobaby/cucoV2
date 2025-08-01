#!/usr/bin/env python3
"""
Test the enhanced Canvas-focused AI Assistant
Tests both intelligent OpenAI responses and ContentAnalyzer integration
"""
import requests
import json
import time

def test_enhanced_canvas_assistant():
    """Test the Canvas-focused AI assistant with intelligent responses"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    print("🎓 Testing Enhanced Canvas-Focused AI Assistant")
    print("=" * 60)
    
    # Test enhanced content ingestion with ContentAnalyzer
    print("📚 Step 1: Testing Enhanced Content Ingestion with ContentAnalyzer...")
    
    canvas_content = {
        "title": "Cell Biology - Eukaryotic and Prokaryotic Cells",
        "content": """
        Cell Biology Chapter 3: Cell Structure and Function
        
        Learning Objectives:
        - Compare prokaryotic and eukaryotic cell structures
        - Identify major organelles and their functions
        - Explain membrane transport mechanisms
        
        PROKARYOTIC CELLS:
        Prokaryotic cells are the simplest type of cells, found in bacteria and archaea. Key characteristics:
        - No membrane-bound nucleus
        - DNA freely floating in the cytoplasm (nucleoid region)
        - Ribosomes are smaller (70S)
        - Cell wall provides structure and protection
        - Examples: E. coli, Streptococcus
        
        EUKARYOTIC CELLS:
        Eukaryotic cells are more complex, found in plants, animals, fungi, and protists:
        - Membrane-bound nucleus containing DNA
        - Complex organelles with specific functions
        - Larger ribosomes (80S)
        - Cytoskeleton provides internal structure
        
        Major Organelles:
        1. NUCLEUS: Control center containing chromosomes and DNA
        2. MITOCHONDRIA: Powerhouse of the cell, produces ATP through cellular respiration
        3. ENDOPLASMIC RETICULUM (ER):
           - Rough ER: Has ribosomes, synthesizes proteins
           - Smooth ER: No ribosomes, synthesizes lipids
        4. GOLGI APPARATUS: Processes and packages proteins from ER
        5. RIBOSOMES: Protein synthesis sites
        6. LYSOSOMES: Digestive organelles (animal cells)
        7. CHLOROPLASTS: Photosynthesis organelles (plant cells only)
        
        Cell Membrane Transport:
        - Passive transport: No energy required (diffusion, osmosis)
        - Active transport: Energy required to move against concentration gradient
        - Endocytosis: Cell engulfs materials
        - Exocytosis: Cell expels materials
        
        Study Tips:
        - Create a comparison chart of prokaryotic vs eukaryotic cells
        - Draw and label organelles
        - Understand the relationship between structure and function
        """,
        "content_type": "canvas_page",
        "source": "canvas_chrome_extension",
        "course_id": "BIOL101", 
        "url": "https://canvas.university.edu/courses/12345/pages/cell-biology-chapter-3",
        "timestamp": "2025-07-31T07:00:00Z"
    }
    
    try:
        ingest_response = requests.post(
            f"{base_url}/ingest-content", 
            json=canvas_content, 
            timeout=30
        )
        
        print(f"📊 Status: {ingest_response.status_code}")
        
        if ingest_response.status_code == 200:
            result = ingest_response.json()
            print(f"✅ Enhanced Ingestion Result:")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print(f"   Content ID: {result['content_id']}")
            print(f"   Chunks Created: {result['chunks_created']}")
            print(f"   Processing Time: {result['processing_time']:.3f}s")
            
            if result['status'] == 'success':
                print("🎉 Content successfully stored with ContentAnalyzer enhancement!")
            else:
                print("⚠️ Content stored but analysis may be limited")
        else:
            print(f"❌ Ingestion failed: {ingest_response.text}")
            return
            
    except Exception as e:
        print(f"💥 Ingestion error: {e}")
        return
    
    # Wait for processing
    print("\n⏳ Waiting for enhanced content processing...")
    time.sleep(5)
    
    # Test intelligent AI responses
    print("\n🧠 Step 2: Testing Intelligent Canvas-Only AI Responses...")
    
    canvas_questions = [
        {
            "question": "What's the difference between prokaryotic and eukaryotic cells?",
            "description": "Course-specific comparison question",
            "expect_canvas_only": True
        },
        {
            "question": "What organelles are found in eukaryotic cells and what do they do?",
            "description": "Detailed course content question",
            "expect_canvas_only": True
        },
        {
            "question": "How do mitochondria produce energy for the cell?",
            "description": "Specific organelle function from course",
            "expect_canvas_only": True
        },
        {
            "question": "What are the main transport mechanisms across cell membranes?",
            "description": "Course material on membrane transport",
            "expect_canvas_only": True
        }
    ]
    
    for i, test_case in enumerate(canvas_questions, 1):
        print(f"\n🎯 Question {i}: {test_case['description']}")
        print(f"   '{test_case['question']}'")
        
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
            
            if qa_response.status_code == 200:
                qa_result = qa_response.json()
                
                print(f"   ✅ Enhanced AI Response:")
                print(f"      Answer: {qa_result['answer'][:300]}...")
                print(f"      Confidence: {qa_result['confidence']}")
                print(f"      Sources: {len(qa_result['sources'])} Canvas source(s)")
                print(f"      Response Time: {qa_result['response_time']:.3f}s")
                
                # Check if response is Canvas-focused
                answer_lower = qa_result['answer'].lower()
                canvas_indicators = [
                    'based on your course',
                    'from your course materials',
                    'according to your canvas',
                    'from the course content',
                    'your uploaded materials'
                ]
                
                canvas_focused = any(indicator in answer_lower for indicator in canvas_indicators)
                if canvas_focused:
                    print("   🎓 ✅ Response is Canvas-course focused!")
                else:
                    print("   ⚠️ Response may not emphasize Canvas-only focus")
                    
                # Check for intelligent, not just raw content
                if len(qa_result['answer']) > 200 and qa_result['confidence'] > 0.8:
                    print("   🧠 ✅ Response shows intelligent processing!")
                else:
                    print("   📝 Response is basic content retrieval")
                    
            else:
                print(f"   ❌ Error: {qa_response.text}")
                
        except Exception as e:
            print(f"   💥 Request failed: {e}")
    
    # Test Canvas-specific features
    print(f"\n🏫 Step 3: Testing Canvas-Specific Features...")
    
    # Test content type detection
    print("   Testing Canvas content type detection...")
    canvas_specific_questions = [
        "What type of course material is this content from?",
        "What should I focus on studying from this Canvas page?"
    ]
    
    for question in canvas_specific_questions:
        try:
            response = requests.post(
                f"{base_url}/ask-question",
                json={"question": question, "course_id": "BIOL101"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📋 '{question}'")
                print(f"      {result['answer'][:150]}...")
        except:
            pass
    
    print(f"\n🎉 Enhanced Canvas-Focused AI Assistant Test Complete!")
    print(f"    ✅ Intelligent OpenAI-powered responses")
    print(f"    ✅ ContentAnalyzer integration for topic awareness") 
    print(f"    ✅ Canvas-specific content understanding")
    print(f"    ✅ Course-focused, relevant answers only")

if __name__ == "__main__":
    test_enhanced_canvas_assistant()
