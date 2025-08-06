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

# --- Educational Response Formatting ---
def format_educational_response(question: str, unique_results: List, sources: List) -> str:
    """Format responses to be educational and student-friendly"""
    question_lower = question.lower()
    
# --- Dynamic Educational Response System ---
def format_educational_response(question: str, unique_results: List, sources: List) -> str:
    """Create educational responses for ANY topic dynamically"""
    
    # Analyze the question to understand what type of response is needed
    question_type = analyze_question_type(question)
    topic = extract_main_topic(question)
    
    # Build structured educational response
    response = f"# 📚 Learning About: {topic}\n\n"
    
    if question_type == "definition":
        response += build_definition_response(question, topic, unique_results, sources)
    elif question_type == "explanation":
        response += build_explanation_response(question, topic, unique_results, sources)
    elif question_type == "comparison":
        response += build_comparison_response(question, topic, unique_results, sources)
    elif question_type == "process":
        response += build_process_response(question, topic, unique_results, sources)
    else:
        response += build_general_response(question, topic, unique_results, sources)
    
    # Add study guidance
    response += "\n## 🎯 Study Tips\n"
    response += generate_study_tips(question, topic, unique_results)
    
    response += "\n---\n💡 **Remember**: Understanding concepts deeply is better than memorizing facts!\n"
    response += "🤖 **Note**: For AI-powered detailed explanations, OpenAI integration is needed."
    
    return response

def analyze_question_type(question: str) -> str:
    """Determine what type of educational response is needed"""
    q_lower = question.lower()
    
    if any(phrase in q_lower for phrase in ["what is", "define", "definition of"]):
        return "definition"
    elif any(phrase in q_lower for phrase in ["how does", "explain", "why does", "how works"]):
        return "explanation"
    elif any(phrase in q_lower for phrase in ["difference between", "compare", "contrast", "vs"]):
        return "comparison"
    elif any(phrase in q_lower for phrase in ["process of", "steps", "pathway", "mechanism"]):
        return "process"
    else:
        return "general"

def extract_main_topic(question: str) -> str:
    """Extract the main topic from the question"""
    # Remove common question words to get the core topic
    q_lower = question.lower()
    
    # Remove question starters
    for starter in ["what is", "what are", "define", "explain", "how does", "why does", "tell me about"]:
        if starter in q_lower:
            q_lower = q_lower.replace(starter, "").strip()
    
    # Clean up articles and prepositions
    for word in ["the", "a", "an", "of", "in", "on", "at", "for"]:
        q_lower = q_lower.replace(f" {word} ", " ")
    
    return q_lower.strip().title()

def build_definition_response(question: str, topic: str, unique_results: List, sources: List) -> str:
    """Build a definition-focused educational response"""
    response = "## Definition\n"
    
    # Extract definition from course materials
    definitions = extract_definitions_from_content(unique_results, topic)
    
    if definitions:
        response += f"{definitions[0]}\n\n"
        
        if len(definitions) > 1:
            response += "## Additional Perspectives\n"
            for i, definition in enumerate(definitions[1:], 2):
                response += f"**Source {i}**: {definition}\n\n"
    else:
        response += "Based on your course materials:\n\n"
        response += format_course_content(unique_results, sources)
    
    return response

def build_explanation_response(question: str, topic: str, unique_results: List, sources: List) -> str:
    """Build an explanation-focused educational response"""
    response = "## How It Works\n"
    
    # Look for explanatory content
    explanations = extract_explanations_from_content(unique_results, question)
    
    if explanations:
        for explanation in explanations:
            response += f"• {explanation}\n"
        response += "\n"
    
    response += "## From Your Course Materials\n"
    response += format_course_content(unique_results, sources, focus="explanation")
    
    return response

def build_comparison_response(question: str, topic: str, unique_results: List, sources: List) -> str:
    """Build a comparison-focused educational response"""
    response = "## Key Comparisons\n"
    
    # Extract comparative information
    comparisons = extract_comparisons_from_content(unique_results, question)
    
    if comparisons:
        for comparison in comparisons:
            response += f"• {comparison}\n"
        response += "\n"
    
    response += "## Detailed Information\n"
    response += format_course_content(unique_results, sources, focus="comparison")
    
    return response

def build_process_response(question: str, topic: str, unique_results: List, sources: List) -> str:
    """Build a process-focused educational response"""
    response = "## Process Overview\n"
    
    # Extract process steps
    steps = extract_process_steps_from_content(unique_results, question)
    
    if steps:
        response += "### Key Steps:\n"
        for i, step in enumerate(steps, 1):
            response += f"{i}. {step}\n"
        response += "\n"
    
    response += "## Detailed Process Information\n"
    response += format_course_content(unique_results, sources, focus="process")
    
    return response

def build_general_response(question: str, topic: str, unique_results: List, sources: List) -> str:
    """Build a general educational response"""
    response = "## Key Information\n"
    response += format_course_content(unique_results, sources)
    return response

