"""
Railway-optimized API server with defensive ChromaDB handling
"""
import os
import tempfile
import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Railway-safe health check
app = FastAPI(title="Canvas AI Assistant API - Railway", version="2.0")

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
        
        # Enhanced content chunking for better search performance
        content_chunks = []
        
        if len(request.content) <= 1200:
            # Small content - store as single chunk
            content_chunks = [request.content]
        else:
            # Large content - intelligent chunking
            # First, try to split by sections/paragraphs
            sections = request.content.split('\n\n')
            current_chunk = ""
            
            for section in sections:
                # If adding this section would make chunk too large, save current chunk
                if len(current_chunk) + len(section) > 1000 and current_chunk:
                    content_chunks.append(current_chunk.strip())
                    current_chunk = section
                else:
                    current_chunk += "\n\n" + section if current_chunk else section
            
            # Add the last chunk
            if current_chunk.strip():
                content_chunks.append(current_chunk.strip())
            
            # If we still have chunks that are too large, split them further
            final_chunks = []
            for chunk in content_chunks:
                if len(chunk) <= 1200:
                    final_chunks.append(chunk)
                else:
                    # Split large chunks by sentences or fixed size
                    sentences = chunk.split('. ')
                    sub_chunk = ""
                    
                    for sentence in sentences:
                        if len(sub_chunk) + len(sentence) > 1000 and sub_chunk:
                            final_chunks.append(sub_chunk.strip() + '.')
                            sub_chunk = sentence
                        else:
                            sub_chunk += ". " + sentence if sub_chunk else sentence
                    
                    if sub_chunk.strip():
                        final_chunks.append(sub_chunk.strip())
            
            content_chunks = final_chunks
        
        print(f"📝 Content split into {len(content_chunks)} chunks")
        for i, chunk in enumerate(content_chunks):
            print(f"   Chunk {i+1}: {len(chunk)} characters")
        
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

# --- Test Endpoint ---
@app.get("/test-simple")
async def test_simple():
    """Simple test endpoint to verify deployment"""
    return {
        "status": "working",
        "message": "API is responding correctly",
        "timestamp": datetime.now().isoformat(),
        "version": "fixed-openai-v2"
    }

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
            
            # Check if collection has any documents
            doc_count = collection.count()
            print(f"📊 Collection has {doc_count} documents")
            
            if doc_count == 0:
                return QuestionResponse(
                    answer="I don't have any course materials uploaded yet. Please upload some content using the 🤖 buttons on Canvas pages first.",
                    confidence=0.0,
                    sources=[],
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Search for relevant content
            print(f"🔍 Searching for: '{request.question}'")
            results = collection.query(
                query_texts=[request.question],
                n_results=min(5, doc_count)
            )
            
            print(f"📝 Search results: {len(results['documents'][0]) if results['documents'][0] else 0} documents found")
            
            if not results['documents'][0] or len(results['documents'][0]) == 0:
                return QuestionResponse(
                    answer="I couldn't find any relevant course materials for your question. Try asking about the topics that have been uploaded.",
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
            try:
                import openai
                print(f"🔧 Initializing OpenAI client...")
                
                # Get API key
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise Exception("OpenAI API key not found in environment")
                
                print(f"✅ API key found: {api_key[:8]}...")
                
                # Railway-safe OpenAI client initialization
                # Clear any proxy-related environment variables that might interfere
                original_proxies = {}
                proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
                for var in proxy_vars:
                    if var in os.environ:
                        original_proxies[var] = os.environ[var]
                        del os.environ[var]
                
                try:
                    # Initialize with minimal parameters to avoid proxy issues
                    openai_client = openai.OpenAI(api_key=api_key)
                    print(f"✅ OpenAI client initialized successfully")
                    
                finally:
                    # Restore proxy environment variables
                    for var, value in original_proxies.items():
                        os.environ[var] = value
                
                print(f"📝 Generating answer for question: {request.question[:50]}...")
                
                # Generate response
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a strict document-based AI assistant. You must ONLY answer questions using information that is explicitly provided in the context below. If the context does not contain the information needed to answer the question, you must say 'I cannot find that information in the uploaded documents.' Do NOT use any general knowledge or information not present in the provided context."},
                        {"role": "user", "content": f"Question: {request.question}\n\nContext from uploaded documents:\n{context}\n\nAnswer this question using ONLY the information provided in the context above. If the context doesn't contain relevant information, say so clearly."}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                
                answer = response.choices[0].message.content
                print(f"✅ OpenAI response generated successfully")
                
            except Exception as openai_error:
                print(f"❌ OpenAI processing failed: {openai_error}")
                print(f"🔍 Error type: {type(openai_error)}")
                print(f"🔍 Error details: {str(openai_error)}")
                
                # Try fallback approach with direct API call
                try:
                    print(f"🔄 Trying fallback OpenAI approach...")
                    import httpx
                    
                    # Direct API call bypassing client initialization issues
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a strict document-based AI assistant. You must ONLY answer questions using information that is explicitly provided in the context below. If the context does not contain the information needed to answer the question, you must say 'I cannot find that information in the uploaded documents.' Do NOT use any general knowledge or information not present in the provided context."},
                            {"role": "user", "content": f"Question: {request.question}\n\nContext from uploaded documents:\n{context}\n\nAnswer this question using ONLY the information provided in the context above. If the context doesn't contain relevant information, say so clearly."}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.3
                    }
                    
                    with httpx.Client() as client:
                        api_response = client.post(
                            "https://api.openai.com/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=30
                        )
                        
                        if api_response.status_code == 200:
                            result = api_response.json()
                            answer = result["choices"][0]["message"]["content"]
                            print(f"✅ Fallback OpenAI call successful")
                        else:
                            raise Exception(f"API call failed: {api_response.status_code} - {api_response.text}")
                            
                except Exception as fallback_error:
                    print(f"❌ Fallback also failed: {fallback_error}")
                    # Return a helpful error message instead of crashing
                    return QuestionResponse(
                        answer=f"I found relevant content but encountered an issue generating the response. The search found content about: {', '.join([s['title'] for s in sources[:3]])}. Please try rephrasing your question.",
                        confidence=0.0,
                        sources=sources,
                        response_time=(datetime.now() - start_time).total_seconds()
                    )
            
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
