"""
Physical AI & Humanoid Robotics Textbook - FastAPI Backend
Main application entry point - Authentication Focus
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import logging

# Import routers
from app.routers import auth, chat

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Physical AI Textbook API with auth...")
    yield
    # Shutdown
    logger.info("Shutting down Physical AI Textbook API...")


# Create FastAPI application
app = FastAPI(
    title="Physical AI Textbook API - Auth",
    description="Backend API for the Physical AI & Humanoid Robotics interactive textbook",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API - Auth",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Physical AI Textbook API - Auth",
        "version": "0.1.0",
        "description": "Backend API for interactive Physical AI textbook",
        "features": [
            "User authentication",
            "AI-powered chat assistant",
        ]
    }


@app.post("/api/v1/auth/test")
async def test_auth():
    """Test endpoint to verify auth is working"""
    return {"message": "Auth endpoints are working!"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main_auth:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,
    )