"""Authentication router for user management"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from ..models.chat import Conversation
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store for demo (replace with database in production)
users = {}
user_sessions = {}


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
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

    # Hash password
    hashed_password = pwd_context.hash(password)

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
    if not pwd_context.verify(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access"
        },
        settings.SECRET_KEY,
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
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
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


@router.put("/me")
async def update_current_user(
    email: Optional[str] = None,
    username: str = Depends(verify_token)
):
    """Update current user info"""
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if email:
        users[username]["email"] = email

    logger.info(f"User {username} updated profile")
    return {"message": "Profile updated successfully"}


@router.get("/conversations")
async def get_user_conversations(
    limit: int = 10,
    offset: int = 0,
    username: str = Depends(verify_token)
):
    """Get user's conversation history"""
    # This would typically query a database
    # For demo, return empty list
    return {
        "conversations": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.delete("/account")
async def delete_account(username: str = Depends(verify_token)):
    """Delete user account"""
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Delete user and sessions
    del users[username]
    if username in user_sessions:
        del user_sessions[username]

    logger.info(f"User {username} deleted account")
    return {"message": "Account deleted successfully"}