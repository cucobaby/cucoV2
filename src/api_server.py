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

# --- Health Check with Enhanced ChromaDB Diagnostics ---
@app.get("/health")
async def health_check():
    """Health check endpoint with detailed ChromaDB diagnostics"""
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Check ChromaDB with detailed diagnostics
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
        client = chromadb.PersistentClient(path=chroma_path)
        
        # Test collection operations
        try:
            # Try to get canvas_content collection
            try:
                collection = client.get_collection("canvas_content")
                count = collection.count()
                health_status["services"]["chromadb"] = f"connected (collection exists, {count} docs)"
            except:
                # Try to create a test collection
                test_collection = client.create_collection("health_test")
                test_collection.add(
                    documents=["health check test"],
                    metadatas=[{"test": "true"}],
                    ids=["health_test"]
                )
                client.delete_collection("health_test")
                health_status["services"]["chromadb"] = "connected (test collection created/deleted successfully)"
        except Exception as op_error:
            health_status["services"]["chromadb"] = f"connected but operations failing: {str(op_error)}"
            
    except Exception as e:
        health_status["services"]["chromadb"] = f"error: {str(e)}"
    
    # Check OpenAI
    try:
        import openai
        health_status["services"]["openai"] = "available"
    except Exception:
        health_status["services"]["openai"] = "not_available"
    
    return health_status

