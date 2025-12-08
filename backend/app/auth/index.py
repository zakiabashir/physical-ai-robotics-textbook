"""
Better-Auth authentication configuration
"""

from better_auth import BetterAuth
from better_auth.adapters.mongodb import MongoDBAdapter
from better_auth.plugins import AdminPlugin, OpenAPIPlugin
import os
from ..core.config import settings

# Initialize Better-Auth
auth = BetterAuth(
    database=MongoDBAdapter(
        connection_string=settings.DATABASE_URL.replace("sqlite+aiosqlite://", "mongodb://"),
        database="physical_ai_textbook"
    ),
    emailAndPassword={
        "enabled": True,
        "requireEmailVerification": False,  # Set to True in production
    },
    socialProviders={
        "google": {
            "clientId": os.getenv("GOOGLE_CLIENT_ID", ""),
            "clientSecret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        },
    },
    session={
        "expiresIn": 60 * 60 * 24 * 7,  # 7 days
        "updateAge": 60 * 60 * 24,  # 1 day
        "cookieCache": {
            "enabled": True,
            "maxAge": 5 * 60,  # 5 minutes
        },
    },
    account={
        "accountLinking": {
            "enabled": True,
        },
    },
    plugins=[
        AdminPlugin(),
        OpenAPIPlugin(),
    ],
)

# Export auth handler for FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_auth(app: FastAPI):
    """Setup Better-Auth with FastAPI"""

    @app.get("/api/auth/*", include_in_schema=False)
    async def auth_handler():
        """Proxy all auth requests to Better-Auth"""
        pass

    # Add CORS middleware for auth routes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )