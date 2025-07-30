from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class StudyGuideMetadata(BaseModel):
    """Metadata extracted from YAML front matter"""
    title: str
    type: str
    course: str
    chapter: str
    lectures: List[str]
    date: str
    study_context: str
    learning_focus: str
    note: Optional[str] = None

class ContentChunk(BaseModel):
    """A chunk of content with metadata"""
    id: str
    content: str
    metadata: StudyGuideMetadata
    section_title: str
    section_type: str  # learning_objectives, vocabulary, mechanisms, etc.
    chunk_index: int
    source_file: str

class SearchQuery(BaseModel):
    """Search query with optional filters"""
    query: str
    course_filter: Optional[str] = None
    chapter_filter: Optional[str] = None
    lecture_filter: Optional[str] = None
    section_type_filter: Optional[str] = None
    limit: int = 5

class SearchResult(BaseModel):
    """Search result with relevance score"""
    chunk: ContentChunk
    relevance_score: float
    distance: float

class QuestionResponse(BaseModel):
    """Response to a user question"""
    answer: str
    sources: List[SearchResult]
    confidence: float
    related_topics: List[str]
