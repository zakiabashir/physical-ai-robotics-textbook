"""Standalone Authentication router for user management - No external dependencies"""

from fastapi import APIRouter, Depends, HTTPException, status, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import jwt
import bcrypt
import os

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Simple configuration
SECRET_KEY = os.getenv("SECRET_KEY", "test_secret_key_123")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory user store for demo (replace with database in production)
users = {}
user_sessions = {}


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
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(username: str, password: str, email: Optional[str] = None):
    """Register a new user"""
    if username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Hash password using bcrypt directly (truncate to 72 bytes max for bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Store user
    users[username] = {
        "username": username,
        "password": hashed_password,
        "email": email,
        "created_at": datetime.utcnow(),
        "is_active": True
    }

    logger.info(f"User {username} registered successfully")
    return {"message": "User created successfully"}


@router.post("/login")
async def login(username: str, password: str) -> Dict[str, Any]:
    """Authenticate user and return token"""
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    user = users[username]
    # Verify password using bcrypt directly
    password_bytes = password.encode('utf-8')[:72]
    stored_hash = user["password"].encode('utf-8')
    if not bcrypt.checkpw(password_bytes, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    # Store session
    user_sessions[username] = {
        "token": access_token,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }

    logger.info(f"User {username} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(username: str = Depends(verify_token)):
    """Logout user"""
    if username in user_sessions:
        del user_sessions[username]

    logger.info(f"User {username} logged out")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(username: str = Depends(verify_token)):
    """Get current user info"""
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = users[username].copy()
    user.pop("password", None)  # Remove password from response

    return user


@router.get("/test")
async def test_auth():
    """Test endpoint to verify auth is working"""
    return {"message": "Auth endpoints are working!", "status": "healthy"}