"""
Physical AI & Humanoid Robotics Textbook - Standalone Authentication Server
No external dependencies, completely isolated from other routers
"""

from fastapi import FastAPI, HTTPException, status, Depends, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, Union
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

# Flexible models that can handle dict input
def get_register_data(data: Union[RegisterRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """Extract register data from either Pydantic model or dict"""
    if isinstance(data, dict):
        return {
            "username": data.get("username"),
            "password": data.get("password"),
            "email": data.get("email")
        }
    else:
        return {
            "username": data.username,
            "password": data.password,
            "email": data.email
        }

def get_login_data(data: Union[LoginRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """Extract login data from either Pydantic model or dict"""
    if isinstance(data, dict):
        return {
            "username": data.get("username"),
            "password": data.get("password")
        }
    else:
        return {
            "username": data.username,
            "password": data.password
        }


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
async def register(request: Request):
    """Register a new user"""
    # Get the raw body
    body = await request.body()

    # Log what we received
    logger.info(f"Register endpoint - Content-Type: {request.headers.get('content-type')}")
    logger.info(f"Register endpoint - Raw body: {body}")
    logger.info(f"Register endpoint - Body as string: {body.decode('utf-8')}")

    # Parse the data based on content type
    content_type = request.headers.get('content-type', '')

    try:
        if 'application/json' in content_type:
            data = json.loads(body.decode('utf-8'))
        else:
            # Try to parse as JSON even if content-type is not set
            data = json.loads(body.decode('utf-8'))
        logger.info(f"Register endpoint - Parsed data: {data}")
    except Exception as e:
        # If JSON parsing fails, assume it's malformed
        logger.error(f"Register endpoint - JSON parse error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request format. Expected JSON. Error: {str(e)}"
        )

    # Extract data
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid request format. Expected JSON object."
        )

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Validate required fields
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    # Check if user already exists
    if username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash password using bcrypt directly (truncate to 72 bytes max for bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Store user
    users[username] = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }

    logger.info(f"User {username} registered successfully")
    return {"message": "User created successfully"}


@app.post("/api/v1/auth/login")
async def login(request: Request):
    """Login user and return access token"""
    # Get the raw body
    body = await request.body()

    # Log what we received
    logger.info(f"Login endpoint - Content-Type: {request.headers.get('content-type')}")
    logger.info(f"Login endpoint - Raw body: {body}")
    logger.info(f"Login endpoint - Body as string: {body.decode('utf-8')}")

    # Parse the data
    try:
        data = json.loads(body.decode('utf-8'))
        logger.info(f"Login endpoint - Parsed data: {data}")
    except Exception as e:
        logger.error(f"Login endpoint - JSON parse error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request format. Expected JSON. Error: {str(e)}"
        )

    # Extract data
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid request format. Expected JSON object."
        )

    username = data.get('username')
    password = data.get('password')

    # Validate required fields
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    # Verify user exists
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    stored_password = users[username]["password"]
    password_bytes = password.encode('utf-8')[:72]

    if not bcrypt.checkpw(password_bytes, stored_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    # Store session
    user_sessions[username] = {
        "token": access_token,
        "expires_at": (datetime.utcnow() + access_token_expires).isoformat()
    }

    logger.info(f"User {username} logged in successfully")
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