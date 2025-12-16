"""
Physical AI & Humanoid Robotics Textbook - Standalone Authentication Server
No external dependencies, completely isolated from other routers
"""

from fastapi import FastAPI, HTTPException, status, Depends, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import os
import logging
import json
from datetime import datetime, timedelta
from jose import jwt
import bcrypt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple configuration
SECRET_KEY = os.getenv("SECRET_KEY", "test_secret_key_123")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user store for demo (replace with database in production)
users = {}
user_sessions = {}

# Security
security = HTTPBearer()

# Request models
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Physical AI Textbook Standalone Auth Server...")
    yield
    # Shutdown
    logger.info("Shutting down Physical AI Textbook Standalone Auth Server...")


# Create FastAPI application
app = FastAPI(
    title="Physical AI Textbook API - Standalone Auth",
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


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return username
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user"""
    # Check if user already exists
    if request.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash password using bcrypt directly (truncate to 72 bytes max for bcrypt)
    password_bytes = request.password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Store user
    users[request.username] = {
        "username": request.username,
        "email": request.email,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }

    logger.info(f"User {request.username} registered successfully")
    return {"message": "User created successfully"}


@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """Login user and return access token"""
    # Verify user exists
    if request.username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    stored_password = users[request.username]["password"]
    password_bytes = request.password.encode('utf-8')[:72]

    if not bcrypt.checkpw(password_bytes, stored_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username}, expires_delta=access_token_expires
    )

    # Store session
    user_sessions[request.username] = {
        "token": access_token,
        "expires_at": (datetime.utcnow() + access_token_expires).isoformat()
    }

    logger.info(f"User {request.username} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.get("/api/v1/auth/me")
async def get_current_user(current_user: str = Depends(verify_token)):
    """Get current user information"""
    user = users.get(current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "username": user["username"],
        "email": user.get("email"),
        "created_at": user["created_at"]
    }


@app.post("/api/v1/auth/debug-register")
async def debug_register(request: Request):
    """Debug endpoint to see what frontend is sending"""
    body = await request.body()
    logger.info(f"Received body: {body}")
    logger.info(f"Content-Type: {request.headers.get('content-type')}")

    try:
        body_str = body.decode('utf-8')
        logger.info(f"Body as string: {body_str}")

        # Try to parse as JSON
        if request.headers.get('content-type') == 'application/json':
            json_data = json.loads(body_str)
            logger.info(f"Parsed JSON: {json_data}")
            return {"received": json_data, "content_type": request.headers.get('content-type')}
        else:
            return {"received": body_str, "content_type": request.headers.get('content-type')}
    except Exception as e:
        logger.error(f"Error parsing body: {e}")
        return {"error": str(e), "raw_body": body.decode('utf-8') if body else "empty"}


@app.post("/api/v1/auth/logout")
async def logout(current_user: str = Depends(verify_token)):
    """Logout user"""
    if current_user in user_sessions:
        del user_sessions[current_user]

    logger.info(f"User {current_user} logged out successfully")
    return {"message": "Successfully logged out"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API - Standalone Auth",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - optimized for speed"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Physical AI Textbook API - Standalone Auth",
        "version": "0.1.0",
        "description": "Backend API for interactive Physical AI textbook",
        "features": [
            "User authentication",
        ]
    }


@app.post("/api/v1/auth/test")
async def test_auth():
    """Test endpoint to verify auth is working"""
    return {"message": "Auth endpoints are working!"}


if __name__ == "__main__":
    uvicorn.run(
        "app.standalone_auth_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,
    )