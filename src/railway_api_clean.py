# Improved Railway API
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import chromadb
import tempfile
import uuid
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# OpenAI import
import openai

# Document processing imports
from PyPDF2 import PdfReader
from docx import Document
import csv
from io import StringIO, BytesIO

# --- Configuration ---
app = FastAPI(title="CucoV2 Educational Assistant API", version="4.0.0")

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

# --- Enhanced Response Generation ---
def format_educational_response(question: str, unique_results: List, sources: List) -> str:
    """Generate concise, focused response using OpenAI with enhanced search results"""
    if not unique_results:
        return "No relevant information found in your uploaded materials. Please upload course content related to this topic."
    
    # Enhanced search targeting for specific topics
    search_terms = []
    q_lower = question.lower()
    
    # Protein structure specific terms
    if any(term in q_lower for term in ["protein", "structure", "level"]):
        search_terms.extend(["primary", "secondary", "tertiary", "quaternary"])
    
    # Extract most relevant content based on distance/relevance
    relevant_content = []
    for doc, metadata in unique_results[:3]:  # Top 3 most relevant
        content = doc.strip()
        if len(content) > 50:  # Meaningful content only
            # Score content by distance if available
            distance = metadata.get('distance', 1.0)
            if distance < 0.5:  # High relevance threshold
                relevant_content.append(content)
    
    if not relevant_content:
        # Fallback to basic content if no high-relevance found
        relevant_content = [doc.strip() for doc, _ in unique_results[:1] if len(doc.strip()) > 50]
    
    # Use OpenAI for concise formatting only
    if relevant_content:
        try:
            combined_content = "\n".join(relevant_content[:2])  # Limit content
            
            prompt = f"""Based on this course content, provide a direct answer to: "{question}"

Course Content:
{combined_content[:1000]}

Requirements:
- Answer the question directly and concisely
- Use ONLY the provided course content
- Keep response under 200 words
- Focus on key facts, not lengthy explanations
- If the content mentions specific levels or categories, list them clearly"""

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI formatting error: {e}")
            # Fallback to simple response
            return f"Based on your course materials:\n\n{relevant_content[0][:300]}..."
    
    # Simple fallback response
    response = f"Based on your course materials:\n\n"
    for i, content in enumerate(relevant_content[:1], 1):
        response += f"{content.strip()}"
        if not content.strip().endswith('.'):
            response += "..."
        response += "\n"
    
    return response.strip()

# --- Health Check ---
@app.get("/")
async def health_check():
    """Health check endpoint with ChromaDB status"""
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
    
    # Test OpenAI
    try:
        import openai
        health_status["services"]["openai"] = "available"
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
        
        # Add specific search terms for protein structure
        if any(term in q_lower for term in ["protein", "structure", "level"]):
            query_terms.extend([
                "primary secondary tertiary quaternary structure",
                "protein folding levels",
                "amino acid structure"
            ])
        
        # Perform multiple searches and combine results
        all_results = []
        for query_term in query_terms:
            try:
                results = collection.query(
                    query_texts=[query_term],
                    n_results=5
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
        
        # Remove duplicates and sort by relevance
        unique_results = []
        seen_content = set()
        
        for doc, metadata in all_results:
            content_key = doc[:100].lower().strip()
            if content_key not in seen_content and len(doc.strip()) > 50:
                seen_content.add(content_key)
                unique_results.append((doc, metadata))
        
        # Sort by distance/relevance and take top results
        unique_results.sort(key=lambda x: x[1].get('distance', 1.0))
        unique_results = unique_results[:3]  # Top 3 most relevant
        
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

# --- Utility Functions ---
def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF content"""
    try:
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
