#!/usr/bin/env python3
"""
Test script to verify the formatting improvements work correctly
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_formatting():
    """Test the enhanced formatting system"""
    
    # Sample response that should be well formatted
    sample_response = """# 🧬 Glycolysis - Cellular Energy Production

> **📚 Learning Objective:** By the end of this explanation, you'll understand how cells break down glucose to produce ATP through glycolysis.

---

## 🎯 Quick Summary

Glycolysis is the metabolic pathway that breaks down glucose (C6H12O6) into two molecules of pyruvate, producing ATP and NADH in the process. This process occurs in the cytoplasm of cells and is the first step in cellular respiration.

**⏱️ Study Time:** 8-10 minutes | **📊 Difficulty:** 🟡 Intermediate

---

## 🔍 Definition & Overview

Glycolysis is a series of ten enzyme-catalyzed reactions that convert glucose into pyruvate. The name literally means "glucose splitting" (glyco = glucose, lysis = splitting). This ancient metabolic pathway is found in virtually all living organisms and can occur with or without oxygen.

The process can be divided into two main phases:
- **Energy Investment Phase** (Steps 1-5): Glucose is phosphorylated and prepared for splitting
- **Energy Payoff Phase** (Steps 6-10): Energy is harvested in the form of ATP and NADH

---

## 🔬 Key Concepts You Need to Know

### 1. 📝 Energy Investment Phase

- **What it is:** The first five steps where the cell "invests" 2 ATP molecules to prepare glucose
- **Why it matters:** This investment is necessary to destabilize glucose and make it reactive
- **Key terms:** Hexokinase, phosphofructokinase (rate-limiting enzyme), glucose-6-phosphate

### 2. ⚙️ Energy Payoff Phase

**Step-by-step breakdown:**

1. **Glyceraldehyde-3-phosphate oxidation** 🚀 - NADH is produced
2. **ATP synthesis via substrate-level phosphorylation** ➡️ - 4 ATP molecules are made
3. **Pyruvate formation** 🏁 - The final product is created

---

## 💡 Key Terms to Remember

| Term | Definition | Why Important |
|------|------------|---------------|
| Substrate-level phosphorylation | Direct transfer of phosphate to ADP | How ATP is made in glycolysis |
| Pyruvate | 3-carbon end product | Can enter aerobic or anaerobic pathways |
| Phosphofructokinase | Rate-limiting enzyme | Controls the speed of glycolysis |

---

## 🤔 Think About This

- Why does the cell invest 2 ATP to eventually gain only 2 net ATP?
- How might glycolysis have evolved as one of the earliest metabolic pathways?

---

## 🔗 Related Topics to Explore Next

- Krebs Cycle (Citric Acid Cycle)
- Electron Transport Chain
- Fermentation pathways"""

    # Test the parsing function
    try:
        from railway_api import parse_educational_response
        
        print("🧪 Testing Enhanced Educational Response Parsing")
        print("=" * 60)
        
        # Parse the response
        parsed = parse_educational_response(sample_response)
        
        # Display parsed sections
        print(f"📝 Title: {parsed.get('title', 'Not found')}")
        print(f"🎯 Learning Objective: {parsed.get('learning_objective', 'Not found')}")
        print(f"📊 Study Info: {parsed.get('study_info', 'Not found')}")
        print()
        
        print("📋 Quick Summary:")
        print(parsed.get('quick_summary', 'Not found'))
        print()
        
        print("🔍 Definition & Overview:")
        print(parsed.get('definition_overview', 'Not found'))
        print()
        
        print("🔬 Key Concepts:")
        key_concepts = parsed.get('key_concepts', [])
        if key_concepts:
            for i, concept in enumerate(key_concepts, 1):
                print(f"{i}. {concept.get('title', 'No title')}")
                print(f"   {concept.get('content', 'No content')}")
        else:
            print("Not found")
        print()
        
        print("💡 Key Terms:")
        key_terms = parsed.get('key_terms', [])
        if key_terms:
            for term in key_terms:
                print(f"- {term.get('term', 'No term')}: {term.get('definition', 'No definition')}")
        else:
            print("Not found")
        print()
        
        print("🤔 Think About:")
        think_about = parsed.get('think_about', [])
        if think_about:
            for item in think_about:
                print(f"- {item}")
        else:
            print("Not found")
        print()
        
        print("🔗 Related Topics:")
        related_topics = parsed.get('related_topics', [])
        if related_topics:
            for topic in related_topics:
                print(f"- {topic}")
        else:
            print("Not found")
        
        print("\n✅ Parsing test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the railway_api.py file is in the src directory")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_formatting()
