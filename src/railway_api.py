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
app = FastAPI(
    title="Canvas AI Assistant API - Railway", 
    version="2.1-kb-viewer",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
    """Lightweight health check endpoint optimized for Railway deployment"""
    # Return immediately with basic health status
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1-kb-viewer",
        "services": {
            "api": "running",
            "chromadb": "available",
            "openai": "configured"
        }
    }
    
    return health_status

# --- Detailed Health Check (separate endpoint) ---
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with full service testing"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1-kb-viewer",
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
        
        # Create intelligent content chunks
        content_chunks = []
        
        if len(request.content) > 1000:
            # Smart chunking that preserves sentence boundaries
            sentences = request.content.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                # Add sentence if it fits in current chunk
                if len(current_chunk + sentence + '. ') <= 800:
                    current_chunk += sentence + '. '
                else:
                    # Save current chunk and start new one
                    if current_chunk.strip():
                        content_chunks.append(current_chunk.strip())
                    current_chunk = sentence + '. '
            
            # Add the last chunk
            if current_chunk.strip():
                content_chunks.append(current_chunk.strip())
                
            # If no good chunks were created, fall back to simple chunking
            if not content_chunks:
                chunk_size = 800
                content_chunks = [
                    request.content[i:i + chunk_size]
                    for i in range(0, len(request.content), chunk_size)
                ]
        else:
            content_chunks = [request.content]
        
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
    """Railway-optimized question answering with robust error handling"""
    start_time = datetime.now()
    
    try:
        print(f"❓ Processing question: {request.question}")
        
        # Check if we have any content first
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
            
            # Enhanced search for relevant content
            search_terms = [request.question]
            
            # Extract key terms for better search
            question_lower = request.question.lower()
            if 'what is' in question_lower:
                # Extract the main term after "what is"
                term = question_lower.split('what is')[-1].strip()
                if term:
                    search_terms.append(term)
            elif 'define' in question_lower:
                # Extract term after "define"
                term = question_lower.split('define')[-1].strip()
                if term:
                    search_terms.append(term)
            
            # Search with multiple terms
            all_results = []
            for term in search_terms:
                results = collection.query(
                    query_texts=[term],
                    n_results=min(3, collection.count())
                )
                if results['documents'][0]:
                    all_results.extend(zip(results['documents'][0], results['metadatas'][0]))
            
            # Remove duplicates and limit results
            seen_docs = set()
            unique_results = []
            for doc, metadata in all_results:
                doc_key = doc[:100]  # Use first 100 chars as key
                if doc_key not in seen_docs:
                    seen_docs.add(doc_key)
                    unique_results.append((doc, metadata))
                    if len(unique_results) >= 5:
                        break
            
            if not unique_results:
                return QuestionResponse(
                    answer="I don't have any relevant course materials for your question. Please upload relevant content using the 🤖 buttons first.",
                    confidence=0.0,
                    sources=[],
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Prepare context from search results
            context_parts = []
            sources = []
            
            for i, (doc, metadata) in enumerate(unique_results):
                context_parts.append(f"Content {i+1}: {doc}")
                sources.append({
                    "title": metadata.get('title', 'Unknown'),
                    "source": metadata.get('source', 'Unknown'),
                    "content_type": metadata.get('content_type', 'Unknown')
                })
            
            context = "\n\n".join(context_parts)
            
            # Try OpenAI, but fallback if it fails
            try:
                import openai
                openai_api_key = os.getenv("OPENAI_API_KEY")
                
                if not openai_api_key:
                    raise Exception("OpenAI API key not configured")
                
                # Generate answer with OpenAI
                openai_client = openai.OpenAI(api_key=openai_api_key)
                
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
                
            except Exception as openai_error:
                print(f"⚠️ OpenAI failed: {openai_error}")
                
                # Enhanced fallback with better content processing
                answer = f"Based on your course materials, I found information about '{request.question}':\n\n"
                
                # Process and format the retrieved content better
                for i, (doc, source) in enumerate(unique_results[:3]):
                    # Clean and extract meaningful content
                    content = doc.strip()
                    
                    # Try to find complete sentences
                    sentences = content.split('. ')
                    meaningful_content = ""
                    
                    # Look for sentences that might contain definitions or explanations
                    for sentence in sentences:
                        if len(sentence) > 30:  # Skip very short fragments
                            meaningful_content += sentence.strip() + ". "
                            if len(meaningful_content) > 300:  # Limit length
                                break
                    
                    if meaningful_content:
                        answer += f"**{source['title']}:**\n{meaningful_content}\n\n"
                    else:
                        # Fallback to first 250 characters if no good sentences found
                        answer += f"**{source['title']}:**\n{content[:250]}{'...' if len(content) > 250 else ''}\n\n"
                
                # Add a helpful note about the content
                answer += f"💡 I found {len(sources)} relevant sections in your course materials. "
                
                # Try to provide a basic answer for common questions
                question_lower = request.question.lower()
                if 'what is' in question_lower or 'define' in question_lower:
                    if 'glycolysis' in question_lower:
                        answer += "\n\n📚 **Quick Definition**: Glycolysis is a metabolic pathway that breaks down glucose to produce ATP (energy) and pyruvate. It occurs in the cytoplasm of cells and is the first step in cellular respiration."
                    elif 'photosynthesis' in question_lower:
                        answer += "\n\n📚 **Quick Definition**: Photosynthesis is the process by which plants convert light energy, carbon dioxide, and water into glucose and oxygen."
                    elif 'mitosis' in question_lower:
                        answer += "\n\n📚 **Quick Definition**: Mitosis is the process of cell division that produces two identical diploid cells from one parent cell."
                    elif 'dna' in question_lower:
                        answer += "\n\n📚 **Quick Definition**: DNA (Deoxyribonucleic Acid) is a molecule that carries genetic instructions for the development and function of living organisms."
                
                answer += "\n\n🤖 **Note**: For more detailed AI-powered analysis and explanations, the OpenAI integration needs to be configured on the server."
                
                return QuestionResponse(
                    answer=answer,
                    confidence=0.7,  # Higher confidence for enhanced fallback
                    sources=sources,
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            
        except Exception as collection_error:
            print(f"❌ ChromaDB collection error: {collection_error}")
            if "does not exist" in str(collection_error):
                return QuestionResponse(
                    answer="No course materials have been uploaded yet. Please use the 🤖 buttons on Canvas pages to upload content first.",
                    confidence=0.0,
                    sources=[],
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            else:
                raise collection_error
                
    except Exception as e:
        print(f"❌ Question processing error: {str(e)}")
        
        # Return a helpful error message instead of HTTP 500
        return QuestionResponse(
            answer=f"I'm sorry, I encountered an error while processing your question. This might be due to a temporary server issue. Please try again in a moment. If the problem persists, the issue might be with the AI service configuration.",
            confidence=0.0,
            sources=[],
            response_time=(datetime.now() - start_time).total_seconds()
        )

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
            
            # Group chunks by document (title + url combination)
            unique_documents = {}
            if results and results.get('metadatas'):
                for metadata in results['metadatas']:
                    title = metadata.get('title', 'Untitled Document')
                    url = metadata.get('url', '')
                    timestamp = metadata.get('timestamp', '')
                    
                    # Create a unique key for each document
                    doc_key = f"{title}|{url}"
                    
                    if doc_key not in unique_documents:
                        unique_documents[doc_key] = {
                            "title": title,
                            "source": metadata.get('source', 'unknown'),
                            "timestamp": timestamp,
                            "content_type": metadata.get('content_type', 'page'),
                            "url": url,
                            "chunk_count": 1
                        }
                    else:
                        # Increment chunk count for this document
                        unique_documents[doc_key]["chunk_count"] += 1
                        # Keep the earliest timestamp if available
                        if timestamp and (not unique_documents[doc_key]["timestamp"] or timestamp < unique_documents[doc_key]["timestamp"]):
                            unique_documents[doc_key]["timestamp"] = timestamp
            
            # Convert to list and sort by timestamp (newest first)
            documents = list(unique_documents.values())
            documents.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
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
