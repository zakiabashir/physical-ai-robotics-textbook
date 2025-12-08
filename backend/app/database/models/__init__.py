"""
Database models for the Physical AI Textbook API
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models
from .user import User
from .chat import ChatSession, ChatMessage

# Update User model to include relationships
User.chat_sessions = relationship("ChatSession", back_populates="user")
ChatSession.messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")