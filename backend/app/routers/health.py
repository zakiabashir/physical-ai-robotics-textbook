"""
Health check endpoints with RAG component monitoring
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
import time
import logging

from app.services.embedding_service import embedding_service
from app.services.qdrant_client import QdrantClient
from app.services.retrieval_service import retrieval_service
from app.services.gemini_client import GeminiClient
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "0.1.0"
    }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """Detailed health check including RAG components"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "0.1.0",
        "components": {},
        "overall": "healthy"
    }

    # Check Qdrant connection
    try:
        qdrant_client = QdrantClient()
        stats = await qdrant_client.get_collection_stats()
        health_status["components"]["qdrant"] = {
            "status": "healthy",
            "collections": stats.get("collections", []),
            "total_documents": stats.get("total_documents", 0)
        }
    except Exception as e:
        health_status["components"]["qdrant"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall"] = "degraded"

    # Check Cohere API
    try:
        # Test embedding generation
        test_embedding = embedding_service.get_embedding("test")
        if test_embedding and len(test_embedding) > 0:
            health_status["components"]["cohere"] = {
                "status": "healthy",
                "embedding_dimension": len(test_embedding)
            }
        else:
            raise Exception("No embedding generated")
    except Exception as e:
        health_status["components"]["cohere"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall"] = "degraded"

    # Check Gemini API
    try:
        gemini_client = GeminiClient()
        # Simple test message
        test_response = await gemini_client.chat_completion(
            messages=[{"role": "user", "content": "Respond with 'OK'"}],
            max_tokens=10
        )
        if test_response:
            health_status["components"]["gemini"] = {
                "status": "healthy",
                "model": settings.GEMINI_MODEL
            }
        else:
            raise Exception("No response from Gemini")
    except Exception as e:
        health_status["components"]["gemini"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall"] = "degraded"

    # Check retrieval service
    try:
        # Test retrieval with a simple query
        retrieved = await retrieval_service.retrieve(
            query="Physical AI",
            limit=1,
            score_threshold=0.1  # Very low threshold for test
        )
        health_status["components"]["retrieval"] = {
            "status": "healthy",
            "collection_name": settings.COLLECTION_NAME,
            "can_retrieve": True
        }
    except Exception as e:
        health_status["components"]["retrieval"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall"] = "degraded"

    return health_status


@router.get("/health/rag", response_model=Dict[str, Any])
async def rag_health_check():
    """Specific RAG component health check"""
    rag_status = {
        "timestamp": time.time(),
        "ingestion": {},
        "retrieval": {},
        "generation": {}
    }

    # Check ingestion readiness
    try:
        qdrant_client = QdrantClient()
        stats = await qdrant_client.get_collection_stats()

        rag_status["ingestion"] = {
            "status": "ready",
            "collection_exists": settings.COLLECTION_NAME in stats.get("collections", []),
            "document_count": stats.get("total_documents", 0),
            "last_checked": time.time()
        }

        if stats.get("total_documents", 0) == 0:
            rag_status["ingestion"]["status"] = "needs_ingestion"
            rag_status["ingestion"]["message"] = "No documents found - run ingestion first"

    except Exception as e:
        rag_status["ingestion"] = {
            "status": "error",
            "error": str(e)
        }

    # Check retrieval performance
    try:
        start_time = time.time()
        retrieved = await retrieval_service.retrieve(
            query="test query",
            limit=5,
            score_threshold=0.5
        )
        retrieval_time = time.time() - start_time

        rag_status["retrieval"] = {
            "status": "healthy",
            "query_time_ms": round(retrieval_time * 1000, 2),
            "results_count": len(retrieved),
            "avg_score": sum(r.get("score", 0) for r in retrieved) / len(retrieved) if retrieved else 0
        }

        if retrieval_time > 2.0:  # If retrieval takes more than 2 seconds
            rag_status["retrieval"]["status"] = "slow"
            rag_status["retrieval"]["warning"] = "Retrieval time is above 2 seconds"

    except Exception as e:
        rag_status["retrieval"] = {
            "status": "error",
            "error": str(e)
        }

    # Check generation availability
    try:
        start_time = time.time()
        gemini_client = GeminiClient()
        response = await gemini_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Generation test successful'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        generation_time = time.time() - start_time

        rag_status["generation"] = {
            "status": "healthy",
            "response_time_ms": round(generation_time * 1000, 2),
            "model": settings.GEMINI_MODEL,
            "max_tokens": settings.GEMINI_MAX_TOKENS
        }

        if generation_time > 5.0:  # If generation takes more than 5 seconds
            rag_status["generation"]["status"] = "slow"
            rag_status["generation"]["warning"] = "Generation time is above 5 seconds"

    except Exception as e:
        rag_status["generation"] = {
            "status": "error",
            "error": str(e)
        }

    # Overall RAG status
    component_statuses = [
        rag_status["ingestion"].get("status"),
        rag_status["retrieval"].get("status"),
        rag_status["generation"].get("status")
    ]

    if "error" in component_statuses:
        rag_status["overall_status"] = "unhealthy"
    elif "slow" in component_statuses or "needs_ingestion" in component_statuses:
        rag_status["overall_status"] = "degraded"
    else:
        rag_status["overall_status"] = "healthy"

    return rag_status


@router.post("/health/ingestion/test", response_model=Dict[str, Any])
async def test_ingestion_pipeline():
    """Test the entire ingestion pipeline with a small sample"""
    test_results = {
        "timestamp": time.time(),
        "tests": {},
        "overall": "not_run"
    }

    # Test URL extraction
    try:
        from app.services.ingestion_service import ingestion_service
        urls = await ingestion_service.get_all_urls()

        test_results["tests"]["url_extraction"] = {
            "status": "passed",
            "urls_found": len(urls)
        }
    except Exception as e:
        test_results["tests"]["url_extraction"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test text extraction
    try:
        if test_results["tests"]["url_extraction"]["status"] == "passed":
            # Test with first URL
            first_url = urls[0]
            extracted = ingestion_service.extract_text_from_url(first_url)

            test_results["tests"]["text_extraction"] = {
                "status": "passed" if extracted["text"] else "failed",
                "url_tested": first_url,
                "chars_extracted": len(extracted.get("text", "")),
                "title": extracted.get("title", "")
            }
    except Exception as e:
        test_results["tests"]["text_extraction"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test embedding generation
    try:
        test_text = "This is a test for embedding generation"
        embedding = embedding_service.get_embedding(test_text)

        test_results["tests"]["embedding"] = {
            "status": "passed" if embedding and len(embedding) > 0 else "failed",
            "embedding_dimension": len(embedding) if embedding else 0
        }
    except Exception as e:
        test_results["tests"]["embedding"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test Qdrant storage
    try:
        from app.services.qdrant_client import QdrantClient
        qdrant_client = QdrantClient()

        # Create test collection
        test_collection = "health_check_test"
        await qdrant_client.create_collection(test_collection)

        # Test point insertion
        test_point = {
            "id": "test_point",
            "vector": [0.1] * settings.QDRANT_VECTOR_SIZE,
            "payload": {"test": True, "timestamp": time.time()}
        }

        await qdrant_client.upsert_vectors(test_collection, [test_point])

        # Clean up
        await qdrant_client.delete_collection(test_collection)

        test_results["tests"]["qdrant_storage"] = {
            "status": "passed",
            "vector_size": settings.QDRANT_VECTOR_SIZE
        }
    except Exception as e:
        test_results["tests"]["qdrant_storage"] = {
            "status": "failed",
            "error": str(e)
        }

    # Determine overall status
    test_statuses = [t.get("status") for t in test_results["tests"].values()]

    if all(s == "passed" for s in test_statuses):
        test_results["overall"] = "passed"
    elif any(s == "failed" for s in test_statuses):
        test_results["overall"] = "failed"
    else:
        test_results["overall"] = "partial"

    return test_results