"""FastAPI dependency injection for core services"""

from typing import Generator
import logging

from ..services.chatbot import PhysicalAIChatbot

logger = logging.getLogger(__name__)

# Global instances
_chatbot_instance = None


async def get_chatbot() -> PhysicalAIChatbot:
    """Get or create chatbot instance"""
    global _chatbot_instance

    if _chatbot_instance is None:
        logger.info("Initializing PhysicalAI Chatbot...")
        _chatbot_instance = PhysicalAIChatbot()

        # Initialize with textbook content
        await _chatbot.initialize_with_content()
        logger.info("PhysicalAI Chatbot initialized successfully")

    return _chatbot_instance


def get_settings():
    """Get application settings"""
    from .config import settings
    return settings