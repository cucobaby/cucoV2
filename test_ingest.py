#!/usr/bin/env python3
"""
Test content ingestion to restore data
"""
import requests
import json

def test_ingest_content():
    """Test the ingest-content endpoint"""
    
    base_url = "https://cucov2-production.up.railway.app"
    
    test_content = {
        "title": "Biology Study Guide - Protein Structure",
        "content": """Protein Structure Levels:

1. Primary Structure: The linear sequence of amino acids in a protein chain, connected by peptide bonds.

2. Secondary Structure: Local folding patterns including:
   - Alpha helixes: spiral structures stabilized by hydrogen bonds
   - Beta sheets: extended strands forming sheet-like structures

3. Tertiary Structure: The overall 3D shape of a single protein molecule, determined by interactions between amino acid side chains (R-groups).

4. Quaternary Structure: The arrangement of multiple protein subunits to form a functional protein complex.

Additional protein concepts:
- Amino acids are the monomers that make up proteins
- Glycine is the simplest amino acid with R-group = H
- Protein folding is crucial for function
- Hydrophobic and hydrophilic interactions affect protein structure""",
        "content_type": "study_guide",
        "source": "biology_course"
    }
    
    try:
        print("🔄 Testing content ingestion...")
        response = requests.post(
            f"{base_url}/ingest-content",
            json=test_content,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Content ingested successfully!")
            print(f"Result: {result}")
        else:
            print(f"❌ Ingestion failed: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_ingest_content()
