"""
Ultra-Simple Canvas AI Assistant API
Minimal deployment version that will definitely work
"""
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Canvas AI Assistant API",
    description="Educational content analysis and question-answering for Canvas LMS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models (compatible with pydantic v1)
class ContentRequest(BaseModel):
    content: str
    content_type: str = "canvas_content" 
    title: str = "Canvas Content"

class QuestionRequest(BaseModel):
    question: str
    context_limit: int = 5

# Simple AI functionality without dependencies
def simple_content_analysis(content: str) -> Dict[str, Any]:
    """Basic content analysis without external dependencies"""
    word_count = len(content.split())
    char_count = len(content)
    
    # Simple keyword detection
    educational_keywords = ["chapter", "lesson", "quiz", "assignment", "study", "learn", "concept", "theory"]
    found_keywords = [kw for kw in educational_keywords if kw.lower() in content.lower()]
    
    return {
        "status": "success",
        "analysis": {
            "word_count": word_count,
            "character_count": char_count,
            "educational_keywords_found": found_keywords,
            "content_type": "educational_material",
            "estimated_reading_time": max(1, word_count // 200)  # ~200 words per minute
        },
        "suggestions": [
            "Content has been analyzed for educational structure",
            f"Found {len(found_keywords)} educational indicators",
            f"Estimated reading time: {max(1, word_count // 200)} minutes"
        ]
    }

def simple_question_answer(question: str) -> Dict[str, Any]:
    """Basic question response without AI dependencies"""
    return {
        "answer": f"I've received your question: '{question}'. This is a basic response since full AI functionality requires additional setup. The content analysis system is working and ready for educational content processing.",
        "confidence": "medium",
        "method": "basic_response",
        "suggestions": [
            "Try analyzing content first to build the knowledge base",
            "Check the /docs endpoint for full API documentation",
            "Ensure OpenAI API key is configured for enhanced responses"
        ]
    }

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API status"""
    return {
        "message": "Canvas AI Assistant API is running!",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze_content": "/analyze-content",
            "ask_question": "/ask-question",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-07-30",
        "api_version": "1.0.0",
        "features": {
            "content_analysis": True,
            "basic_qa": True,
            "cors_enabled": True
        }
    }

@app.post("/analyze-content")
async def analyze_content(request: ContentRequest):
    """Analyze educational content"""
    try:
        logger.info(f"Analyzing content: {request.title}")
        
        if not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        # Perform basic analysis
        analysis_result = simple_content_analysis(request.content)
        
        return {
            "success": True,
            "data": analysis_result,
            "content_info": {
                "title": request.title,
                "type": request.content_type,
                "processed_at": "2025-07-30"
            }
        }
        
    except Exception as e:
        logger.error(f"Content analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/ask-question")
async def ask_question(request: QuestionRequest):
    """Answer questions about content"""
    try:
        logger.info(f"Processing question: {request.question}")
        
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Generate basic response
        response = simple_question_answer(request.question)
        
        return {
            "success": True,
            "data": response,
            "query_info": {
                "question": request.question,
                "context_limit": request.context_limit,
                "processed_at": "2025-07-30"
            }
        }
        
    except Exception as e:
        logger.error(f"Question processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

@app.get("/status")
async def get_status():
    """Get detailed API status"""
    return {
        "api_status": "operational",
        "features": {
            "content_analysis": "basic",
            "question_answering": "basic", 
            "cors": "enabled",
            "health_checks": "active"
        },
        "deployment": {
            "platform": "render",
            "python_version": "auto-detected",
            "dependencies": "minimal"
        },
        "next_steps": [
            "Content analysis is working",
            "Basic Q&A functionality is available",
            "Ready for Canvas browser extension integration"
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/analyze-content", "/ask-question", "/docs"],
        "tip": "Check /docs for API documentation"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "message": "The API encountered an unexpected error",
        "tip": "Check /health endpoint to verify API status"
    }

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
