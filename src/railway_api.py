# Improved Railway API - Optimized for fast startup
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import tempfile
import uuid
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Defer heavy imports until needed
# import chromadb - loaded when needed
# import openai - loaded when needed
# Document processing imports - loaded when needed

# --- FastAPI App ---
app = FastAPI(title="CucoV2 Educational Assistant API - Clean v2", version="4.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to search for")

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    timestamp: str

class IngestResponse(BaseModel):
    message: str
    files_processed: List[str]
    status: str

class ContentUploadRequest(BaseModel):
    title: str = Field(..., description="Title of the content")
    content: str = Field(..., description="The content text to upload") 
    source: str = Field(default="chrome_extension", description="Source of the content")
    url: Optional[str] = Field(default=None, description="URL where content came from")
    content_type: str = Field(default="page", description="Type of content")
    timestamp: Optional[str] = Field(default=None, description="When content was created")

class ContentUploadResponse(BaseModel):
    status: str
    message: str
    content_id: str
    chunks_created: int

# --- Enhanced Response Generation (Core Assistant Integration) ---
def format_educational_response(question: str, unique_results: List, sources: List) -> str:
    """Generate comprehensive, well-structured response using improved OpenAI integration"""
    if not unique_results:
        return "No relevant information found in your uploaded materials. Please upload course content related to this topic."
    
    # Extract and prepare context chunks
    context_chunks = []
    for doc, metadata in unique_results[:5]:  # Use top 5 chunks
        content = doc.strip()
        
        # Skip very short or unhelpful content
        if (len(content) < 50 or 
            content.startswith(("see sg", "draw", "your diagram")) or
            content.endswith("...") or
            content.startswith("for practice applying this material")):
            continue
            
        context_chunks.append({
            'content': content,
            'source': metadata.get('title', 'Unknown Source'),
            'chapter': metadata.get('content_type', 'study_guide'),
            'lectures': metadata.get('source', 'course_material'),
            'relevance_score': 1.0 - metadata.get('distance', 0.5)  # Convert distance to relevance
        })
    
    if not context_chunks:
        return "No relevant information found in your course materials. The content may be too fragmented or focused on learning objectives rather than explanations."
    
    # Use improved OpenAI integration with proper error handling
    try:
        import openai
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("No OpenAI API key found - using fallback response")
            return _create_fallback_response(question, context_chunks)
        
        # Create client with explicit import to avoid issues
        client = OpenAI(api_key=api_key)
        
        # Build context for the prompt
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n--- Source {i}: {chunk['source']} ---\n"
            context_text += chunk['content']
            context_text += "\n"
        
        # Biology-focused system prompt
        system_prompt = """You are an expert biology tutor helping students understand complex biological concepts. 
Your responses should be:
- Clear and educational
- Well-structured with headings and bullet points
- Include step-by-step processes when applicable
- Define key terms and concepts
- Synthesize information from multiple sources into coherent explanations
- Focus on understanding rather than memorization"""

        user_prompt = f"""Question: {question}

Course Content:
{context_text}

Please provide a comprehensive, well-structured educational answer based on this course content. Aim for 400-600 words with clear organization."""

        print(f"Attempting OpenAI call for question: {question}")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1200,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"OpenAI response successful: {len(ai_response)} characters")
        return ai_response
        
    except Exception as e:
        print(f"OpenAI API error (falling back to structured response): {e}")
        return _create_fallback_response(question, context_chunks)

