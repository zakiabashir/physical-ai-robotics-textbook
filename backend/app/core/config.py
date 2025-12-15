"""
Configuration settings for the Physical AI Textbook API
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Physical AI Textbook"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30

    # Gemini API (optional)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "models/gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_MAX_TOKENS: int = 4000
    GEMINI_TEMPERATURE: float = 0.7

    # Cohere API (for embeddings)
    COHERE_API_KEY: Optional[str] = None

    # RAG Configuration
    EMBED_MODEL: str = "embed-english-v3.0"
    COLLECTION_NAME: str = "humanoid_ai_book"
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 100
    SITEMAP_URL: str = "https://physical-ai-book-hacka-mges.vercel.app/sitemap.xml"

    # Qdrant
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "textbook_content"
    QDRANT_VECTOR_SIZE: int = 1024  # Updated for Cohere's embed-english-v3.0
    VECTOR_DISTANCE: str = "Cosine"

    # Authentication
    SECRET_KEY: str
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str = "http://localhost:3000"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "https://physical-ai-robotics.panaversity.org",
        "https://physical-ai-robotics-textbook-8tzi59hee-zakiabashirs-projects.vercel.app"
    ]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    CHAT_RATE_LIMIT_PER_MINUTE: int = 30

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Google Translate
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    GOOGLE_TRANSLATE_PROJECT_ID: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ANALYTICS_ID: Optional[str] = None

    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()