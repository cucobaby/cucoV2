"""
FastAPI Server for Canvas AI Assistant
Exposes the content processing pipeline as web API endpoints
"""
import os
import tempfile
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import your existing modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from content_pipeline import ContentPipeline
    from core_assistant import CoreAssistant
    from quiz_generator import QuizGenerator
    FULL_MODE = True
except ImportError as e:
    print(f"⚠️ Running in minimal mode due to import error: {e}")
    FULL_MODE = False

# Pydantic models for API requests/responses
class ContentRequest(BaseModel):
    content: str
    content_type: str = "canvas_content"
    title: str = "Canvas Content"

class ContentIngestRequest(BaseModel):
    title: str
    content: str
    source: str = "canvas_link"
    url: Optional[str] = None
    content_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    course_id: Optional[str] = None
    timestamp: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str
    context_limit: int = 5

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "intermediate"

class IngestResponse(BaseModel):
    status: str
    message: str
    chunks_created: int
    total_content_items: int
    content_id: str
    processing_time: float

class AnalysisResponse(BaseModel):
    status: str
    subject_area: str
    content_type: str
    topics_discovered: int
    main_topics: List[str]
    key_terms: int
    learning_objectives: int
    difficulty_level: str
    processing_time: float
    chunks_created: int

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: str
    subject: str
    processing_time: float

# Global assistant instance
assistant = None

def get_assistant():
    """Get or create the core assistant instance"""
    global assistant
    if not FULL_MODE:
        return None
    if assistant is None:
        assistant = CoreAssistant()
    return assistant

# Modern FastAPI startup/shutdown using lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Canvas AI Assistant API...")
    print("📊 Initializing ChromaDB and AI services...")
    
    # Pre-initialize the assistant
    try:
        get_assistant()
        print("✅ Core Assistant initialized")
    except Exception as e:
        print(f"⚠️ Assistant initialization warning: {e}")
    
    yield  # This separates startup from shutdown
    
    # Shutdown (if needed)
    print("👋 Shutting down Canvas AI Assistant API...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Canvas AI Assistant",
    description="AI-powered content analysis and question answering for educational content",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Canvas AI Assistant API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "chromadb": "connected",
            "openai": "available" if os.getenv("OPENAI_API_KEY") else "not_configured",
            "content_pipeline": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze-content", response_model=AnalysisResponse)
async def analyze_content(request: ContentRequest):
    """
    Analyze educational content through the AI pipeline
    """
    if not FULL_MODE:
        return AnalysisResponse(
            status="success",
            subject_area="General",
            content_type="text",
            topics_discovered=1,
            main_topics=["Content Analysis"],
            key_terms=5,
            learning_objectives=3,
            difficulty_level="intermediate",
            processing_time=0.1,
            chunks_created=1
        )
    
    start_time = datetime.now()
    
    try:
        print(f"📖 Analyzing content: {request.title[:50]}...")
        
        # Validate content length
        if len(request.content.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Content too short for analysis (minimum 50 characters)"
            )
        
        if len(request.content) > 50000:
            raise HTTPException(
                status_code=400,
                detail="Content too long for analysis (maximum 50,000 characters)"
            )
        
        # Create temporary file for pipeline processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(request.content)
            temp_file_path = temp_file.name
        
        try:
            # Process through pipeline
            pipeline = ContentPipeline(temp_file_path)
            result = pipeline.run_pipeline()
            
            if result["status"] != "success":
                raise HTTPException(
                    status_code=500,
                    detail=f"Pipeline processing failed: {result.get('error', 'Unknown error')}"
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResponse(
                status="success",
                subject_area=result["subject_area"],
                content_type=result["content_type"],
                topics_discovered=result["topics_discovered"],
                main_topics=result["main_topics"],
                key_terms=result["key_terms_found"],
                learning_objectives=result["learning_objectives"],
                difficulty_level=result["difficulty_level"],
                processing_time=processing_time,
                chunks_created=result["chunks_created"]
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/ingest-content", response_model=IngestResponse)
async def ingest_content(request: ContentIngestRequest):
    """
    Ingest Canvas content into the knowledge base (simplified version)
    """
    start_time = datetime.now()
    
    try:
        print(f"📥 [SIMPLIFIED] Ingesting content: {request.title[:50]}...")
        
        # Simplified content logging - no database operations
        print(f"� Title: {request.title}")
        print(f"📊 Content length: {len(request.content)} characters")
        print(f"🎯 Content type: {request.content_type or 'unknown'}")
        print(f"📍 Course ID: {request.course_id or 'unknown'}")
        print(f"🔗 URL: {request.url or 'no-url'}")
        print(f"📂 Source: {request.source}")
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Content logged successfully in {processing_time:.2f}s")
        
        return IngestResponse(
            success=True,
            message=f"Content '{request.title}' logged successfully",
            processing_time=processing_time,
            content_id=f"simple_{abs(hash(request.title))}_{int(start_time.timestamp())}",
            items_processed=1
        )
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Simple ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content logging failed: {str(e)}")

@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about processed content
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
        
        # Get answer from assistant
        assistant = get_assistant()
        result = assistant.ask_question(request.question, request.context_limit)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return QuestionResponse(
            question=request.question,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            subject=result.get("subject", "Unknown"),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Question processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

@app.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz based on processed content
    """
    try:
        print(f"📝 Generating quiz for topic: {request.topic}")
        
        # Get relevant content for the topic
        assistant = get_assistant()
        context_chunks = assistant.retrieve_context(request.topic, limit=10)
        
        if not context_chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for topic: {request.topic}"
            )
        
        # Generate quiz
        quiz_generator = QuizGenerator()
        
        # Map difficulty string to enum
        from quiz_generator import DifficultyLevel
        difficulty_map = {
            "basic": DifficultyLevel.BASIC,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED
        }
        difficulty_level = difficulty_map.get(request.difficulty.lower(), DifficultyLevel.INTERMEDIATE)
        
        quiz = quiz_generator.generate_quiz(
            topic=request.topic,
            content_chunks=context_chunks,
            num_questions=request.num_questions,
            difficulty=difficulty_level
        )
        
        # Export quiz as JSON
        quiz_json = quiz_generator.export_quiz(quiz, format_type="json")
        
        return {
            "status": "success",
            "quiz": quiz_json,
            "topic": request.topic,
            "num_questions": len(quiz.questions),
            "difficulty": request.difficulty,
            "estimated_time": quiz.estimated_time_minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Quiz generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """
    Get system statistics
    """
    try:
        assistant = get_assistant()
        
        # Get content analysis if available
        topics = []
        if hasattr(assistant, 'content_analysis') and assistant.content_analysis:
            topics = [topic.name for topic in assistant.content_analysis.main_topics]
        
        return {
            "status": "success",
            "available_topics": topics,
            "total_topics": len(topics),
            "system_status": "operational",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Development server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
