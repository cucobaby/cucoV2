"""
Script to clear the ChromaDB knowledge base
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def clear_knowledge_base():
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
        print(f"🔧 Connecting to ChromaDB at: {chroma_path}")
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            # Get the collection and count documents before deletion
            collection = client.get_collection("canvas_content")
            doc_count = collection.count()
            print(f"📊 Found {doc_count} documents in knowledge base")
            
            # Delete the collection
            client.delete_collection("canvas_content")
            print(f"✅ Successfully cleared knowledge base! Removed {doc_count} documents.")
            
            return doc_count
            
        except Exception as e:
            if "does not exist" in str(e).lower():
                print("✅ Knowledge base was already empty.")
                return 0
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Error clearing knowledge base: {str(e)}")
        return None

if __name__ == "__main__":
    print("🧹 Clearing Canvas AI Assistant Knowledge Base...")
    result = clear_knowledge_base()
    
    if result is not None:
        print(f"\n🎉 Knowledge base cleared successfully!")
        print(f"📈 Ready for fresh, high-quality content!")
    else:
        print(f"\n❌ Failed to clear knowledge base. Check the error above.")
