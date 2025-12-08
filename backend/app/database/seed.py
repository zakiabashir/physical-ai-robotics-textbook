"""
Database seeding script for initial data
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database import AsyncSessionLocal
from app.database.models import User, ChatSession
import logging

logger = logging.getLogger(__name__)


async def create_sample_user(session: AsyncSession) -> User:
    """Create a sample user for testing"""

    user = User(
        id=str(uuid.uuid4()),
        email="demo@physical-ai-robotics.org",
        education="bachelor",
        preferences={
            "language": "en",
            "learningStyle": "visual",
            "backgroundLevel": "intermediate",
            "notifications": {
                "email": True,
                "browser": False
            }
        },
        background={
            "experience": ["python", "basic-robotics"],
            "education": "bachelor",
            "goals": ["industry"]
        },
        hardware={
            "hasRobot": False,
            "hasGPU": True,
            "platform": "windows"
        }
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"Created sample user: {user.email}")
    return user


async def create_sample_chat_session(session: AsyncSession, user_id: str) -> ChatSession:
    """Create a sample chat session"""

    chat_session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        lesson_context="1.1",  # Chapter 1, Lesson 1
        is_active=True
    )

    session.add(chat_session)
    await session.commit()
    await session.refresh(chat_session)

    logger.info(f"Created sample chat session: {chat_session.id}")
    return chat_session


async def seed_database():
    """Seed the database with initial data"""

    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting database seeding...")

            # Check if demo user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "demo@physical-ai-robotics.org")
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                # Create sample user
                user = await create_sample_user(session)

                # Create sample chat session
                await create_sample_chat_session(session, user.id)

                logger.info("Database seeding completed successfully!")
            else:
                logger.info("Demo user already exists, skipping seeding")

        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())