# --- Diagnostic Endpoint ---
@app.get("/debug/chromadb")
async def debug_chromadb():
    """Diagnostic endpoint to test ChromaDB operations"""
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    try:
        import chromadb
        debug_info["tests"]["import"] = "✅ ChromaDB imported successfully"
        
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
        debug_info["chroma_path"] = chroma_path
        
        client = chromadb.PersistentClient(path=chroma_path)
        debug_info["tests"]["client"] = "✅ Client created successfully"
        
        # Test collection operations
        test_collection_name = f"debug_test_{int(datetime.now().timestamp())}"
        
        try:
            # Create test collection
            collection = client.create_collection(test_collection_name)
            debug_info["tests"]["create_collection"] = "✅ Collection created"
            
            # Add test document
            collection.add(
                documents=["This is a test document for debugging ChromaDB functionality"],
                metadatas=[{"test": "true", "type": "debug"}],
                ids=["debug_doc_1"]
            )
            debug_info["tests"]["add_document"] = "✅ Document added"
            
            # Query test
            results = collection.query(query_texts=["test document"], n_results=1)
            debug_info["tests"]["query"] = f"✅ Query successful, found {len(results['documents'][0])} results"
            
            # Count test
            count = collection.count()
            debug_info["tests"]["count"] = f"✅ Count successful: {count} documents"
            
            # Clean up
            client.delete_collection(test_collection_name)
            debug_info["tests"]["cleanup"] = "✅ Test collection deleted"
            
        except Exception as test_error:
            debug_info["tests"]["collection_operations"] = f"❌ Failed: {str(test_error)}"
            
        # Check existing canvas_content collection
        try:
            canvas_collection = client.get_collection("canvas_content")
            canvas_count = canvas_collection.count()
            debug_info["canvas_collection"] = f"✅ Exists with {canvas_count} documents"
        except Exception as canvas_error:
            debug_info["canvas_collection"] = f"❌ Does not exist: {str(canvas_error)}"
            
    except Exception as e:
        debug_info["tests"]["general_error"] = f"❌ {str(e)}"
    
    return debug_info

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
            
            # Use a fresh ChromaDB path to avoid schema conflicts
            # Use environment variable or default to a v3 path to avoid old schema issues
            fresh_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
            print(f"📁 Using fresh ChromaDB path: {fresh_db_path}")
            
            print("🔄 Creating ChromaDB client with fresh database...")
            client = chromadb.PersistentClient(path=fresh_db_path)
            print("✅ ChromaDB client created with fresh database")
            
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
            
            # Start with basic metadata that we know will work
            enhanced_metadata = {
                "title": str(request.title)[:500],
                "content_type": str(request.content_type or "unknown")[:100],
                "course_id": str(request.course_id or "unknown")[:100], 
                "source_url": str(request.url or "")[:500],
                "source": str(request.source)[:100],
                "timestamp": str(request.timestamp or datetime.now().isoformat()),
                "ingested_at": datetime.now().isoformat()
            }
            
            # Try to enhance with ContentAnalyzer, but don't let it break storage
            try:
                print("🔍 Running content analysis for enhanced storage...")
                
                # Import and use ContentAnalyzer for intelligent content processing
                import sys
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                
                from content_analyzer import ContentAnalyzer
                
                analyzer = ContentAnalyzer()
                
                # Analyze the content to extract topics and key information
                source_info = {
                    "filename": request.title,
                    "url": request.url,
                    "course_id": request.course_id
                }
                
                content_analysis = analyzer.analyze_content([request.content], source_info)
                
                print(f"📊 Analysis complete: {content_analysis.subject_area} - {len(content_analysis.main_topics)} topics")
                
                # Add enhanced fields from content analysis
                enhanced_metadata.update({
                    "subject_area": str(content_analysis.subject_area)[:100],
                    "difficulty_level": str(content_analysis.estimated_difficulty)[:50],
                    "main_topics": str([topic.name for topic in content_analysis.main_topics[:5]])[:1000],  # Top 5 topics as string
                    "key_concepts": str(list(content_analysis.key_terms.keys())[:10])[:1000],  # Top 10 key terms as string
                    "learning_objectives": str(content_analysis.learning_objectives[:3] if content_analysis.learning_objectives else [])[:1000]
                })
                
                print(f"📝 Enhanced metadata with content analysis successful")
                
            except Exception as analysis_error:
                print(f"⚠️ Content analysis failed, proceeding with basic metadata: {analysis_error}")
                # Continue with basic metadata - don't let analysis failure break storage
            
            print(f"📝 Enhanced metadata prepared: {list(enhanced_metadata.keys())}")
            print(f"📄 Content length: {len(request.content)} chars")
            
            # Store in ChromaDB with validation
            try:
                print("🔄 Adding document to collection...")
                collection.add(
                    documents=[str(request.content)],
                    metadatas=[enhanced_metadata],
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
                print(f"   Enhanced metadata keys: {list(enhanced_metadata.keys())}")
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
            
            # Use the same fresh database path pattern
            fresh_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db_v3_fresh")
            print(f"📁 ChromaDB path: {fresh_db_path}")
            
            print("🔄 Creating ChromaDB client...")
            client = chromadb.PersistentClient(path=fresh_db_path)
            
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
            
            # Enhanced semantic search for relevant content
            print(f"🔍 Searching for: '{request.question[:100]}'...")
            
            # Improve search quality with multiple approaches
            try:
                # Primary search: Standard semantic similarity
                results = collection.query(
                    query_texts=[request.question],
                    n_results=min(5, count) if 'count' in locals() else 5
                )
                
                print(f"📋 Initial search results: {len(results['documents'][0]) if results['documents'] and results['documents'][0] else 0} matches")
                
                # If we don't get good results, try expanded search terms
                if not results['documents'] or not results['documents'][0] or len(results['documents'][0]) < 2:
                    print("🔍 Expanding search with additional terms...")
                    
                    # Extract key terms from the question for better matching
                    question_words = request.question.lower().split()
                    key_terms = [word for word in question_words if len(word) > 3 and word not in ['what', 'how', 'why', 'when', 'where', 'about', 'explain', 'describe', 'tell']]
                    
                    if key_terms:
                        expanded_query = f"{request.question} {' '.join(key_terms[:3])}"
                        print(f"🔍 Expanded query: '{expanded_query[:100]}'...")
                        
                        results = collection.query(
                            query_texts=[expanded_query],
                            n_results=min(5, count) if 'count' in locals() else 5
                        )
                
                # Filter and rank results by relevance
                if results['documents'] and results['documents'][0]:
                    print(f"✅ Processing {len(results['documents'][0])} search results...")
                    
                    # Simple relevance scoring based on content quality and question matching
                    scored_results = []
                    question_lower = request.question.lower()
                    
                    for i, (doc, doc_id) in enumerate(zip(results['documents'][0], results['ids'][0])):
                        doc_lower = doc.lower()
                        
                        # Calculate relevance score
                        relevance_score = 0
                        
                        # Check for direct term matches
                        question_terms = question_lower.split()
                        for term in question_terms:
                            if len(term) > 3 and term in doc_lower:
                                relevance_score += 1
                        
                        # Prefer longer, more detailed content
                        if len(doc) > 200:
                            relevance_score += 0.5
                        
                        # ChromaDB's similarity ranking (earlier results are more similar)
                        position_score = (len(results['documents'][0]) - i) / len(results['documents'][0])
                        relevance_score += position_score
                        
                        scored_results.append({
                            'doc': doc,
                            'id': doc_id,
                            'score': relevance_score
                        })
                    
                    # Sort by relevance score
                    scored_results.sort(key=lambda x: x['score'], reverse=True)
                    
                    # Take top results
                    top_results = scored_results[:3]
                    
                    # Reconstruct results in the expected format
                    results['documents'][0] = [r['doc'] for r in top_results]
                    results['ids'][0] = [r['id'] for r in top_results]
                    
                    print(f"📊 Relevance scores: {[f'{r['score']:.2f}' for r in top_results]}")
                    
            except Exception as search_error:
                print(f"⚠️ Advanced search failed: {search_error}")
                # Fallback to simple search
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
                
                # Enhanced answer generation with OpenAI
                try:
                    print("🧠 Generating intelligent answer with OpenAI...")
                    
                    # Check if OpenAI is available
                    try:
                        from openai import OpenAI
                        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                        
                        # Create enhanced prompt with context
                        enhanced_prompt = f"""
You are an AI tutor helping a student understand their course materials. 

Based on the following content from their course materials, please answer their question in a helpful, educational way.

STUDENT'S QUESTION: {request.question}

RELEVANT COURSE CONTENT:
{relevant_content}

Please provide a clear, educational answer that:
1. Directly answers their question
2. Uses information from the provided course content
3. Explains concepts in a way that helps learning
4. Includes relevant examples or details from the content
5. Is conversational and encouraging

If the content doesn't fully answer their question, acknowledge what you can answer and suggest what additional information might be helpful.
"""
                        
                        # Generate intelligent response
                        ai_response = openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": enhanced_prompt}],
                            temperature=0.7,
                            max_tokens=500
                        )
                        
                        intelligent_answer = ai_response.choices[0].message.content
                        print("✅ OpenAI generated intelligent answer")
                        
                        return QuestionResponse(
                            answer=intelligent_answer,
                            confidence=0.9,  # Higher confidence with AI processing
                            sources=sources,
                            response_time=(datetime.now() - start_time).total_seconds()
                        )
                        
                    except Exception as openai_error:
                        print(f"⚠️ OpenAI generation failed: {openai_error}")
                        # Fallback to enhanced template-based answer
                        enhanced_answer = f"""Based on your course materials, here's what I found about your question:

**Question:** {request.question}

**Answer from your content:**
{relevant_content[:800]}

This information comes from your uploaded course materials. If you need more specific details or have follow-up questions, feel free to ask!"""
                        
                        return QuestionResponse(
                            answer=enhanced_answer,
                            confidence=0.8,
                            sources=sources,
                            response_time=(datetime.now() - start_time).total_seconds()
                        )
                        
                except Exception as enhancement_error:
                    print(f"⚠️ Answer enhancement failed: {enhancement_error}")
                    # Original simple answer as final fallback
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
