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
    sections: Optional[Dict[str, Any]] = None  # Parsed sections for better display

class IngestResponse(BaseModel):
    message: str
    files_processed: List[str]
    status: str

class QuizAnswerRequest(BaseModel):
    answer: str = Field(..., description="User's answer to the quiz question")
    session_id: Optional[str] = Field(default=None, description="Quiz session ID")
    question_index: int = Field(default=0, description="Current question index")

class QuizConfigRequest(BaseModel):
    config_input: str = Field(..., description="User's quiz configuration preferences")
    available_topics: List[str] = Field(default=[], description="Available topics from previous request")

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

def parse_educational_response(response_text: str) -> Dict[str, Any]:
    """Parse the educational response into structured sections for better display"""
    sections = {
        "title": "",
        "learning_objective": "",
        "quick_summary": "",
        "study_info": "",
        "definition_overview": "",
        "key_concepts": [],
        "key_terms": [],
        "think_about": [],
        "related_topics": [],
        "formatted_text": response_text
    }
    
    try:
        lines = response_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Parse title
            if line.startswith('# '):
                sections["title"] = line[2:].strip()
                
            # Parse learning objective
            elif line.startswith('> **📚 Learning Objective:**'):
                sections["learning_objective"] = line.replace('> **📚 Learning Objective:**', '').strip()
                
            # Parse quick summary section
            elif line.startswith('## 🎯 Quick Summary'):
                current_section = "quick_summary"
                current_content = []
                
            # Parse study time info
            elif line.startswith('**⏱️ Study Time:**'):
                sections["study_info"] = line.replace('**⏱️ Study Time:**', '').strip()
                
            # Parse definition section
            elif line.startswith('## 🔍 Definition & Overview'):
                current_section = "definition_overview"
                current_content = []
                
            # Parse key concepts section
            elif line.startswith('## 🔬 Key Concepts'):
                current_section = "key_concepts"
                current_content = []
                
            # Parse individual concepts
            elif line.startswith('### '):
                if current_section == "key_concepts":
                    if current_content:
                        sections["key_concepts"].append({
                            "title": current_content[0] if current_content else "",
                            "content": "\n".join(current_content[1:]) if len(current_content) > 1 else ""
                        })
                    current_content = [line[4:].strip()]  # Remove ### and emoji
                else:
                    current_content.append(line)
                    
            # Parse key terms table
            elif line.startswith('## 💡 Key Terms'):
                current_section = "key_terms"
                current_content = []
                
            # Parse think about section
            elif line.startswith('## 🤔 Think About'):
                current_section = "think_about"
                current_content = []
                
            # Parse related topics section
            elif line.startswith('## 🔗 Related Topics'):
                current_section = "related_topics"
                current_content = []
                
            # Handle table rows for key terms
            elif current_section == "key_terms" and '|' in line and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3 and parts[0] not in ['Term', 'Definition']:
                    sections["key_terms"].append({
                        "term": parts[0],
                        "definition": parts[1],
                        "importance": parts[2] if len(parts) > 2 else ""
                    })
                    
            # Handle bullet points
            elif line.startswith('- ') and current_section in ["think_about", "related_topics"]:
                sections[current_section].append(line[2:].strip())
                
            # Add to current content
            elif line and current_section and not line.startswith('#') and not line.startswith('**⏱️'):
                current_content.append(line)
        
        # Add last section content
        if current_section and current_content:
            if current_section == "key_concepts":
                sections["key_concepts"].append({
                    "title": current_content[0] if current_content else "",
                    "content": "\n".join(current_content[1:]) if len(current_content) > 1 else ""
                })
            elif current_section in ["quick_summary", "definition_overview"]:
                sections[current_section] = "\n".join(current_content)
                
    except Exception as e:
        print(f"Error parsing response: {e}")
        # Return basic structure if parsing fails
        
    return sections

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
        
        # Enhanced educational system prompt with better formatting
        system_prompt = """You are an expert educational tutor helping students master complex academic concepts. 
Create responses that are:
- Visually structured with clear sections and emojis
- Student-friendly with learning objectives and summaries
- Include difficulty indicators and study guidance
- Define key terms in a glossary format
- Use step-by-step explanations for processes
- Add "Think About This" sections for deeper understanding
- Connect to related topics for comprehensive learning
- Use proper line breaks and spacing for readability"""

        user_prompt = f"""Question: {question}

Course Content:
{context_text}

Create a comprehensive, visually appealing educational response using this EXACT format with proper spacing:

# 🧬 [Main Topic Title]

> **📚 Learning Objective:** By the end of this explanation, you'll understand [key learning goal].

---

## 🎯 Quick Summary

[2-3 sentence overview of the topic]

**⏱️ Study Time:** [X-Y minutes] | **📊 Difficulty:** [🟢 Basic/🟡 Intermediate/🔴 Advanced]

---

## 🔍 Definition & Overview

[Clear definition and context with proper paragraphs]

---

## 🔬 Key Concepts You Need to Know

### 1. 📝 [Concept Name]

- **What it is:** [explanation]
- **Why it matters:** [relevance]  
- **Key terms:** [important vocabulary]

### 2. ⚙️ [Process/Mechanism Name]

**Step-by-step breakdown:**

1. **[Step 1]** 🚀 - [description]
2. **[Step 2]** ➡️ - [description]  
3. **[Step 3]** 🏁 - [description]

---

## 💡 Key Terms to Remember

| Term | Definition | Why Important |
|------|------------|---------------|
| [Term 1] | [Definition] | [Significance] |
| [Term 2] | [Definition] | [Significance] |

---

## 🤔 Think About This

- [Thought-provoking question 1]
- [Connection or application question 2]

---

## 🔗 Related Topics to Explore Next

- [Related topic 1]
- [Related topic 2]  
- [Related topic 3]

IMPORTANT: Use double line breaks (\\n\\n) between all major sections and proper spacing for excellent readability. Make it engaging for students with clear visual separation."""

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
        return f"# ❓ {question.title()}\n\n> **📚 Learning Objective:** Find relevant course materials to answer this question.\n\n---\n\n## 🎯 Quick Summary\nI couldn't find relevant content to answer your question about '{question}'. Try rephrasing or asking about a different topic.\n\n**💡 Tip:** Upload more course materials or try asking about topics in your study guides."
    
    # Determine topic and difficulty
    topic_title = question.title()
    if any(term in question.lower() for term in ['dna', 'replication', 'protein', 'enzyme']):
        subject_emoji = "🧬"
        difficulty = "🟡 Intermediate"
    elif any(term in question.lower() for term in ['basic', 'simple', 'definition', 'what is']):
        subject_emoji = "📚"
        difficulty = "🟢 Basic"
    else:
        subject_emoji = "🔬"
        difficulty = "🟡 Intermediate"
    
    # Create enhanced educational answer from context chunks
    answer_parts = [f"# {subject_emoji} {topic_title}\n"]
    answer_parts.append(f"> **📚 Learning Objective:** By the end of this explanation, you'll understand the key concepts related to {question.lower()}.\n")
    answer_parts.append("---\n")
    
    # Quick Summary
    answer_parts.append("## 🎯 Quick Summary")
    answer_parts.append("Based on your course materials, here's what we found about this topic:\n")
    answer_parts.append(f"**⏱️ Study Time:** 3-5 minutes | **📊 Difficulty:** {difficulty}\n")
    answer_parts.append("---\n")
    
    # Group and organize content by relevance
    high_relevance = [chunk for chunk in context_chunks if chunk.get('relevance_score', 0) > 0.7]
    medium_relevance = [chunk for chunk in context_chunks if 0.4 <= chunk.get('relevance_score', 0) <= 0.7]
    
    # Use high relevance content primarily
    primary_chunks = high_relevance[:2] if high_relevance else context_chunks[:2]
    
    answer_parts.append("## 🔍 Key Information from Course Materials\n")
    
    for i, chunk in enumerate(primary_chunks, 1):
        answer_parts.append(f"### {i}. 📝 From {chunk['source']}\n")
        
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
        answer_parts.append("## 📖 Additional Context\n")
        supp_content = medium_relevance[0]['content'][:300]
        if len(medium_relevance[0]['content']) > 300:
            supp_content += "..."
        answer_parts.append(supp_content + "\n")
    
    # Add study guidance
    answer_parts.append("---\n")
    answer_parts.append("## 💡 Study Tips\n")
    answer_parts.append("- Review the key concepts highlighted above\n")
    answer_parts.append("- Look for connections to other topics in your course materials\n")
    answer_parts.append("- Ask follow-up questions to deepen your understanding\n")
    
    answer_parts.append("---\n")
    answer_parts.append("*📖 This explanation was compiled from your study materials. The content covers the key concepts needed to understand this topic.*")
    
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

