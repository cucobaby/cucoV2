#!/usr/bin/env python3
"""
Force upload the photosynthesis study guide content to ensure it's properly stored
"""
import requests
import json
from datetime import datetime

def force_upload_study_guide():
    """Upload the photosynthesis study guide content directly"""
    
    # The content from your study guide file
    photosynthesis_content = """
Biology: Photosynthesis Study Guide

Learning Objectives:
1. Explain the process of photosynthesis, including the role of chlorophyll, the two main stages involved, and the products generated.
2. Compare and contrast aerobic and anaerobic respiration, highlighting the differences in ATP production and the presence of oxygen.
3. Analyze the relationship between the Calvin cycle and the light-dependent reactions in photosynthesis, focusing on the utilization of ATP and NADPH.
4. Calculate the ATP yield from the complete metabolism of glucose, considering the ATP produced in glycolysis, the citric acid cycle, and the electron transport chain.
5. Describe the function of mitochondria in cellular respiration and the specific locations within the mitochondria where each stage occurs.
6. Identify the key role of enzymes in both photosynthesis and cellular respiration, explaining how they facilitate biochemical reactions.
7. Evaluate the importance of the electron transport chain in generating ATP during cellular respiration, emphasizing the role of NADH and FADH2.
8. Apply the concept of energy conversion in living organisms by explaining how photosynthesis and cellular respiration form a cycle of energy and matter in ecosystems.

Photosynthesis:
Process by which plants convert light energy into chemical energy stored in glucose. This process occurs in two main stages: the light-dependent reactions and the Calvin cycle.

The light-dependent reactions occur in the thylakoid membranes of chloroplasts. Here, chlorophyll absorbs light energy and uses it to split water molecules, releasing oxygen as a byproduct. The energy is captured in ATP and NADPH molecules.

The Calvin cycle takes place in the stroma of chloroplasts. This cycle uses CO2 from the atmosphere, along with ATP and NADPH from the light reactions, to produce glucose through a series of enzyme-catalyzed reactions.

Cellular Respiration:
Process by which cells break down glucose to release energy in the form of ATP. This process occurs in three main stages: glycolysis, the citric acid cycle, and the electron transport chain.

Glycolysis occurs in the cytoplasm and partially breaks down glucose into pyruvate, producing a small amount of ATP and NADH. The citric acid cycle occurs in the mitochondrial matrix and completes the breakdown of glucose derivatives, producing more NADH, FADH2, and ATP.

The electron transport chain is located in the inner mitochondrial membrane. It uses the NADH and FADH2 produced in earlier stages to generate a large amount of ATP through oxidative phosphorylation.

Key Vocabulary:
- ATP: Adenosine triphosphate, the energy currency of cells
- Chloroplast: Organelle where photosynthesis occurs in plant cells
- Mitochondria: Organelle where cellular respiration occurs
- Glucose: A simple sugar that serves as a primary energy source
- NADH: An electron carrier molecule
- Enzyme: Proteins that catalyze biochemical reactions
- Calvin cycle: The light-independent reactions of photosynthesis that produce glucose
- Chlorophyll: The pigment that absorbs light energy in photosynthesis
- Thylakoid: Membrane structures in chloroplasts where light reactions occur
- Stroma: The fluid-filled space in chloroplasts where the Calvin cycle occurs

The relationship between photosynthesis and cellular respiration creates a cycle of energy and matter in ecosystems. Plants use photosynthesis to convert solar energy into chemical energy, while both plants and animals use cellular respiration to extract that energy for cellular processes.
"""

    # Prepare the upload request
    upload_data = {
        "title": "Biology Photosynthesis Study Guide - Force Upload",
        "content": photosynthesis_content,
        "content_type": "canvas_study_guide",
        "source": "direct_upload_fix",
        "course_id": "BIOLOGY_PHOTOSYNTHESIS", 
        "url": "https://canvas.university.edu/study-guide/photosynthesis",
        "timestamp": datetime.now().isoformat()
    }
    
    print("🔄 Force uploading photosynthesis study guide...")
    
    try:
        response = requests.post(
            "https://cucov2-production.up.railway.app/ingest-content",
            json=upload_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print(f"   Content ID: {result['content_id']}")
            print(f"   Chunks Created: {result['chunks_created']}")
            print(f"   Processing Time: {result['processing_time']:.3f}s")
            
            # Test immediately
            print("\n🤔 Testing photosynthesis question...")
            
            test_response = requests.post(
                "https://cucov2-production.up.railway.app/ask-question",
                json={"question": "Explain the Calvin cycle from my study guide", "course_id": "BIOLOGY_PHOTOSYNTHESIS"},
                timeout=15
            )
            
            if test_response.status_code == 200:
                test_result = test_response.json()
                print(f"📋 Test Answer: {test_result['answer'][:300]}...")
                print(f"📊 Confidence: {test_result['confidence']}")
                print(f"📚 Sources: {len(test_result['sources'])}")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    force_upload_study_guide()
