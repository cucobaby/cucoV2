"""
Standalone ChromaDB Clear Tool
Run this anytime you want to clear the knowledge base for focused testing

Usage:
    python clear_chroma_tool.py [options]

Options:
    --local     Clear local ChromaDB only (default)
    --railway   Clear Railway ChromaDB via API
    --both      Clear both local and Railway
    --confirm   Skip confirmation prompt
"""

import os
import sys
import argparse
import requests
from datetime import datetime

def clear_local_chromadb():
    """Clear local ChromaDB database"""
    print("🧹 Clearing Local ChromaDB...")
    
    try:
        import chromadb
        
        # Try multiple possible paths
        possible_paths = [
            os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh"),
            "./chroma_db_v3_fresh",
            "./chroma_db",
            "/tmp/chroma_db_railway"
        ]
        
        cleared_any = False
        
        for chroma_path in possible_paths:
            if os.path.exists(chroma_path):
                print(f"🔍 Found ChromaDB at: {chroma_path}")
                
                try:
                    client = chromadb.PersistentClient(path=chroma_path)
                    
                    # Get all collections
                    collections = client.list_collections()
                    total_docs = 0
                    
                    for collection_info in collections:
                        collection = client.get_collection(collection_info.name)
                        doc_count = collection.count()
                        total_docs += doc_count
                        print(f"   📊 Collection '{collection_info.name}': {doc_count} documents")
                        
                        # Delete the collection
                        client.delete_collection(collection_info.name)
                        print(f"   ✅ Deleted collection '{collection_info.name}'")
                    
                    if total_docs > 0:
                        print(f"✅ Local ChromaDB cleared: {total_docs} documents removed from {chroma_path}")
                        cleared_any = True
                    else:
                        print(f"ℹ️  ChromaDB at {chroma_path} was already empty")
                        
                except Exception as e:
                    print(f"⚠️  Error clearing {chroma_path}: {str(e)}")
        
        if not cleared_any:
            print("ℹ️  No local ChromaDB found or all were already empty")
            
        return True
        
    except ImportError:
        print("❌ ChromaDB not installed. Run: pip install chromadb")
        return False
    except Exception as e:
        print(f"❌ Error clearing local ChromaDB: {str(e)}")
        return False

def clear_railway_chromadb():
    """Clear Railway ChromaDB via API"""
    print("🧹 Clearing Railway ChromaDB...")
    
    API_BASE_URL = "https://cucov2-production.up.railway.app"
    
    try:
        # Test API health first
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ Railway API not responding: {health_response.status_code}")
            return False
        
        # Clear the knowledge base
        clear_response = requests.delete(f"{API_BASE_URL}/clear-knowledge-base", timeout=30)
        
        if clear_response.status_code == 200:
            result = clear_response.json()
            docs_removed = result.get('documents_removed', 0)
            message = result.get('message', 'Cleared successfully')
            print(f"✅ Railway ChromaDB cleared: {message}")
            return True
        else:
            print(f"❌ Railway clear failed: {clear_response.status_code} - {clear_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Railway API error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error clearing Railway ChromaDB: {str(e)}")
        return False

def confirm_action(message):
    """Ask for user confirmation"""
    response = input(f"{message} (y/N): ").lower().strip()
    return response in ['y', 'yes']

def main():
    parser = argparse.ArgumentParser(description="Clear ChromaDB for focused testing")
    parser.add_argument('--local', action='store_true', help='Clear local ChromaDB only')
    parser.add_argument('--railway', action='store_true', help='Clear Railway ChromaDB only')
    parser.add_argument('--both', action='store_true', help='Clear both local and Railway')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Default to local if no specific option
    if not any([args.local, args.railway, args.both]):
        args.local = True
    
    print("🔧 ChromaDB Clear Tool")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Determine what to clear
    clear_local = args.local or args.both
    clear_railway = args.railway or args.both
    
    if clear_local and clear_railway:
        action_desc = "both local and Railway ChromaDB"
    elif clear_local:
        action_desc = "local ChromaDB"
    else:
        action_desc = "Railway ChromaDB"
    
    # Confirmation
    if not args.confirm:
        if not confirm_action(f"🚨 This will clear {action_desc}. Continue?"):
            print("❌ Operation cancelled")
            return
    
    print()
    success = True
    
    # Clear local if requested
    if clear_local:
        if not clear_local_chromadb():
            success = False
        print()
    
    # Clear Railway if requested
    if clear_railway:
        if not clear_railway_chromadb():
            success = False
        print()
    
    # Summary
    if success:
        print("🎉 ChromaDB clear operation completed successfully!")
        print("📋 Ready for focused testing with clean knowledge base")
    else:
        print("⚠️  ChromaDB clear operation completed with some errors")
        print("📋 Check the output above for details")

if __name__ == "__main__":
    main()
