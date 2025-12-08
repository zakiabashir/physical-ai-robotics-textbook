"""
API routers for the Physical AI Textbook backend
"""

from . import auth, chat, embeddings, content, ingestion, health, analytics, code

__all__ = ["auth", "chat", "embeddings", "content", "ingestion", "health", "analytics", "code"]