def _create_fallback_response(question: str, context_chunks: List) -> str:
    """Create comprehensive fallback response when AI is not available"""
    if not context_chunks:
        return f"I couldn't find relevant content to answer your question about '{question}'. Try rephrasing or asking about a different topic."
    
    # Create comprehensive educational answer from context chunks
    answer_parts = [f"# {question.title()}\n"]
    answer_parts.append("Based on your course materials, here's a comprehensive explanation:\n")
    
    # Group and organize content by relevance
    high_relevance = [chunk for chunk in context_chunks if chunk.get('relevance_score', 0) > 0.7]
    medium_relevance = [chunk for chunk in context_chunks if 0.4 <= chunk.get('relevance_score', 0) <= 0.7]
    
    # Use high relevance content primarily
    primary_chunks = high_relevance[:2] if high_relevance else context_chunks[:2]
    
    for i, chunk in enumerate(primary_chunks, 1):
        answer_parts.append(f"## Key Information from {chunk['source']}\n")
        
        content = chunk['content']
        
        # Clean and format the content better
        content = content.replace('\n\n', '\n').strip()
        
        # If content is very long, extract key sentences
        if len(content) > 500:
            sentences = content.split('. ')
            # Prioritize sentences with key biological terms
            key_sentences = []
            for sentence in sentences:
                if any(term in sentence.lower() for term in [
                    'dna', 'replication', 'process', 'mechanism', 'enzyme', 'structure',
                    'protein', 'synthesis', 'occurs', 'involves', 'during', 'formation'
                ]):
                    key_sentences.append(sentence.strip())
            
            if key_sentences:
                content = '. '.join(key_sentences[:4]) + '.'
            else:
                content = '. '.join(sentences[:3]) + '.'
        
        answer_parts.append(content + "\n")
    
    # Add supplementary information if available
    if medium_relevance and len(primary_chunks) < 2:
        answer_parts.append("## Additional Context\n")
        supp_content = medium_relevance[0]['content'][:300]
        if len(medium_relevance[0]['content']) > 300:
            supp_content += "..."
        answer_parts.append(supp_content + "\n")
    
    # Add educational note
    answer_parts.append("---")
    answer_parts.append("*This explanation was compiled from your study materials. The content covers the key concepts needed to understand this topic.*")
    
    return "\n".join(answer_parts)

# --- Auto-load Knowledge Base ---
async def load_persistent_knowledge_base():
    """Load study guides from knowledge_base folder on startup"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
        except:
            collection = client.create_collection("canvas_content")
        
        # Check if knowledge base is already loaded
        existing_count = collection.count()
        if existing_count > 0:
            print(f"Knowledge base already has {existing_count} documents, skipping auto-load")
            return
        
        knowledge_base_path = Path("knowledge_base")
        if not knowledge_base_path.exists():
            knowledge_base_path = Path("../knowledge_base")  # Alternative path for deployment
        
        if not knowledge_base_path.exists():
            print("No knowledge_base folder found")
            return
        
        loaded_count = 0
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        # Load all .txt files from knowledge_base folder
        for txt_file in knowledge_base_path.glob("*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) < 50:
                    continue
                
                # Chunk the content
                chunks = chunk_text(content, max_chunk_size=800, overlap=100)
                
                for i, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 20:
                        doc_id = f"{txt_file.stem}_chunk_{i}_{uuid.uuid4().hex[:8]}"
                        all_documents.append(chunk)
                        all_metadatas.append({
                            "title": txt_file.stem.replace('_', ' ').title(),
                            "source": "persistent_knowledge_base",
                            "content_type": "study_guide",
                            "url": "",
                            "chunk_index": i,
                            "timestamp": datetime.now().isoformat(),
                            "content_id": txt_file.stem
                        })
                        all_ids.append(doc_id)
                
                loaded_count += 1
                print(f"Loaded: {txt_file.name}")
                
            except Exception as e:
                print(f"Error loading {txt_file.name}: {e}")
                continue
        
        # Add all documents to ChromaDB
        if all_documents:
            collection.add(
                documents=all_documents,
                metadatas=all_metadatas,
                ids=all_ids
            )
            print(f"Auto-loaded {loaded_count} study guides with {len(all_documents)} chunks to knowledge base")
        else:
            print("No valid content found in knowledge_base folder")
            
    except Exception as e:
        print(f"Error auto-loading knowledge base: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize knowledge base on startup"""
    await load_persistent_knowledge_base()

