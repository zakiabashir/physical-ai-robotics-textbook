"""
Simple FastAPI app for basic deployment testing
"""

from fastapi import FastAPI
import os
import time

app = FastAPI(title="Physical AI Textbook API - Simple", version="0.1.0")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))