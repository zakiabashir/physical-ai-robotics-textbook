"""
Chat models for the Physical AI Textbook API
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Text, Integer, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base


class ChatSession(Base):
    """Chat session model for tracking conversations"""

    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True)  # UUID v4
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    lesson_context = Column(String, nullable=True)  # Lesson ID when chat was started
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationship to user
    user = relationship("User", back_populates="chat_sessions")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """Individual chat messages within a session"""

    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)  # UUID v4
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sources = Column(JSON, default=[])  # Source documents referenced
    related_lessons = Column(JSON, default=[])  # Related lesson IDs

    # Feedback from user on assistant responses
    feedback = Column(JSON, default={})
    feedback_rating = Column(Integer, nullable=True)  # 1-5 stars

    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, session_id={self.session_id})>"