"""
Simple FastAPI app for basic deployment testing with chat functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from typing import Dict, Any

app = FastAPI(title="Physical AI Textbook API - Simple", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/api/v1/info")
async def info():
    return {
        "name": "Physical AI Textbook API",
        "version": "0.1.0",
        "status": "simple_mode"
    }


@app.get("/api/v1/test")
async def test():
    """Test endpoint to verify API is working"""
    return {
        "status": "ok",
        "message": "API is working correctly",
        "timestamp": time.time()
    }


@app.post("/api/v1/chat/")
async def chat_endpoint(request: Dict[str, Any]):
    """Simple chat endpoint with mock response"""
    try:
        message = request.get("message", "")

        # Simple mock response
        response_text = f"I received your message: '{message}'. This is a simplified response from the minimal app. The AI assistant functionality will be enhanced once the full backend is deployed."

        return {
            "response": response_text,
            "sources": [],
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "response": "Sorry, I encountered an error. Please try again.",
            "sources": [],
            "timestamp": time.time(),
            "error": str(e)
        }


@app.post("/api/v1/chat/feedback")
async def feedback_endpoint(request: Dict[str, Any]):
    """Simple feedback endpoint"""
    return {
        "status": "success",
        "message": "Feedback received"
    }


@app.get("/api/v1/content/chapters")
async def get_chapters():
    """Get available chapters"""
    return {
        "chapters": [
            {"id": 1, "title": "Introduction to Physical AI", "lessons": 5},
            {"id": 2, "title": "Robotics Fundamentals", "lessons": 8}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))