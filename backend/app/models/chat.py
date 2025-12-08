"""Pydantic models for chat functionality"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ChatMessage(BaseModel):
    """Model for a chat message"""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[Dict[str, Any]]] = Field(default=None)
    code_examples: Optional[List[Dict[str, Any]]] = Field(default=None)


class ChatRequest(BaseModel):
    """Model for chat request"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Context about current page/selection")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for session tracking")
    lesson_id: Optional[str] = Field(None, description="Current lesson ID")


class ChatResponse(BaseModel):
    """Model for chat response"""
    message: str = Field(..., description="Assistant's response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source references")
    related_concepts: List[str] = Field(default_factory=list, description="Related concepts to explore")
    code_examples: List[Dict[str, Any]] = Field(default_factory=list, description="Code examples for the response")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for further learning")
    can_explain_code: bool = Field(default=False, description="Whether code can be explained further")
    related_content: List[Dict[str, Any]] = Field(default_factory=list, description="Related content suggestions")


class Conversation(BaseModel):
    """Model for a conversation"""
    id: str = Field(default_factory=lambda: str(UUID.uuid4()), description="Conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0, description="Number of messages in conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Feedback(BaseModel):
    """Model for user feedback"""
    conversation_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=500)
    category: str = Field(default="general", description="Feedback category")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CodeExplanation(BaseModel):
    """Model for code explanation"""
    code: str = Field(..., description="Code to explain")
    language: str = Field(..., description="Programming language")
    explanation: str = Field(..., description="Explanation of the code")
    line_numbers: Optional[List[int]] = Field(None, description="Line numbers referenced")
    context: Optional[str] = Field(None, description="Additional context")


class HighlightQuestion(BaseModel):
    """Model for question about highlighted text"""
    text: str = Field(..., description="Highlighted text")
    lesson_id: str = Field(..., description="Current lesson ID")
    section: Optional[str] = Field(None, description="Section within lesson")
    question: Optional[str] = Field(None, description="Implicit question about the text")
    response: str = Field(..., description="AI response about the text")
    related_content: List[Dict[str, Any]] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Model for search result"""
    lesson_id: str
    chapter_id: str
    title: str
    content_snippet: str
    relevance_score: float
    url: str


class LessonSuggestion(BaseModel):
    """Model for lesson suggestions"""
    suggestion: str
    type: str  # practice, theory, reference
    priority: int  # 1-5
    related_lessons: List[str]