# --- Health Check ---
@app.get("/")
async def root():
    """Simple root endpoint"""
    return {"status": "Canvas AI Assistant API", "version": "4.1.0"}

@app.get("/health")
def health_check():
    """Minimal health check for Railway"""
    return {"status": "ok"}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service testing"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0",
        "services": {}
    }
    
    # Test ChromaDB
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
            count = collection.count()
            health_status["services"]["chromadb"] = f"connected (collection exists, {count} docs)"
        except Exception:
            health_status["services"]["chromadb"] = "connected (ready for collections)"
        
    except Exception as e:
        health_status["services"]["chromadb"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check OpenAI API key availability (without testing API call)
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            health_status["services"]["openai"] = "API key configured"
        else:
            health_status["services"]["openai"] = "No API key found"
    except Exception as e:
        health_status["services"]["openai"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

# --- Content Ingestion ---
@app.post("/ingest-content", response_model=IngestResponse)
async def ingest_content(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """Ingest educational content from uploaded files"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
        except:
            collection = client.create_collection("canvas_content")
        
        processed_files = []
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        for file in files:
            try:
                content = await file.read()
                
                # Process different file types
                if file.filename.endswith('.pdf'):
                    text = extract_pdf_text(content)
                elif file.filename.endswith('.docx'):
                    text = extract_docx_text(content)
                elif file.filename.endswith('.txt'):
                    text = content.decode('utf-8')
                elif file.filename.endswith('.csv'):
                    text = extract_csv_text(content)
                else:
                    continue
                
                if not text or len(text.strip()) < 10:
                    continue
                
                # Chunk the content
                chunks = chunk_text(text, max_chunk_size=800, overlap=100)
                
                for i, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 20:
                        doc_id = f"{file.filename}_{i}_{uuid.uuid4().hex[:8]}"
                        all_documents.append(chunk)
                        all_metadatas.append({
                            "source": file.filename,
                            "chunk_index": i,
                            "title": file.filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ').title(),
                            "content_type": "educational_content"
                        })
                        all_ids.append(doc_id)
                
                processed_files.append(file.filename)
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                continue
        
        # Add all documents to ChromaDB
        if all_documents:
            collection.add(
                documents=all_documents,
                metadatas=all_metadatas,
                ids=all_ids
            )
        
        return IngestResponse(
            message=f"Successfully processed {len(processed_files)} files with {len(all_documents)} content chunks",
            files_processed=processed_files,
            status="success"
        )
        
    except Exception as e:
        print(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest content: {str(e)}")

# --- JSON Content Upload (for Chrome Extension) ---
@app.post("/upload-content", response_model=ContentUploadResponse)
async def upload_content(request: ContentUploadRequest):
    """Upload content from JSON (used by Chrome extension)"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
        except:
            collection = client.create_collection("canvas_content")
        
        # Validate content
        if not request.content or len(request.content.strip()) < 20:
            raise HTTPException(status_code=400, detail="Content too short or empty")
        
        # Chunk the content
        chunks = chunk_text(request.content, max_chunk_size=800, overlap=100)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid content chunks created")
        
        # Prepare documents for ChromaDB
        all_documents = []
        all_metadatas = []
        all_ids = []
        content_id = uuid.uuid4().hex[:12]
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 20:
                doc_id = f"{content_id}_chunk_{i}"
                all_documents.append(chunk)
                all_metadatas.append({
                    "title": request.title,
                    "source": request.source,
                    "content_type": request.content_type,
                    "url": request.url or "",
                    "chunk_index": i,
                    "timestamp": request.timestamp or datetime.now().isoformat(),
                    "content_id": content_id
                })
                all_ids.append(doc_id)
        
        if not all_documents:
            raise HTTPException(status_code=400, detail="No valid content chunks to upload")
        
        # Add to ChromaDB
        collection.add(
            documents=all_documents,
            metadatas=all_metadatas,
            ids=all_ids
        )
        
        return ContentUploadResponse(
            status="success",
            message=f"Successfully uploaded '{request.title}' with {len(all_documents)} chunks",
            content_id=content_id,
            chunks_created=len(all_documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Content upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload content: {str(e)}")

# --- Query Processing ---
@app.post("/query", response_model=QueryResponse)
async def query_content(request: QueryRequest):
    """Query the educational content with enhanced search"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_collection("canvas_content")
        
        if collection.count() == 0:
            return QueryResponse(
                answer="No educational content has been uploaded yet. Please upload your course materials first.",
                sources=[],
                timestamp=datetime.now().isoformat()
            )
        
        # Enhanced search with topic-specific terms
        query_terms = [request.question]
        q_lower = request.question.lower()
        
        # Add specific search terms for different biology topics
        if any(term in q_lower for term in ["protein", "structure", "level"]):
            query_terms.extend([
                "primary secondary tertiary quaternary structure",
                "protein folding levels",
                "amino acid structure"
            ])
        elif any(term in q_lower for term in ["dna", "replication", "replicate"]):
            query_terms.extend([
                "DNA replication process",
                "replication fork leading lagging strand",
                "DNA polymerase helicase primase",
                "semiconservative replication"
            ])
        elif any(term in q_lower for term in ["cell", "division", "mitosis", "meiosis"]):
            query_terms.extend([
                "cell division phases",
                "mitosis meiosis stages",
                "chromosome segregation"
            ])
        
        # Perform multiple searches and combine results
        all_results = []
        for query_term in query_terms:
            try:
                results = collection.query(
                    query_texts=[query_term],
                    n_results=8  # Get more results per query
                )
                
                if results['documents'] and results['documents'][0]:
                    for doc, metadata, distance in zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    ):
                        all_results.append((doc, {**metadata, 'distance': distance}))
            except Exception as e:
                print(f"Search error for '{query_term}': {e}")
                continue
        
        if not all_results:
            return QueryResponse(
                answer="No relevant information found for your question. Try rephrasing or upload more detailed course materials.",
                sources=[],
                timestamp=datetime.now().isoformat()
            )
        
        # Remove duplicates and prioritize quality content with smarter filtering
        unique_results = []
        seen_content = set()
        
        for doc, metadata in all_results:
            content_key = doc[:150].lower().strip()
            doc_text = doc.strip()
            
            if content_key not in seen_content and len(doc_text) > 40:
                # Less aggressive filtering - allow more content through
                if not (doc_text.startswith("for practice applying this material") or
                        doc_text.startswith("complete the practice quiz") or
                        doc_text.endswith("...") or
                        len(doc_text) < 50):
                    seen_content.add(content_key)
                    unique_results.append((doc, metadata))
        
        # Sort by relevance (distance) and content quality
        unique_results.sort(key=lambda x: (
            x[1].get('distance', 1.0),  # Primary: relevance
            -len(x[0]),  # Secondary: longer content preferred
            # Boost content that looks explanatory
            -10 if any(word in x[0].lower() for word in ["process", "mechanism", "involves", "occurs"]) else 0
        ))
        unique_results = unique_results[:8]  # Get more results for better coverage
        
        # Extract sources
        sources = list(set([metadata['title'] for _, metadata in unique_results]))
        
        # Generate response
        answer = format_educational_response(request.question, unique_results, sources)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# --- Clear Database ---
@app.post("/clear-documents")
async def clear_all_documents():
    """Clear all documents from ChromaDB"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            client.delete_collection("canvas_content")
            return {"message": "All documents cleared successfully", "status": "success"}
        except Exception:
            return {"message": "Collection was already empty or didn't exist", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear documents: {str(e)}")

# --- List Documents ---
@app.get("/list-documents")
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection("canvas_content")
        except Exception:
            return {"documents": [], "count": 0}
        
        # Get all documents with metadata
        results = collection.get(include=["metadatas"])
        
        if not results or not results["metadatas"]:
            return {"documents": [], "count": 0}
        
        # Process documents and group by title
        documents_map = {}
        
        for metadata in results["metadatas"]:
            if not metadata:
                continue
                
            title = metadata.get("title", "Unknown Document")
            timestamp = metadata.get("timestamp", "")
            content_type = metadata.get("content_type", "unknown")
            
            if title not in documents_map:
                documents_map[title] = {
                    "title": title,
                    "timestamp": timestamp,
                    "content_type": content_type,
                    "chunk_count": 1
                }
            else:
                documents_map[title]["chunk_count"] += 1
        
        documents = list(documents_map.values())
        
        # Sort by timestamp (newest first)
        documents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "documents": documents,
            "count": len(documents)
        }
        
    except Exception as e:
        print(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

# --- Utility Functions ---
def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        from io import BytesIO
        from PyPDF2 import PdfReader
        
        pdf_file = BytesIO(content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX content"""
    try:
        from io import BytesIO
        from docx import Document
        
        doc_file = BytesIO(content)
        doc = Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

def extract_csv_text(content: bytes) -> str:
    """Extract text from CSV content"""
    try:
        import csv
        from io import StringIO
        
        csv_text = content.decode('utf-8')
        csv_reader = csv.reader(StringIO(csv_text))
        text = ""
        for row in csv_reader:
            text += " ".join(row) + "\n"
        return text
    except Exception as e:
        print(f"CSV extraction error: {e}")
        return ""

def chunk_text(text: str, max_chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Find the last sentence boundary within the chunk
        chunk = text[start:end]
        last_period = chunk.rfind('.')
        last_newline = chunk.rfind('\n')
        
        boundary = max(last_period, last_newline)
        if boundary > start + max_chunk_size // 2:
            end = start + boundary + 1
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 20]

# --- Debug Endpoints ---
@app.get("/debug/chromadb")
async def debug_chromadb():
    """Debug ChromaDB status and content"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "chroma_path": chroma_path,
            "path_exists": os.path.exists(chroma_path)
        }
        
        if os.path.exists(chroma_path):
            client = chromadb.PersistentClient(path=chroma_path)
            try:
                collection = client.get_collection("canvas_content")
                debug_info["canvas_collection"] = f"Found with {collection.count()} documents"
                
                if collection.count() > 0:
                    test_results = collection.query(query_texts=["protein"], n_results=1)
                    debug_info["test_query"] = "Success" if test_results['documents'][0] else "No results"
                else:
                    debug_info["test_query"] = "Collection is empty"
            except Exception as e:
                debug_info["canvas_collection"] = f"Error: {str(e)}"
        else:
            debug_info["canvas_collection"] = "ChromaDB path does not exist"
        
        return debug_info
        
    except Exception as e:
        return {"error": f"Debug failed: {str(e)}"}

@app.get("/debug/openai-test")
async def debug_openai_test():
    """Debug OpenAI integration specifically"""
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "api_key_present": bool(os.getenv("OPENAI_API_KEY")),
        "api_key_length": len(os.getenv("OPENAI_API_KEY", "")),
    }
    
    try:
        import openai
        debug_info["openai_module"] = "imported successfully"
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            debug_info["error"] = "No API key in environment"
            return debug_info
            
        # Try explicit initialization without any other parameters
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            debug_info["client_init"] = "successful"
        except Exception as init_error:
            debug_info["client_init_error"] = str(init_error)
            return debug_info
        
        # Test simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        
        debug_info["api_test"] = f"successful: {response.choices[0].message.content}"
        
    except Exception as e:
        debug_info["error"] = str(e)
        debug_info["error_type"] = type(e).__name__
        
    return debug_info

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    
    # Railway optimization
    log_level = "info" if os.getenv("RAILWAY_ENVIRONMENT") else "debug"
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level=log_level,
        access_log=False  # Reduce logging overhead
    )
