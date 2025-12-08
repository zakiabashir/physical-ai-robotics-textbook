"""
User model for the Physical AI Textbook API
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from . import Base


class User(Base):
    """User model for authentication and personalization"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # UUID v4
    email = Column(String, unique=True, index=True, nullable=False)
    education = Column(String, nullable=True)  # high-school, bachelor, master, phd, other
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # User preferences
    preferences = Column(JSON, default={})

    # Background information from onboarding
    background = Column(JSON, default={})

    # Hardware capabilities
    hardware = Column(JSON, default={})

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"