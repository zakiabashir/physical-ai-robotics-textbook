"""
Minimal FastAPI server for Railway deployment
This is the simplest possible server to debug Railway issues
"""

from fastapi import FastAPI
import os
import sys

# Create the simplest possible FastAPI app
app = FastAPI(title="Minimal Test API")

@app.get("/")
async def root():
    return {
        "message": "Minimal API is running",
        "python_version": sys.version,
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok"}

# Add auth test endpoint (minimal)
@app.get("/api/v1/auth/test")
async def auth_test():
    """Test auth endpoint"""
    return {"message": "Auth test endpoint works"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)