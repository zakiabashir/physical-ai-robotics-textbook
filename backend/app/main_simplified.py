"""
Simplified Physical AI & Humanoid Robotics Textbook - FastAPI Backend
Main application entry point with essential endpoints only
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any
import time

# Setup logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Physical AI Textbook API...")
    yield
    # Shutdown
    logger.info("Shutting down Physical AI Textbook API...")


# Create FastAPI application
app = FastAPI(
    title="Physical AI Textbook API",
    description="Backend API for the Physical AI & Humanoid Robotics interactive textbook",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": "production"
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Physical AI Textbook API",
        "version": "0.1.0",
        "description": "Backend API for interactive Physical AI textbook",
        "features": [
            "User authentication",
            "AI-powered chat assistant",
            "Progress tracking",
            "Personalized learning"
        ]
    }


@app.post("/api/v1/chat/")
async def chat_endpoint(request: Dict[str, Any]):
    """Simple chat endpoint with mock response"""
    try:
        message = request.get("message", "")
        context = request.get("context")

        # Debug logging
        logger.info(f"Received chat request: message='{message[:50]}...'")

        # Simple mock response for now
        response_text = f"I received your message: '{message}'. This is a simplified response. The full RAG functionality will be available once all dependencies are properly configured."

        return {
            "response": response_text,
            "sources": [],
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return {
            "response": "Sorry, I encountered an error processing your request.",
            "sources": [],
            "timestamp": time.time(),
            "error": str(e)
        }


@app.post("/api/v1/chat/feedback")
async def feedback_endpoint(request: Dict[str, Any]):
    """Simple feedback endpoint"""
    return {
        "status": "success",
        "message": "Feedback received (simplified mode)"
    }


@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "ok",
        "message": "API is working correctly",
        "timestamp": time.time()
    }


@app.get("/api/v1/content/chapters")
async def get_chapters():
    """Get available chapters"""
    return {
        "chapters": [
            {"id": 1, "title": "Introduction to Physical AI", "lessons": 5},
            {"id": 2, "title": "Robotics Fundamentals", "lessons": 8},
            {"id": 3, "title": "Humanoid Robots", "lessons": 6}
        ]
    }


@app.get("/api/v1/content/navigation")
async def get_navigation():
    """Get navigation structure"""
    return {
        "structure": {
            "chapters": [
                {
                    "id": "ch1",
                    "title": "Introduction to Physical AI",
                    "lessons": [
                        {"id": "ch1-l1", "title": "What is Physical AI?"},
                        {"id": "ch1-l2", "title": "Applications of Physical AI"}
                    ]
                }
            ]
        }
    }


# Include health router if available
try:
    from app.routers.health import router as health_router
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
except ImportError:
    logger.warning("Health router not available")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)