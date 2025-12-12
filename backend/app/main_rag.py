"""
Physical AI & Humanoid Robotics Textbook - FastAPI Backend
Main application with RAG support - Simplified for Railway deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
from typing import Dict, Any, List, Optional
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services with graceful fallback
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams
    import cohere
    import google.generativeai as genai

    # Check if all required services are available
    qdrant_available = os.getenv("QDRANT_URL") and os.getenv("QDRANT_API_KEY")
    cohere_available = os.getenv("COHERE_API_KEY")
    gemini_available = os.getenv("GEMINI_API_KEY")

    # Initialize clients if keys are available
    if qdrant_available:
        qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        logger.info("Qdrant client initialized")
    else:
        logger.warning("Qdrant credentials not available")
        qdrant_client = None

    if cohere_available:
        cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
        logger.info("Cohere client initialized")
    else:
        logger.warning("Cohere API key not available")
        cohere_client = None

    if gemini_available:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Gemini AI initialized")
    else:
        logger.warning("Gemini API key not available")
        gemini_model = None

except ImportError as e:
    logger.error(f"Import error: {e}")
    qdrant_client = None
    cohere_client = None
    gemini_model = None
except Exception as e:
    logger.error(f"Service initialization error: {e}")
    qdrant_client = None
    cohere_client = None
    gemini_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Physical AI Textbook API with RAG...")
    yield
    # Shutdown
    logger.info("Shutting down Physical AI Textbook API...")


# Create FastAPI application
app = FastAPI(
    title="Physical AI Textbook API - RAG Enhanced",
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
        "message": "Physical AI & Humanoid Robotics Textbook API - RAG Enhanced",
        "status": "running",
        "services": {
            "qdrant": qdrant_client is not None,
            "cohere": cohere_client is not None,
            "gemini": gemini_model is not None,
            "rag_enabled": qdrant_client is not None and cohere_client is not None
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "qdrant": qdrant_client is not None,
            "cohere": cohere_client is not None,
            "gemini": gemini_model is not None,
            "rag_enabled": qdrant_client is not None and cohere_client is not None
        }
    }


@app.get("/api/v1/health/detailed")
async def health_detailed():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": "connected",
            "ai_model": "gemini-2.0-flash" if gemini_model else "fallback",
            "rag": qdrant_client is not None and cohere_client is not None,
            "vector_db": "qdrant" if qdrant_client else "not connected",
            "embedding_model": "cohere" if cohere_client else "not connected"
        },
        "version": "0.1.0"
    }


@app.get("/api/v1/info")
async def info():
    return {
        "name": "Physical AI Textbook API",
        "version": "0.1.0",
        "status": "rag_enhanced",
        "services": {
            "qdrant": qdrant_client is not None,
            "cohere": cohere_client is not None,
            "gemini": gemini_model is not None
        }
    }


@app.get("/api/v1/test")
async def test():
    """Test endpoint to verify API is working"""
    return {
        "status": "ok",
        "message": "API is working correctly",
        "timestamp": time.time(),
        "rag_enabled": qdrant_client is not None and cohere_client is not None
    }


async def retrieve_relevant_content(query: str, limit: int = 5) -> List[Dict]:
    """Retrieve relevant content from Qdrant"""
    if not qdrant_client or not cohere_client:
        return []

    try:
        # Create embedding for the query
        embed_response = cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        query_vector = embed_response.embeddings[0]

        # Search in Qdrant
        search_result = qdrant_client.search(
            collection_name=os.getenv("COLLECTION_NAME", "humanoid_ai_book"),
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )

        # Format results
        results = []
        for hit in search_result:
            results.append({
                "content": hit.payload.get("text", ""),
                "title": hit.payload.get("title", ""),
                "url": hit.payload.get("url", ""),
                "score": hit.score
            })

        return results
    except Exception as e:
        logger.error(f"Error retrieving content: {e}")
        return []


def generate_contextual_response(query: str, context: List[Dict]) -> str:
    """Generate response using retrieved context"""
    if not gemini_model:
        return "AI service not available. Please check your API keys."

    context_text = ""
    if context:
        context_text = "\n\nRelevant content from the textbook:\n"
        for i, doc in enumerate(context, 1):
            context_text += f"\n{i}. {doc['title']}: {doc['content'][:300]}...\n"

    prompt = f"""You are a knowledgeable assistant for the Physical AI & Humanoid Robotics textbook.
    Use the following context to answer the user's question accurately.

    User Question: {query}
    {context_text}

    Provide a comprehensive answer based on the textbook content. If the context doesn't contain
    relevant information, say so and provide a general response about the topic.
    """

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Sorry, I encountered an error while generating the response."


@app.post("/api/v1/chat/")
async def chat_endpoint(request: Dict[str, Any]):
    """Enhanced chat endpoint with RAG support"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Get context if available
        context_data = request.get("context", {})

        # Try to retrieve relevant content if RAG is enabled
        retrieved_content = []
        if qdrant_client and cohere_client:
            retrieved_content = await retrieve_relevant_content(message)

        # Generate response
        if retrieved_content:
            response_text = generate_contextual_response(message, retrieved_content)
            sources = [{"title": doc["title"], "url": doc["url"], "score": doc["score"]} for doc in retrieved_content]
        else:
            # Fallback response
            response_text = f"I understand you're asking about '{message}'. "
            if not (qdrant_client and cohere_client and gemini_model):
                response_text += "Note: Some AI services are not configured. "
            response_text += "As a Physical AI assistant, I'm here to help you learn about robotics and AI integration."
            sources = []

        return {
            "response": response_text,
            "sources": sources,
            "timestamp": time.time(),
            "rag_used": len(retrieved_content) > 0,
            "ai_used": gemini_model is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/chat/feedback")
async def feedback_endpoint(request: Dict[str, Any]):
    """Feedback endpoint"""
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