@app.post("/test-quiz-detection")
async def test_quiz_detection(request: QueryRequest):
    """Test quiz detection without full CoreAssistant initialization"""
    try:
        # Import the enhanced core assistant with quiz capabilities
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from core_assistant import CoreAssistant
        
        # Test just the quiz detection logic without initializing ChromaDB
        temp_assistant = CoreAssistant.__new__(CoreAssistant)  # Create without __init__
        
        # Use the internal quiz detection method
        quiz_result = temp_assistant._detect_quiz_intent(request.question)
        
        return {
            "status": "success",
            "question": request.question,
            "quiz_detected": quiz_result.get('is_quiz_request', False),
            "confidence": quiz_result.get('confidence', 'unknown'),
            "parameters": str(quiz_result.get('parameters', {})),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
def health_check():
    """Enhanced health check with CoreAssistant import testing"""
    health_info = {
        "status": "ok",
        "version": "4.1.0",
        "timestamp": datetime.now().isoformat()
    }
    
    # Test CoreAssistant import specifically
    try:
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from core_assistant import CoreAssistant
        health_info["core_assistant"] = "✅ Available"
        health_info["quiz_functionality"] = "✅ Available"
    except ImportError as e:
        health_info["core_assistant"] = f"❌ Import Error: {e}"
        health_info["quiz_functionality"] = "❌ Not Available"
        health_info["environment_debug"] = {
            "cwd": os.getcwd(),
            "script_dir": os.path.dirname(os.path.abspath(__file__)),
            "files_in_dir": [f for f in os.listdir('.') if f.endswith('.py')]
        }
    except Exception as e:
        health_info["core_assistant"] = f"❌ Other Error: {e}"
        health_info["quiz_functionality"] = "❌ Not Available"
    
    return health_info

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
    """Query the educational content with enhanced search and quiz functionality"""
    try:
        # Import the enhanced core assistant with quiz capabilities
        try:
            # Add current directory to path for Railway deployment
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from core_assistant import CoreAssistant
            print("✅ Successfully imported CoreAssistant")
        except ImportError as e:
            print(f"❌ Failed to import CoreAssistant: {e}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
            
            # List files in current directory for debugging
            try:
                files = os.listdir('.')
                print(f"Files in current dir: {[f for f in files if f.endswith('.py')]}")
            except Exception as list_error:
                print(f"Could not list current directory: {list_error}")
                
            # Try to find core_assistant.py specifically
            try:
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                core_assistant_path = os.path.join(current_dir, 'core_assistant.py')
                print(f"Looking for core_assistant.py at: {core_assistant_path}")
                print(f"Exists: {os.path.exists(core_assistant_path)}")
            except Exception as find_error:
                print(f"Error finding core_assistant.py: {find_error}")
                
            print(f"Python path: {sys.path[:3]}")  # Show first 3 paths
            # Fallback to original logic
            return await query_content_fallback(request)
        
        # Initialize the core assistant (this will auto-detect subject and load quiz functionality)
        try:
            print("🔄 Initializing CoreAssistant...")
            assistant = CoreAssistant(collection_name="canvas_content")
            print("✅ Successfully initialized CoreAssistant")
        except Exception as e:
            print(f"❌ Failed to initialize CoreAssistant: {e}")
            print(f"Error type: {type(e).__name__}")
            # More detailed error for ChromaDB issues
            if "chroma" in str(e).lower():
                print("This appears to be a ChromaDB-related error")
            if "openai" in str(e).lower():
                print("This appears to be an OpenAI-related error")
            # Fallback to original logic
            return await query_content_fallback(request)
        
        # Process the query (will automatically detect if it's a quiz request or normal question)
        try:
            print(f"🔄 Processing question: {request.question[:50]}...")
            result = assistant.ask_question(request.question)
            print(f"✅ Successfully processed question: {result.get('type', 'unknown')}")
        except Exception as e:
            print(f"❌ Failed to process question with CoreAssistant: {e}")
            print(f"Error type: {type(e).__name__}")
            # Fallback to original logic
            return await query_content_fallback(request)
        
        # Format response based on type
        if result.get('type') in ['quiz_config', 'quiz_start', 'topic_selection']:
            # Quiz-related response
            return QueryResponse(
                answer=result['answer'],
                sources=result.get('sources', []),
                timestamp=datetime.now().isoformat(),
                sections={
                    "quiz_mode": True,
                    "quiz_type": result.get('type'),
                    "quiz_data": {
                        "session_id": result.get('quiz_session_id'),
                        "current_question": result.get('current_question'),
                        "total_questions": result.get('total_questions'),
                        "available_topics": result.get('available_topics', []),
                        "awaiting_config": result.get('awaiting_config', False)
                    }
                }
            )
        else:
            # Normal Q&A response
            sources_list = []
            if result.get('sources'):
                for source in result['sources']:
                    if isinstance(source, dict):
                        sources_list.append(source.get('source', str(source)))
                    else:
                        sources_list.append(str(source))
            
            return QueryResponse(
                answer=result.get('answer', 'No answer provided'),
                sources=sources_list,
                timestamp=datetime.now().isoformat(),
                sections=parse_educational_response(result.get('answer', ''))
            )
            
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        # Fallback to original logic if core assistant fails
        return await query_content_fallback(request)

async def query_content_fallback(request: QueryRequest):
    """Fallback query processing using original logic"""
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
        
        # Parse response into sections for better display
        parsed_sections = parse_educational_response(answer)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            timestamp=datetime.now().isoformat(),
            sections=parsed_sections
        )
        
    except Exception as e:
        print(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# --- Parsed Query Response (for better frontend display) ---
@app.post("/query-parsed")
async def query_content_parsed(request: QueryRequest):
    """Query and return parsed sections for better display"""
    try:
        # Get the regular response
        regular_response = await query_content(request)
        
        # Return just the parsed sections
        return {
            "title": regular_response.sections.get("title", ""),
            "learning_objective": regular_response.sections.get("learning_objective", ""),
            "quick_summary": regular_response.sections.get("quick_summary", ""),
            "study_info": regular_response.sections.get("study_info", ""),
            "definition_overview": regular_response.sections.get("definition_overview", ""),
            "key_concepts": regular_response.sections.get("key_concepts", []),
            "key_terms": regular_response.sections.get("key_terms", []),
            "think_about": regular_response.sections.get("think_about", []),
            "related_topics": regular_response.sections.get("related_topics", []),
            "sources": regular_response.sources,
            "timestamp": regular_response.timestamp
        }
        
    except Exception as e:
        print(f"Parsed query error: {e}")
        raise HTTPException(status_code=500, detail=f"Parsed query failed: {str(e)}")

# --- Quiz-Specific Endpoints ---
@app.post("/quiz-config")
async def configure_quiz(request: QuizConfigRequest):
    """Configure a quiz based on user preferences"""
    try:
        # Add current directory to path for Railway deployment
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from core_assistant import CoreAssistant
        
        assistant = CoreAssistant(collection_name="canvas_content")
        result = assistant.handle_quiz_configuration(request.config_input, request.available_topics)
        
        return {
            "status": "success",
            "type": result.get('type'),
            "answer": result.get('answer'),
            "quiz_data": {
                "session_id": result.get('quiz_session_id'),
                "current_question": result.get('current_question'),
                "total_questions": result.get('total_questions')
            } if result.get('type') == 'quiz_start' else None,
            "sources": result.get('sources', []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Quiz configuration error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz configuration failed: {str(e)}")

@app.post("/quiz-answer")
async def submit_quiz_answer(request: QuizAnswerRequest):
    """Submit an answer to a quiz question"""
    try:
        # Add current directory to path for Railway deployment
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from core_assistant import CoreAssistant
        
        assistant = CoreAssistant(collection_name="canvas_content")
        result = assistant.continue_quiz(request.answer, request.session_id, request.question_index)
        
        return {
            "status": "success",
            "type": result.get('type'),
            "answer": result.get('answer'),
            "quiz_data": {
                "current_question": result.get('current_question'),
                "score": result.get('score'),
                "final_score": result.get('final_score'),
                "total_questions": result.get('total_questions'),
                "percentage": result.get('percentage')
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Quiz answer processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz answer processing failed: {str(e)}")

@app.get("/quiz-analytics")
async def get_quiz_analytics():
    """Get user's quiz performance analytics"""
    try:
        # Add current directory to path for Railway deployment
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from core_assistant import CoreAssistant
        
        assistant = CoreAssistant(collection_name="canvas_content")
        result = assistant.get_quiz_analytics()
        
        return {
            "status": "success",
            "analytics": result.get('analytics_data', {}),
            "formatted_response": result.get('answer'),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Quiz analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz analytics failed: {str(e)}")

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
            # Clear any environment variables that might interfere
            import sys
            debug_info["python_version"] = sys.version
            debug_info["openai_version"] = openai.__version__
            
            # Try most basic initialization possible
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            debug_info["client_init"] = "successful"
        except Exception as init_error:
            debug_info["client_init_error"] = str(init_error)
            debug_info["init_error_type"] = type(init_error).__name__
            
            # Try alternative initialization
            try:
                import openai
                openai.api_key = api_key
                debug_info["legacy_init"] = "attempted openai.api_key method"
            except Exception as legacy_error:
                debug_info["legacy_error"] = str(legacy_error)
            
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

@app.post("/api/ingest-content")  
async def api_ingest_content(request: ContentUploadRequest):
    """API endpoint for web app content upload (same as upload-content but with /api prefix)"""
    return await upload_content(request)

# --- Additional API Endpoints for Web App ---

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics for the web app"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        client = chromadb.PersistentClient(path=chroma_path)
        
        # Get collection stats
        try:
            collection = client.get_collection(name="educational_content")
            total_content = collection.count()
        except:
            total_content = 0
        
        # Mock stats for now - you can enhance these later
        stats = {
            "total_content": total_content,
            "questions_asked": 42,  # You can track this in a database later
            "study_streak": 5,
            "last_active": "2 hours ago"
        }
        
        return stats
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return {"total_content": 0, "questions_asked": 0, "study_streak": 0, "last_active": "Unknown"}

@app.post("/api/content/search")
async def search_content(request: dict):
    """Advanced search with filters for the web app"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        client = chromadb.PersistentClient(path=chroma_path)
        
        query = request.get("query", "")
        filters = request.get("filters", {})
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        try:
            collection = client.get_collection(name="educational_content")
        except:
            return {
                "results": [],
                "total": 0,
                "query": query,
                "filters": filters,
                "message": "No content collection found"
            }
        
        # Build ChromaDB query with filters
        where_filter = {}
        if filters.get("content_type") and filters["content_type"] != "all":
            where_filter["content_type"] = filters["content_type"]
        
        # Perform search
        results = collection.query(
            query_texts=[query],
            n_results=min(20, request.get("limit", 10)),
            where=where_filter if where_filter else None
        )
        
        # Format results for web app
        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                
                # Calculate relevance percentage
                relevance = max(0, min(100, int((1 - distance) * 100)))
                
                search_results.append({
                    "id": i + 1,
                    "title": metadata.get("title", "Untitled Content"),
                    "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                    "type": metadata.get("content_type", "unknown"),
                    "date": metadata.get("timestamp", datetime.now().isoformat()),
                    "relevance": relevance
                })
        
        return {
            "results": search_results,
            "total": len(search_results),
            "query": query,
            "filters": filters
        }
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/content/list")
async def get_content_list():
    """Get list of all content for content manager"""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_DB_PATH", "/tmp/chroma_db_railway")
        client = chromadb.PersistentClient(path=chroma_path)
        
        try:
            collection = client.get_collection(name="educational_content")
        except:
            return {"content": [], "total": 0, "message": "No content collection found"}
        
        # Get all content (you might want to paginate this later)
        results = collection.get()
        
        content_list = []
        if results['documents']:
            for i, doc in enumerate(results['documents']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                
                content_list.append({
                    "id": results['ids'][i] if results['ids'] else str(i),
                    "title": metadata.get("title", "Untitled Content"),
                    "type": metadata.get("content_type", "unknown"),
                    "date": metadata.get("timestamp", datetime.now().isoformat()),
                    "size": len(doc),
                    "excerpt": doc[:100] + "..." if len(doc) > 100 else doc
                })
        
        return {
            "content": content_list,
            "total": len(content_list)
        }
        
    except Exception as e:
        print(f"❌ Error getting content list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get content list: {str(e)}")

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data for the web app"""
    try:
        # Mock analytics data for now - you can enhance this later
        analytics = {
            "study_sessions": [
                {"date": "2024-08-01", "questions": 5, "time_spent": 30},
                {"date": "2024-08-02", "questions": 8, "time_spent": 45},
                {"date": "2024-08-03", "questions": 12, "time_spent": 60},
                {"date": "2024-08-04", "questions": 6, "time_spent": 35},
                {"date": "2024-08-05", "questions": 10, "time_spent": 50},
                {"date": "2024-08-06", "questions": 15, "time_spent": 75},
                {"date": "2024-08-07", "questions": 9, "time_spent": 40},
            ],
            "top_topics": [
                {"name": "Protein Structure", "questions": 25},
                {"name": "DNA Replication", "questions": 18},
                {"name": "Cell Biology", "questions": 15},
                {"name": "Photosynthesis", "questions": 12},
            ],
            "difficulty_distribution": {
                "beginner": 40,
                "intermediate": 35,
                "advanced": 25
            }
        }
        
        return analytics
        
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
        return {"error": str(e)}

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
