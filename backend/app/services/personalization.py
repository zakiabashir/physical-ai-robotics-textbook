"""
Personalization service for adaptive learning experience
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import logging

from ..database.models import User, ChatSession, ChatMessage
from ..core.config import settings

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Service for personalizing learning content based on user profile and behavior"""

    def __init__(self):
        self.content_difficulty_map = {
            "beginner": {
                "complexity_threshold": 0.3,
                "preferred_depth": "overview",
                "code_example_level": "basic"
            },
            "intermediate": {
                "complexity_threshold": 0.6,
                "preferred_depth": "detailed",
                "code_example_level": "intermediate"
            },
            "advanced": {
                "complexity_threshold": 0.8,
                "preferred_depth": "in-depth",
                "code_example_level": "advanced"
            }
        }

    async def get_personalized_content(
        self,
        user_id: str,
        lesson_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get content personalized for the user"""

        # Get user profile
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return self._get_default_content()

        # Analyze user's learning style and background
        adaptations = await self._analyze_user_profile(user, db)

        # Get content adaptations based on preferences
        content = {
            "language": user.preferences.get("language", "en"),
            "learningStyle": self._adapt_for_learning_style(
                user.preferences.get("learningStyle", "mixed"),
                adaptations
            ),
            "difficulty": self._adjust_difficulty(
                user.preferences.get("backgroundLevel", "beginner"),
                adaptations
            ),
            "codeExamples": self._customize_code_examples(
                user.hardware.get("hasGPU", False),
                user.background.get("experience", [])
            ),
            "recommendations": await self._get_recommendations(user, lesson_id, db)
        }

        return content

    async def update_user_profile(
        self,
        user_id: str,
        interactions: List[Dict[str, Any]],
        db: AsyncSession
    ) -> None:
        """Update user profile based on interactions"""

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        # Analyze interaction patterns
        insights = self._analyze_interactions(interactions)

        # Update preferences based on behavior
        updated_preferences = user.preferences.copy()

        if insights.get("preferred_language"):
            updated_preferences["language"] = insights["preferred_language"]

        if insights.get("code_engagement"):
            if insights["code_engagement"] > 0.7:
                updated_preferences["learningStyle"] = "kinesthetic"
            elif insights["code_engagement"] < 0.3:
                updated_preferences["learningStyle"] = "textual"

        if insights.get("difficulty_preference"):
            updated_preferences["backgroundLevel"] = insights["difficulty_preference"]

        # Update the user
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(preferences=updated_preferences)
        )
        await db.execute(stmt)
        await db.commit()

    async def _analyze_user_profile(
        self,
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze user's learning patterns and behavior"""

        adaptations = {}

        # Analyze chat history for patterns
        result = await db.execute(
            select(ChatMessage)
            .join(ChatSession)
            .where(ChatSession.user_id == user.id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(50)
        )
        messages = result.scalars().all()

        # Count question types
        question_types = {
            "conceptual": 0,
            "practical": 0,
            "troubleshooting": 0
        }

        for message in messages:
            if message.role == "user":
                content = message.content.lower()
                if any(word in content for word in ["what", "why", "explain", "define"]):
                    question_types["conceptual"] += 1
                elif any(word in content for word in ["how", "implement", "code", "example"]):
                    question_types["practical"] += 1
                elif any(word in content for word in ["error", "issue", "problem", "fix"]):
                    question_types["troubleshooting"] += 1

        # Determine learning style preference
        total_questions = sum(question_types.values())
        if total_questions > 0:
            if question_types["practical"] / total_questions > 0.6:
                adaptations["learning_style"] = "kinesthetic"
            elif question_types["conceptual"] / total_questions > 0.6:
                adaptations["learning_style"] = "visual"

        return adaptations

    def _adapt_for_learning_style(
        self,
        style: str,
        adaptations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt content based on learning style"""

        base_adaptations = {
            "visual": {
                "include_diagrams": True,
                "include_videos": True,
                "text_density": "medium",
                "code_annotations": True
            },
            "kinesthetic": {
                "include_diagrams": False,
                "include_videos": True,
                "text_density": "low",
                "code_examples": "high",
                "interactive_elements": True
            },
            "textual": {
                "include_diagrams": False,
                "include_videos": False,
                "text_density": "high",
                "code_examples": "minimal",
                "interactive_elements": False
            },
            "mixed": {
                "include_diagrams": True,
                "include_videos": True,
                "text_density": "medium",
                "code_examples": "medium"
            }
        }

        # Override with adaptations from behavior analysis
        user_style = adaptations.get("learning_style", style)

        return base_adaptations.get(user_style, base_adaptations["mixed"])

    def _adjust_difficulty(
        self,
        level: str,
        adaptations: Dict[str, Any]
    ) -> str:
        """Adjust content difficulty based on user level and performance"""

        # For now, return the user's preferred level
        # In the future, this could be adjusted based on quiz scores and interaction patterns
        return level

    def _customize_code_examples(
        self,
        has_gpu: bool,
        experience: List[str]
    ) -> Dict[str, Any]:
        """Customize code examples based on user's hardware and experience"""

        customizations = {
            "show_gpu_examples": has_gpu,
            "show_ros_examples": any("ros" in exp.lower() for exp in experience),
            "show_python_only": len(experience) == 0 or all(
                exp.lower() in ["python"] for exp in experience
            ),
            "complexity_level": "beginner" if not experience else "intermediate"
        }

        return customizations

    async def _get_recommendations(
        self,
        user: User,
        current_lesson: str,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations"""

        recommendations = []

        # Based on user's education level
        if user.education in ["high-school"]:
            recommendations.append({
                "type": "prerequisite",
                "title": "Programming Fundamentals",
                "description": "Basic programming concepts to get started"
            })

        # Based on user's goals
        goals = user.background.get("goals", [])
        if "research" in goals:
            recommendations.append({
                "type": "advanced_topic",
                "title": "Academic Papers on Physical AI",
                "description": "Latest research in embodied intelligence"
            })
        elif "industry" in goals:
            recommendations.append({
                "type": "practical_application",
                "title": "Industry Case Studies",
                "description": "Real-world implementations of Physical AI"
            })

        # Based on user's hardware
        if not user.hardware.get("hasRobot"):
            recommendations.append({
                "type": "setup",
                "title": "Getting Started with Simulation",
                "description": "Set up Gazebo or Webots for robot simulation"
            })

        return recommendations[:5]  # Limit to 5 recommendations

    def _analyze_interactions(
        self,
        interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user interactions to infer preferences"""

        insights = {}

        # Language preference
        languages = [i.get("language") for i in interactions if i.get("language")]
        if languages:
            most_common = max(set(languages), key=languages.count)
            insights["preferred_language"] = most_common

        # Code engagement
        code_interactions = [i for i in interactions if "code" in i.get("type", "").lower()]
        if len(interactions) > 0:
            insights["code_engagement"] = len(code_interactions) / len(interactions)

        return insights

    def _get_default_content(self) -> Dict[str, Any]:
        """Get default content when user is not authenticated"""

        return {
            "language": "en",
            "learningStyle": "mixed",
            "difficulty": "beginner",
            "codeExamples": {
                "show_gpu_examples": False,
                "show_ros_examples": True,
                "show_python_only": True,
                "complexity_level": "beginner"
            },
            "recommendations": [
                {
                    "type": "authentication",
                    "title": "Create an Account",
                    "description": "Sign up to save your progress and get personalized recommendations"
                }
            ]
        }