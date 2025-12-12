"""
Physical AI & Humanoid Robotics Textbook - FastAPI Backend with AI Integration
Main application with Gemini AI for chat functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any, List, Optional
import time
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini (if available)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    # Configure with environment variable if available
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini AI initialized successfully")
    else:
        logger.warning("GEMINI_API_KEY not set, using fallback responses")
        GEMINI_AVAILABLE = False
except ImportError:
    logger.warning("Google Generative AI not installed")
    GEMINI_AVAILABLE = False
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {e}")
    GEMINI_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Physical AI Textbook API...")
    yield
    # Shutdown
    logger.info("Shutting down Physical AI Textbook API...")


# Create FastAPI application
app = FastAPI(
    title="Physical AI Textbook API - AI Enhanced",
    description="Backend API for the Physical AI & Humanoid Robotics interactive textbook",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API - AI Enhanced",
        "status": "running",
        "ai_enabled": GEMINI_AVAILABLE,
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "ai_enabled": GEMINI_AVAILABLE
    }


@app.get("/api/v1/info")
async def info():
    return {
        "name": "Physical AI Textbook API",
        "version": "0.1.0",
        "status": "ai_enhanced",
        "ai_enabled": GEMINI_AVAILABLE
    }


@app.get("/api/v1/test")
async def test():
    """Test endpoint to verify API is working"""
    return {
        "status": "ok",
        "message": "API is working correctly",
        "timestamp": time.time(),
        "ai_enabled": GEMINI_AVAILABLE
    }


def generate_ai_response(message: str, context: Optional[Dict] = None) -> str:
    """Generate AI response using Gemini or fallback"""

    if not GEMINI_AVAILABLE:
        # Fallback responses
        responses = [
            f"I understand you're asking about '{message}'. As a Physical AI assistant, I'd be happy to help you learn about robotics and AI integration. This is a simplified response while we enhance the AI capabilities.",
            f"That's an interesting question about '{message}'. In Physical AI and Humanoid Robotics, we explore the intersection of artificial intelligence and robotic systems. I'm here to guide you through these concepts!",
            f"You asked about '{message}'. Physical AI focuses on creating intelligent systems that can interact with the physical world, like humanoid robots that can perceive, reason, and act in their environment."
        ]
        import random
        return random.choice(responses)

    try:
        # Use Gemini for actual AI responses
        prompt = f"""You are an expert AI assistant for Physical AI & Humanoid Robotics.
        Answer the following question clearly and concisely:

        Question: {message}

        Provide helpful, educational responses about robotics, AI, and their applications."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"I apologize, but I'm having trouble processing your request about '{message}' right now. Please try again or contact support if the issue persists."


@app.post("/api/v1/chat/")
async def chat_endpoint(request: Dict[str, Any]):
    """Enhanced chat endpoint with AI responses"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        context = request.get("context", {})
        conversation_history = request.get("conversation_history", [])

        # Generate AI response
        ai_response = generate_ai_response(message, context)

        # Add contextual information about Physical AI
        if "physical ai" in message.lower() or "robot" in message.lower():
            ai_response += "\n\nWould you like to know more about specific aspects of Physical AI, such as perception systems, motion planning, or real-world applications?"

        return {
            "response": ai_response,
            "sources": [],
            "timestamp": time.time(),
            "ai_used": GEMINI_AVAILABLE
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/chat/feedback")
async def feedback_endpoint(request: Dict[str, Any]):
    """Simple feedback endpoint"""
    feedback_data = {
        "feedback": request,
        "timestamp": time.time()
    }
    logger.info(f"Feedback received: {feedback_data}")
    return {
        "status": "success",
        "message": "Thank you for your feedback!"
    }


@app.get("/api/v1/content/chapters")
async def get_chapters():
    """Get available chapters with Physical AI focus"""
    return {
        "chapters": [
            {
                "id": 1,
                "title": "Introduction to Physical AI",
                "description": "Understanding the fundamentals of AI in physical systems",
                "lessons": [
                    {"id": "ch1-l1", "title": "What is Physical AI?"},
                    {"id": "ch1-l2", "title": "Applications in Robotics"},
                    {"id": "ch1-l3", "title": "Sensing and Perception"},
                    {"id": "ch1-l4", "title": "Actuation and Control"},
                    {"id": "ch1-l5", "title": "Real-world Examples"}
                ]
            },
            {
                "id": 2,
                "title": "Humanoid Robotics",
                "description": "Design and control of humanoid robots",
                "lessons": [
                    {"id": "ch2-l1", "title": "Humanoid Robot Anatomy"},
                    {"id": "ch2-l2", "title": "Locomotion and Balance"},
                    {"id": "ch2-l3", "title": "Manipulation and Grasping"},
                    {"id": "ch2-l4", "title": "Human-Robot Interaction"},
                    {"id": "ch2-l5", "title": "Learning and Adaptation"}
                ]
            },
            {
                "id": 3,
                "title": "AI Control Systems",
                "description": "Intelligent control for robotic systems",
                "lessons": [
                    {"id": "ch3-l1", "title": "Neural Networks for Robotics"},
                    {"id": "ch3-l2", "title": "Reinforcement Learning"},
                    {"id": "ch3-l3", "title": "Computer Vision"},
                    {"id": "ch3-l4", "title": "Path Planning"},
                    {"id": "ch3-l5", "title": "Multi-agent Systems"}
                ]
            }
        ]
    }


@app.get("/api/v1/content/navigation")
async def get_navigation():
    """Get navigation structure"""
    return {
        "structure": {
            "chapters": [
                {
                    "id": "ch1",
                    "title": "Introduction to Physical AI",
                    "description": "Learn the basics of AI in physical systems",
                    "estimated_time": "2 hours",
                    "lessons": [
                        {
                            "id": "ch1-l1",
                            "title": "What is Physical AI?",
                            "duration": "15 min",
                            "completed": False
                        },
                        {
                            "id": "ch1-l2",
                            "title": "Applications in Robotics",
                            "duration": "20 min",
                            "completed": False
                        }
                    ]
                }
            ]
        }
    }


@app.get("/api/v1/suggestions")
async def get_suggestions():
    """Get topic suggestions for Physical AI learning"""
    return {
        "suggestions": [
            "How do humanoid robots maintain balance?",
            "What's the difference between reactive and deliberative control?",
            "Explain computer vision in robotics",
            "How does reinforcement learning work in robotics?",
            "What are proprioceptive sensors?",
            "Design principles for robotic manipulators",
            "AI approaches to motion planning",
            "Challenges in human-robot interaction"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))