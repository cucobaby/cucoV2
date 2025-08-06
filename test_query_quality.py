#!/usr/bin/env python3
"""
Quick Query Quality Tester
Rapidly test and iterate on query responses without using the Chrome extension
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://cucov2-production.up.railway.app"
# API_BASE_URL = "http://localhost:8000"  # Uncomment for local testing

class QueryTester:
    def __init__(self):
        self.session = requests.Session()
        
    def upload_test_content(self, title, content):
        """Upload content for testing"""
        payload = {
            "title": title,
            "content": content,
            "source": "test_script",
            "url": "http://test.local",
            "timestamp": datetime.now().isoformat()
        }
        
        response = self.session.post(f"{API_BASE_URL}/upload-content", 
                                   json=payload, 
                                   headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Uploaded: {title} ({result.get('chunks_created', 1)} chunks)")
            return result
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
    
    def test_query(self, question):
        """Test a query and return detailed results"""
        print(f"\n🤖 Testing Question: '{question}'")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            response = self.session.post(f"{API_BASE_URL}/query",
                                       json={"question": question},
                                       headers={'Content-Type': 'application/json'})
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"⏱️  Response Time: {response_time:.2f}s")
                print(f"📚 Sources Found: {len(result.get('sources', []))}")
                if result.get('sources'):
                    for i, source in enumerate(result['sources'], 1):
                        print(f"   {i}. {source}")
                
                print(f"\n🤖 Answer:")
                print(result['answer'])
                print("-" * 60)
                
                return {
                    'question': question,
                    'answer': result['answer'],
                    'sources': result.get('sources', []),
                    'response_time': response_time,
                    'timestamp': result.get('timestamp')
                }
            else:
                print(f"❌ Query failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def list_documents(self):
        """List all documents in knowledge base"""
        try:
            response = self.session.get(f"{API_BASE_URL}/list-documents")
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Knowledge Base: {result.get('count', 0)} documents")
                for doc in result.get('documents', []):
                    chunks = doc.get('chunk_count', 1)
                    print(f"   📄 {doc.get('title')} ({chunks} chunks)")
                return result
            else:
                print(f"❌ Failed to list documents: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error listing documents: {str(e)}")
            return None
    
    def clear_knowledge_base(self):
        """Clear all documents for fresh testing"""
        try:
            response = self.session.post(f"{API_BASE_URL}/clear-documents")
            if response.status_code == 200:
                print("✅ Knowledge base cleared")
                return True
            else:
                print(f"❌ Failed to clear: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error clearing: {str(e)}")
            return False

def run_test_suite():
    """Run a comprehensive test suite"""
    tester = QueryTester()
    
    print("🧪 Starting Query Quality Test Suite")
    print("=" * 60)
    
    # Check current knowledge base
    tester.list_documents()
    
    # Sample test content (you can modify this)
    test_content = """
    Protein Structure Levels:
    
    1. Primary Structure: The linear sequence of amino acids in a protein chain.
    2. Secondary Structure: Local folding patterns like alpha helices and beta sheets.
    3. Tertiary Structure: The overall 3D shape of a single protein molecule.
    4. Quaternary Structure: The arrangement of multiple protein subunits.
    
    Key Points:
    - Proteins fold based on amino acid properties
    - Hydrophobic residues tend to cluster inside
    - Hydrogen bonds stabilize secondary structures
    - Disulfide bonds provide additional stability
    """
    
    # Upload test content
    # tester.upload_test_content("Protein Structure Guide", test_content)
    
    # Test various question types
    test_questions = [
        "What are the four levels of protein structure?",
        "How do proteins fold?",
        "What stabilizes secondary structure?",
        "Explain hydrophobic interactions in proteins",
        "What is the difference between tertiary and quaternary structure?"
    ]
    
    results = []
    for question in test_questions:
        result = tester.test_query(question)
        if result:
            results.append(result)
        time.sleep(0.5)  # Brief pause between queries
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 60)
    avg_time = sum(r['response_time'] for r in results) / len(results) if results else 0
    print(f"Average Response Time: {avg_time:.2f}s")
    print(f"Successful Queries: {len(results)}/{len(test_questions)}")
    
    return results

if __name__ == "__main__":
    # Quick interactive mode
    tester = QueryTester()
    
    while True:
        print("\n🤖 Query Quality Tester")
        print("1. Test single question")
        print("2. Run test suite")
        print("3. List knowledge base")
        print("4. Clear knowledge base")
        print("5. Upload test content")
        print("0. Exit")
        
        choice = input("\nChoose option: ").strip()
        
        if choice == "1":
            question = input("Enter question: ")
            tester.test_query(question)
        elif choice == "2":
            run_test_suite()
        elif choice == "3":
            tester.list_documents()
        elif choice == "4":
            tester.clear_knowledge_base()
        elif choice == "5":
            title = input("Document title: ")
            content = input("Document content: ")
            tester.upload_test_content(title, content)
        elif choice == "0":
            break
        else:
            print("Invalid choice")
