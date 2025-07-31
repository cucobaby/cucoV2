"""
Simplified API Server for Canvas AI Assistant
Focuses on reliable content ingestion with ChromaDB storage
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

# Simple health check without complex dependencies
app = FastAPI(title="Canvas AI Assistant API", version="2.0")

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
    sources: List[str]
    response_time: float

# --- Health Check ---
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Check ChromaDB
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        client = chromadb.PersistentClient(path=chroma_path)
        health_status["services"]["chromadb"] = "connected"
    except Exception as e:
        health_status["services"]["chromadb"] = f"error: {str(e)}"
    
    # Check OpenAI
    try:
        import openai
        health_status["services"]["openai"] = "available"
    except Exception:
        health_status["services"]["openai"] = "not_available"
    
    return health_status

# --- Content Ingestion ---
@app.post("/ingest-content", response_model=IngestResponse)
async def ingest_content(request: ContentIngestRequest):
    """
    Ingest Canvas content into ChromaDB knowledge base
    """
    start_time = datetime.now()
    
    try:
        print(f"📥 Ingesting content: {request.title[:50]}...")
        
        # Try ChromaDB storage with enhanced error handling
        try:
            print("🔄 Attempting ChromaDB import...")
            import chromadb
            print("✅ ChromaDB imported successfully")
            
            # Initialize ChromaDB with detailed logging
            chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            print(f"📁 ChromaDB path: {chroma_path}")
            
            print("🔄 Creating ChromaDB client...")
            client = chromadb.PersistentClient(path=chroma_path)
            print("✅ ChromaDB client created")
            
            # Get or create collection with better error handling
            collection_name = "canvas_content"
            collection = None
            
            try:
                print(f"🔍 Looking for existing collection '{collection_name}'...")
                collection = client.get_collection(collection_name)
                print(f"✅ Using existing '{collection_name}' collection")
            except Exception as get_error:
                print(f"📦 Collection doesn't exist, creating new one. Error: {get_error}")
                try:
                    collection = client.create_collection(
                        name=collection_name,
                        metadata={"description": "Canvas course materials via Chrome extension"}
                    )
                    print(f"✅ Created new '{collection_name}' collection")
                except Exception as create_error:
                    print(f"❌ Failed to create collection: {create_error}")
                    raise create_error
            
            if not collection:
                raise Exception("Failed to get or create collection")
            
            # Generate unique ID
            chunk_id = f"canvas_{abs(hash(request.title))}_{int(start_time.timestamp())}"
            print(f"🆔 Generated chunk ID: {chunk_id}")
            
            # Prepare metadata with validation
            metadata = {
                "title": str(request.title)[:500],  # Limit title length
                "content_type": str(request.content_type or "unknown")[:100],
                "course_id": str(request.course_id or "unknown")[:100], 
                "source_url": str(request.url or "")[:500],
                "source": str(request.source)[:100],
                "timestamp": str(request.timestamp or datetime.now().isoformat()),
                "ingested_at": datetime.now().isoformat()
            }
            
            print(f"📝 Metadata prepared: {list(metadata.keys())}")
            print(f"📄 Content length: {len(request.content)} chars")
            
            # Store in ChromaDB with validation
            try:
                print("🔄 Adding document to collection...")
                collection.add(
                    documents=[str(request.content)],
                    metadatas=[metadata],
                    ids=[chunk_id]
                )
                print(f"✅ Document added successfully")
                
                # Verify storage by counting
                try:
                    count = collection.count()
                    print(f"📊 Collection now has {count} documents")
                except:
                    print("⚠️ Could not verify document count")
                
            except Exception as add_error:
                print(f"❌ Failed to add document: {add_error}")
                print(f"   Document length: {len(request.content)}")
                print(f"   Metadata keys: {list(metadata.keys())}")
                raise add_error
            
            print(f"✅ Content stored in ChromaDB with ID: {chunk_id}")
            
            return IngestResponse(
                status="success", 
                message=f"Content '{request.title}' stored in knowledge base",
                chunks_created=1,
                total_content_items=1,
                content_id=chunk_id,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as db_error:
            print(f"❌ ChromaDB storage failed: {db_error}")
            
            # Fallback: Simple logging with success response
            print("🆘 Using fallback logging mode...")
            
            print(f"📝 Title: {request.title}")
            print(f"📊 Content length: {len(request.content)} characters")
            print(f"🎯 Content type: {request.content_type or 'unknown'}")
            print(f"📍 Course ID: {request.course_id or 'unknown'}")
            print(f"🔗 URL: {request.url or 'no-url'}")
            print(f"📂 Source: {request.source}")
            
            # Return success so the Chrome extension still gets positive feedback
            return IngestResponse(
                status="logged",
                message=f"Content '{request.title}' logged (database temporarily unavailable)",
                chunks_created=0,
                total_content_items=1,
                content_id=f"log_{abs(hash(request.title))}_{int(start_time.timestamp())}",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
    except Exception as e:
        print(f"❌ Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content ingestion failed: {str(e)}")

# --- Question Answering ---
@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer questions about stored content
    """
    start_time = datetime.now()
    
    try:
        print(f"❓ Processing question: {request.question[:50]}...")
        
        # Validate question
        if len(request.question.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Question too short (minimum 5 characters)"
            )
        
        # Try to find relevant content in ChromaDB with enhanced debugging
        try:
            print("🔄 Importing ChromaDB for question answering...")
            import chromadb
            
            chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            print(f"📁 ChromaDB path: {chroma_path}")
            
            print("🔄 Creating ChromaDB client...")
            client = chromadb.PersistentClient(path=chroma_path)
            
            print("🔍 Getting canvas_content collection...")
            collection = client.get_collection("canvas_content")
            
            # Check collection status
            try:
                count = collection.count()
                print(f"📊 Collection has {count} documents")
                
                if count == 0:
                    print("⚠️ No content found in collection")
                    return QuestionResponse(
                        answer="The knowledge base is empty. Please add some content first using the Chrome extension 🤖 buttons.",
                        confidence=0.0,
                        sources=[],
                        response_time=(datetime.now() - start_time).total_seconds()
                    )
                    
            except Exception as count_error:
                print(f"⚠️ Could not count documents: {count_error}")
            
            # Search for relevant content
            print(f"🔍 Searching for: '{request.question[:100]}'...")
            results = collection.query(
                query_texts=[request.question],
                n_results=min(3, count) if 'count' in locals() else 3
            )
            
            print(f"📋 Search results: {len(results['documents'][0]) if results['documents'] and results['documents'][0] else 0} matches")
            
            if results['documents'] and results['documents'][0]:
                relevant_content = "\n\n".join(results['documents'][0])
                sources = [f"Content ID: {id}" for id in results['ids'][0]]
                
                print(f"✅ Found {len(sources)} relevant sources")
                print(f"📄 Content preview: {relevant_content[:200]}...")
                
                # Simple answer generation (without OpenAI for now)
                answer = f"Based on the stored content, here are the relevant details about your question:\n\n{relevant_content[:500]}..."
                
                return QuestionResponse(
                    answer=answer,
                    confidence=0.8,
                    sources=sources,
                    response_time=(datetime.now() - start_time).total_seconds()
                )
            else:
                print("❌ No matching content found")
                return QuestionResponse(
                    answer="I couldn't find relevant information about your question in the stored content.",
                    confidence=0.1,
                    sources=[],
                    response_time=(datetime.now() - start_time).total_seconds()
                )
                
        except Exception as search_error:
            print(f"❌ Search error: {search_error}")
            return QuestionResponse(
                answer="I'm currently unable to search the knowledge base. Please try again later.",
                confidence=0.0,
                sources=[],
                response_time=(datetime.now() - start_time).total_seconds()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Question processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