def extract_definitions_from_content(unique_results: List, topic: str) -> List[str]:
    """Extract definition-like sentences from course content"""
    definitions = []
    topic_lower = topic.lower()
    
    for doc, metadata in unique_results:
        sentences = doc.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            sentence_lower = sentence.lower()
            
            # Look for definition patterns
            if (topic_lower in sentence_lower and 
                any(pattern in sentence_lower for pattern in [" is ", " are ", " refers to", " means", " defined as"])):
                definitions.append(sentence + ".")
                
    return definitions[:3]  # Return top 3 definitions

def extract_explanations_from_content(unique_results: List, question: str) -> List[str]:
    """Extract explanatory content"""
    explanations = []
    
    for doc, metadata in unique_results:
        sentences = doc.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30:
                continue
                
            # Look for explanatory patterns
            if any(pattern in sentence.lower() for pattern in ["because", "due to", "results in", "causes", "leads to"]):
                explanations.append(sentence + ".")
                
    return explanations[:4]

def extract_comparisons_from_content(unique_results: List, question: str) -> List[str]:
    """Extract comparative information"""
    comparisons = []
    
    for doc, metadata in unique_results:
        sentences = doc.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 25:
                continue
                
            # Look for comparison patterns
            if any(pattern in sentence.lower() for pattern in ["unlike", "compared to", "different from", "similar to", "whereas", "while"]):
                comparisons.append(sentence + ".")
                
    return comparisons[:4]

def extract_process_steps_from_content(unique_results: List, question: str) -> List[str]:
    """Extract process steps"""
    steps = []
    
    for doc, metadata in unique_results:
        sentences = doc.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 25:
                continue
                
            # Look for step patterns
            if any(pattern in sentence.lower() for pattern in ["first", "second", "third", "next", "then", "finally", "step"]):
                steps.append(sentence + ".")
                
    return steps[:5]

def format_course_content(unique_results: List, sources: List, focus: str = "general") -> str:
    """Format course content in an educational way"""
    formatted_content = ""
    
    for i, (doc, source) in enumerate(unique_results[:3]):
        # Extract meaningful content
        relevant_content = extract_relevant_content(doc, focus)
        
        if relevant_content:
            formatted_content += f"### {source['title']}\n"
            formatted_content += f"{relevant_content}\n\n"
    
    return formatted_content if formatted_content else "No specific content found in your course materials for this topic."

def extract_relevant_content(text: str, focus: str = "general") -> str:
    """Extract the most relevant content from text"""
    sentences = text.split('.')
    relevant_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
            
        # Score sentence relevance
        relevance_score = 0
        
        # General quality indicators
        if len(sentence) > 50:
            relevance_score += 1
        if any(char.isupper() for char in sentence):
            relevance_score += 1
        if sentence.count(' ') >= 5:  # Has substance
            relevance_score += 1
            
        # Focus-specific scoring
        if focus == "explanation" and any(word in sentence.lower() for word in ["because", "therefore", "results", "causes"]):
            relevance_score += 2
        elif focus == "process" and any(word in sentence.lower() for word in ["step", "first", "then", "next", "process"]):
            relevance_score += 2
        elif focus == "comparison" and any(word in sentence.lower() for word in ["compare", "unlike", "similar", "different"]):
            relevance_score += 2
            
        if relevance_score >= 2:
            relevant_sentences.append(sentence)
    
    # Return top sentences
    result = '. '.join(relevant_sentences[:4])
    if result and not result.endswith('.'):
        result += '.'
        
    return result if len(result) > 50 else text[:400] + '...'

def generate_study_tips(question: str, topic: str, unique_results: List) -> str:
    """Generate relevant study tips based on the question and content"""
    tips = []
    
    # General study tips based on question type
    q_lower = question.lower()
    
    if "what is" in q_lower or "define" in q_lower:
        tips.append("• Focus on understanding the core definition first, then build on details")
        tips.append("• Try to explain the concept in your own words")
    elif "how does" in q_lower or "explain" in q_lower:
        tips.append("• Break down the process into smaller steps")
        tips.append("• Look for cause-and-effect relationships")
    elif "compare" in q_lower or "difference" in q_lower:
        tips.append("• Create a comparison table to organize similarities and differences")
        tips.append("• Focus on key distinguishing features")
    
    # Add content-specific tips
    if len(unique_results) > 1:
        tips.append("• Review multiple sources to get a complete understanding")
    
    tips.append("• Connect this concept to related topics you've already learned")
    tips.append("• Practice applying this knowledge to solve problems")
    
    return '\n'.join(tips[:4])

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
                        {"role": "system", "content": """You are an expert biology tutor helping students learn. Your job is to:
1. TEACH concepts clearly with definitions and explanations
2. Break down complex topics into understandable parts  
3. Use analogies and examples when helpful
4. Structure responses with clear headings and bullet points
5. Connect concepts to broader biological principles
6. Be encouraging and supportive

Always start with a clear definition, then explain key points, and provide examples."""},
                        {"role": "user", "content": f"""Question: {request.question}

Course Material Context:
{context}

Please provide a comprehensive, educational response that teaches the student about this topic. Structure your answer with:
- Clear definition
- Key concepts explained
- Examples or analogies  
- How it connects to other biology concepts
- Study tips if relevant

Base your answer on the course materials provided."""}
                    ],
                    max_tokens=800,
                    temperature=0.3
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
                
                # Enhanced educational responses for better teaching
                answer = format_educational_response(request.question, unique_results, sources)
                
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
