"""
Minimal API server for Railway deployment testing
Strips out potential problematic imports to isolate deployment issues
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Simple health check without complex dependencies
app = FastAPI(title="Canvas AI Assistant API - Minimal", version="2.0")

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

class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None
    course_id: Optional[str] = None

# --- Health Check (Minimal) ---
@app.get("/health")
async def health_check():
    """Minimal health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0-minimal",
            "message": "Minimal API for deployment testing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# --- Test Endpoints ---
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify deployment"""
    return {
        "message": "API deployment successful!",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ingest-content")
async def minimal_ingest(request: ContentIngestRequest):
    """Minimal content ingestion for testing"""
    return {
        "status": "received",
        "message": f"Content '{request.title}' received successfully",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ask-question") 
async def minimal_question(request: QuestionRequest):
    """Minimal question handling for testing"""
    return {
        "answer": f"Minimal API received your question: '{request.question}'",
        "confidence": 0.0,
        "sources": [],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
