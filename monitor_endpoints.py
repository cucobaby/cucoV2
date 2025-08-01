"""
Additional monitoring endpoints for the Canvas AI Assistant API
Add these endpoints to your main API to support the monitoring dashboard
"""

from fastapi import APIRouter
from datetime import datetime
import json
import os

# Create monitoring router
monitor_router = APIRouter(prefix="/monitor", tags=["monitoring"])

@monitor_router.get("/list-documents")
async def list_documents():
    """List all documents in the knowledge base with metadata"""
    try:
        # Import ChromaDB here to avoid dependency issues
        import chromadb
        from chromadb.config import Settings
        
        # Get ChromaDB path from environment or use default
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get all collections
        collections = client.list_collections()
        
        total_documents = 0
        all_documents = []
        collection_info = []
        
        for collection_info_item in collections:
            try:
                collection = client.get_collection(collection_info_item.name)
                doc_count = collection.count()
                total_documents += doc_count
                
                collection_info.append({
                    "name": collection_info_item.name,
                    "document_count": doc_count
                })
                
                # Get some sample documents with metadata
                if doc_count > 0:
                    # Get up to 10 recent documents
                    result = collection.get(
                        limit=min(doc_count, 10),
                        include=["metadatas", "documents"]
                    )
                    
                    if result and result.get("ids"):
                        for i, doc_id in enumerate(result["ids"]):
                            metadata = result["metadatas"][i] if result.get("metadatas") else {}
                            document_text = result["documents"][i] if result.get("documents") else ""
                            
                            all_documents.append({
                                "id": doc_id,
                                "title": metadata.get("title", document_text[:100] + "..." if len(document_text) > 100 else document_text),
                                "source": metadata.get("source", "unknown"),
                                "timestamp": metadata.get("timestamp", "unknown"),
                                "content_type": metadata.get("content_type", "unknown"),
                                "content_preview": document_text[:200] + "..." if len(document_text) > 200 else document_text
                            })
                            
            except Exception as e:
                print(f"Error processing collection {collection_info_item.name}: {str(e)}")
                continue
        
        # Sort documents by timestamp (newest first)
        all_documents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "total_documents": total_documents,
            "collections": collection_info,
            "documents": all_documents,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "total_documents": 0,
            "collections": [],
            "documents": [],
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@monitor_router.get("/system-stats")
async def get_system_stats():
    """Get system statistics and health information"""
    try:
        import chromadb
        from chromadb.config import Settings
        import psutil
        
        # Get ChromaDB path from environment or use default
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        # System stats
        stats = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if os.path.exists('/') else 0
            },
            "chromadb": {
                "status": "connected",
                "path": chroma_path,
                "path_exists": os.path.exists(chroma_path)
            },
            "api": {
                "status": "online",
                "uptime": "unknown"  # You can track this with app startup time
            }
        }
        
        # Try to connect to ChromaDB
        try:
            client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            collections = client.list_collections()
            stats["chromadb"]["collections_count"] = len(collections)
            stats["chromadb"]["status"] = "connected"
        except Exception as e:
            stats["chromadb"]["status"] = "error"
            stats["chromadb"]["error"] = str(e)
        
        return stats
        
    except ImportError as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": f"Missing dependencies: {str(e)}",
            "system": {"status": "degraded"}
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "system": {"status": "error"}
        }

@monitor_router.get("/activity-log")
async def get_activity_log():
    """Get recent activity log (if logging is implemented)"""
    # This is a placeholder - you can implement actual logging
    # For now, return some sample activity
    
    activities = [
        {
            "timestamp": datetime.now().isoformat(),
            "action": "system_check",
            "status": "completed",
            "message": "System health check completed successfully"
        },
        {
            "timestamp": (datetime.now()).isoformat(),
            "action": "document_query",
            "status": "completed", 
            "message": "Document search query processed"
        }
    ]
    
    return {
        "activities": activities,
        "total_count": len(activities),
        "timestamp": datetime.now().isoformat()
    }

@monitor_router.post("/test-search")
async def test_search_endpoint(query: dict):
    """Test search functionality with detailed response"""
    try:
        # This would call your existing search function
        # For now, return a test response
        search_query = query.get("question", "")
        
        if not search_query:
            return {
                "error": "No query provided",
                "timestamp": datetime.now().isoformat()
            }
        
        # You can integrate with your existing ask endpoint here
        # For now, return test data
        return {
            "query": search_query,
            "answer": "This is a test response from the monitoring system",
            "sources": ["Test Source 1", "Test Source 2"],
            "search_time_ms": 150,
            "documents_searched": 5,
            "relevance_scores": [0.85, 0.72, 0.68],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Add this to your main API file:
"""
To integrate these monitoring endpoints into your main API:

1. Import this router:
   from monitor_endpoints import monitor_router

2. Include it in your FastAPI app:
   app.include_router(monitor_router)

3. Or add these endpoints directly to your existing API file
"""
