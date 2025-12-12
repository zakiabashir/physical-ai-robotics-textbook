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
        collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")

        # Check if collection exists
        try:
            collections = qdrant_client.get_collections()
            collection_exists = any(c.name == collection_name for c in collections.collections)

            if not collection_exists:
                logger.warning(f"Collection '{collection_name}' does not exist")
                return []

        except Exception as e:
            logger.error(f"Error checking collections: {e}")
            return []

        # Create embedding for the query
        embed_response = cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        query_vector = embed_response.embeddings[0]

        # Search in Qdrant
        from qdrant_client.http import models

        search_result = qdrant_client.query_points(
            collection_name=collection_name,
            query=models.NamedVector(
                name="",
                vector=query_vector
            ),
            limit=limit,
            with_payload=True
        )

        # Check if we got any results
        if not search_result.points:
            logger.warning(f"No results found for query: {query}")
            return []

        # Format results
        results = []
        for hit in search_result.points:
            results.append({
                "content": hit.payload.get("text", ""),
                "title": hit.payload.get("title", ""),
                "url": hit.payload.get("url", ""),
                "score": hit.score
            })

        logger.info(f"Retrieved {len(results)} documents from Qdrant")
        return results

    except Exception as e:
        logger.error(f"Error retrieving content: {e}")
        return []


def generate_contextual_response(query: str, context: List[Dict]) -> str:
    """Generate response using retrieved context"""
    if not gemini_model:
        logger.warning("Gemini model not available")
        return "AI service not available. Please check your API keys."

    context_text = ""
    if context:
        context_text = "\n\nRelevant content from the textbook:\n"
        for i, doc in enumerate(context, 1):
            context_text += f"\n{i}. {doc['title']}: {doc['content'][:300]}...\n"
        logger.info(f"Using {len(context)} context documents for response")

    prompt = f"""You are a knowledgeable assistant for the Physical AI & Humanoid Robotics textbook.
    Use the following context to answer the user's question accurately.

    User Question: {query}
    {context_text}

    Provide a comprehensive answer based on the textbook content. If the context doesn't contain
    relevant information, say so and provide a general response about the topic.
    """

    try:
        logger.info(f"Generating response with Gemini for query: {query[:50]}...")
        response = gemini_model.generate_content(prompt)
        response_text = response.text
        logger.info(f"Gemini response generated successfully")
        return response_text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        # Return a fallback response about Physical AI
        return f"I understand you're asking about '{query}'. As a Physical AI assistant, I'm here to help you learn about robotics and AI integration."


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


@app.get("/api/v1/health/rag")
async def health_rag():
    collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")
    collection_info = {
        "exists": False,
        "document_count": 0,
        "status": "not_initialized"
    }

    if qdrant_client:
        try:
            from qdrant_client.http.models import Distance, VectorParams
            collections = qdrant_client.get_collections()
            collection_exists = any(c.name == collection_name for c in collections.collections)

            if collection_exists:
                collection_data = qdrant_client.get_collection(collection_name)
                collection_info = {
                    "exists": True,
                    "document_count": collection_data.points_count,
                    "status": "initialized",
                    "vector_size": collection_data.config.params.vectors.size
                }
        except Exception as e:
            logger.error(f"Error checking collection: {e}")

    return {
        "status": "healthy",
        "rag_status": collection_info["status"],
        "vector_db": "qdrant",
        "embedding_model": "cohere",
        "ai_enabled": gemini_model is not None,
        "collection": {
            "name": collection_name,
            "exists": collection_info["exists"],
            "document_count": collection_info.get("document_count", 0)
        },
        "timestamp": time.time()
    }


@app.post("/api/v1/ingest/sample")
async def ingest_sample_data():
    """Ingest sample Physical AI content into Qdrant for testing"""
    if not qdrant_client or not cohere_client:
        raise HTTPException(status_code=503, detail="RAG services not available")

    collection_name = os.getenv("COLLECTION_NAME", "humanoid_ai_book")

    try:
        from qdrant_client.http.models import Distance, VectorParams

        # Create collection if it doesn't exist
        try:
            qdrant_client.get_collection(collection_name)
        except:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {collection_name}")

        # Sample content about Physical AI
        sample_docs = [
            {
                "text": "Physical AI refers to artificial intelligence systems that interact with the physical world through sensors and actuators. Unlike purely digital AI, Physical AI systems must perceive, reason about, and act in real-world environments. This includes robots, autonomous vehicles, and smart devices that can manipulate physical objects.",
                "title": "Introduction to Physical AI",
                "url": "/docs/intro"
            },
            {
                "text": "Humanoid robots are designed to mimic human form and function. They typically feature a torso, head, two arms, and two legs. Key challenges in humanoid robotics include balance control, bipedal locomotion, manipulation skills, and human-robot interaction. Famous examples include ASIMO, Atlas, and Pepper.",
                "title": "Humanoid Robotics Fundamentals",
                "url": "/docs/chapter-1/lesson-1"
            },
            {
                "text": "Computer vision enables robots to perceive and understand visual information from the world. Key techniques include image processing, object detection, facial recognition, and depth sensing. Modern approaches use deep learning and convolutional neural networks to achieve human-level performance in many visual tasks.",
                "title": "Perception and Computer Vision",
                "url": "/docs/chapter-2/lesson-3"
            },
            {
                "text": "Reinforcement learning is a machine learning paradigm where an agent learns to make decisions by taking actions in an environment to maximize cumulative reward. In robotics, RL is used for teaching complex behaviors like walking, grasping, and manipulation through trial and error, often combined with simulation for efficient learning.",
                "title": "Reinforcement Learning in Robotics",
                "url": "/docs/chapter-3/lesson-2"
            },
            {
                "text": "Actuators are the muscles of robots, converting energy into physical motion. Common types include electric motors (servo, stepper, brushless DC), hydraulic systems, pneumatic systems, and newer technologies like shape memory alloys and artificial muscles. The choice of actuator depends on factors like power, precision, speed, and weight requirements.",
                "title": "Actuation Systems",
                "url": "/docs/chapter-4/lesson-1"
            }
        ]

        # Create embeddings for each document
        texts = [doc["text"] for doc in sample_docs]
        embed_response = cohere_client.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"
        )

        # Upload to Qdrant
        points = []
        for i, (doc, embedding) in enumerate(zip(sample_docs, embed_response.embeddings)):
            points.append({
                "id": i,
                "vector": embedding,
                "payload": {
                    "text": doc["text"],
                    "title": doc["title"],
                    "url": doc["url"]
                }
            })

        qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )

        return {
            "status": "success",
            "message": f"Successfully ingested {len(sample_docs)} documents",
            "collection": collection_name
        }

    except Exception as e:
        logger.error(f"Error ingesting data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest data: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))