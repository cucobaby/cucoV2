"""
Railway-optimized API server with defensive ChromaDB handling - v2.1 with Knowledge Base Viewer
"""
import os
import tempfile
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Railway-safe health check
app = FastAPI(title="Canvas AI Assistant API - Railway", version="2.1-kb-viewer")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ContentIngestRequest(BaseModel):
    title: str
    content: str
    content_type: Optional[str] = None
    course_id: Optional[str] = None
    url: Optional[str] = None
    source: str = "unknown"
    timestamp: Optional[str] = None

class IngestResponse(BaseModel):
    status: str
    message: str
    chunks_created: int
    total_content_items: int
    content_id: str
    processing_time: float

class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None
    course_id: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    response_time: float

# --- Health Check with Defensive ChromaDB ---
@app.get("/health")
async def health_check():
    """Health check endpoint with Railway-safe ChromaDB testing"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0-railway",
        "services": {}
    }
    
    # Test ChromaDB with Railway-safe error handling
    try:
        import chromadb
        
        # Use Railway-safe path
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        # Ensure directory exists
        os.makedirs(chroma_path, exist_ok=True)
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            # Try to get existing collection
            collection = client.get_collection("canvas_content")
            count = collection.count()
            health_status["services"]["chromadb"] = f"connected (collection exists, {count} docs)"
        except Exception:
            # Collection doesn't exist or other issues - this is OK for health check
            health_status["services"]["chromadb"] = "connected (ready for collections)"
        
    except Exception as e:
        health_status["services"]["chromadb"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Test OpenAI
    try:
        import openai
        health_status["services"]["openai"] = "available"
    except Exception as e:
        health_status["services"]["openai"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

# --- Simplified Content Ingestion ---
@app.post("/ingest-content", response_model=IngestResponse)
async def ingest_content(request: ContentIngestRequest):
    """Railway-optimized content ingestion"""
    start_time = datetime.now()
    
    try:
        print(f"📥 Ingesting content: {request.title}")
        
        # Import ChromaDB with Railway-safe handling
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        os.makedirs(chroma_path, exist_ok=True)
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        # Get or create collection
        try:
            collection = client.get_collection("canvas_content")
        except Exception:
            collection = client.create_collection(
                name="canvas_content",
                metadata={"description": "Canvas course content for AI assistant"}
            )
        
        # Create content chunks
        content_chunks = [request.content]
        if len(request.content) > 1000:
            # Simple chunking for large content
            chunk_size = 800
            content_chunks = [
                request.content[i:i + chunk_size]
                for i in range(0, len(request.content), chunk_size)
            ]
        
        # Store in ChromaDB
        content_id = str(uuid.uuid4())
        
        for i, chunk in enumerate(content_chunks):
            collection.add(
                documents=[chunk],
                metadatas=[{
                    "title": request.title,
                    "source": request.source,
                    "content_type": request.content_type or "unknown",
                    "course_id": request.course_id or "unknown",
                    "url": request.url or "",
                    "chunk_index": i,
                    "total_chunks": len(content_chunks),
                    "timestamp": request.timestamp or datetime.now().isoformat(),
                    "content_id": content_id
                }],
                ids=[f"{content_id}_chunk_{i}"]
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Successfully ingested {len(content_chunks)} chunks for '{request.title}'")
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested content: {request.title}",
            chunks_created=len(content_chunks),
            total_content_items=collection.count(),
            content_id=content_id,
            processing_time=processing_time
        )
        
    except Exception as e:
        print(f"❌ Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content ingestion failed: {str(e)}")

# --- Simplified Question Answering ---
@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Railway-optimized question answering"""
    start_time = datetime.now()
    
    try:
        print(f"❓ Processing question: {request.question}")
        
        # Import ChromaDB
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        if not os.path.exists(chroma_path):
            return QuestionResponse(
                answer="I don't have any course materials uploaded yet. Please upload some content using the 🤖 buttons on Canvas pages first.",
                confidence=0.0,
                sources=[],
                response_time=(datetime.now() - start_time).total_seconds()
            )
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
            
            # Search for relevant content
            results = collection.query(
                query_texts=[request.question],
                n_results=min(5, collection.count())
            )
            
            if not results['documents'][0]:
                return QuestionResponse(
                    answer="I don't have any relevant course materials for your question. Please upload relevant content using the 🤖 buttons first.",
                    confidence=0.0,
                    sources=[],
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Use OpenAI for answer generation
            import openai
            
            # Prepare context from search results
            context_parts = []
            sources = []
            
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                context_parts.append(f"Content {i+1}: {doc}")
                sources.append({
                    "title": metadata.get('title', 'Unknown'),
                    "source": metadata.get('source', 'Unknown'),
                    "content_type": metadata.get('content_type', 'Unknown')
                })
            
            context = "\n\n".join(context_parts)
            
            # Generate answer with OpenAI
            openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping students with their course materials. Answer questions based only on the provided context."},
                    {"role": "user", "content": f"Question: {request.question}\n\nContext from course materials:\n{context}\n\nPlease provide a helpful answer based on the course materials."}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return QuestionResponse(
                answer=answer,
                confidence=0.8,
                sources=sources,
                response_time=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            if "does not exist" in str(e):
                return QuestionResponse(
                    answer="No course materials have been uploaded yet. Please use the 🤖 buttons on Canvas pages to upload content first.",
                    confidence=0.0,
                    sources=[],
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Question processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

# --- List Knowledge Base Documents Endpoint ---
@app.get("/list-documents")
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        if not os.path.exists(chroma_path):
            return {
                "status": "success",
                "documents": [],
                "count": 0,
                "message": "Knowledge base is empty"
            }
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
            
            # Get all documents with metadata
            results = collection.get(include=["metadatas"])
            
            # Extract document information
            documents = []
            if results and results.get('metadatas'):
                for i, metadata in enumerate(results['metadatas']):
                    doc_info = {
                        "title": metadata.get('title', 'Untitled Document'),
                        "source": metadata.get('source', 'unknown'),
                        "timestamp": metadata.get('timestamp', ''),
                        "content_type": metadata.get('content_type', 'page'),
                        "url": metadata.get('url', '')
                    }
                    documents.append(doc_info)
            
            return {
                "status": "success",
                "documents": documents,
                "count": len(documents),
                "message": f"Found {len(documents)} documents in knowledge base"
            }
            
        except Exception as collection_error:
            print(f"Collection error: {collection_error}")
            return {
                "status": "success",
                "documents": [],
                "count": 0,
                "message": "Knowledge base is empty (no collection found)"
            }
            
    except Exception as e:
        print(f"❌ List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

# --- Clear Knowledge Base Endpoint ---
@app.delete("/clear-knowledge-base")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        if not os.path.exists(chroma_path):
            return {
                "status": "success",
                "message": "Knowledge base was already empty.",
                "documents_removed": 0
            }
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
            doc_count = collection.count()
            client.delete_collection("canvas_content")
            
            return {
                "status": "success",
                "message": f"Knowledge base cleared successfully. Removed {doc_count} documents.",
                "documents_removed": doc_count
            }
            
        except Exception as e:
            if "does not exist" in str(e).lower():
                return {
                    "status": "success", 
                    "message": "Knowledge base was already empty.",
                    "documents_removed": 0
                }
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Clear knowledge base error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear knowledge base: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
