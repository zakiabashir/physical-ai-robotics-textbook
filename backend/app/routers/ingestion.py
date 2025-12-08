"""
Routers for data ingestion endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.services.ingestion_service import ingestion_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class IngestionStatus(BaseModel):
    """Model for ingestion status"""
    total_urls: int = Field(..., description="Total URLs to process")
    successful_urls: int = Field(..., description="Successfully processed URLs")
    failed_urls: int = Field(..., description="Failed URLs")
    total_chunks: int = Field(..., description="Total chunks stored")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    errors: list = Field(default_factory=list, description="List of errors")


class SingleURLRequest(BaseModel):
    """Model for single URL ingestion request"""
    url: str = Field(..., description="URL to ingest")
    force: bool = Field(False, description="Force re-ingestion even if already exists")


@router.post("/ingest/all", response_model=Dict[str, Any])
async def ingest_all_content(
    background_tasks: BackgroundTasks,
    max_urls: Optional[int] = Query(None, description="Maximum URLs to process (for testing)")
):
    """
    Ingest all content from the sitemap
    This runs in the background
    """
    try:
        logger.info(f"Starting ingestion of all content (max_urls={max_urls})")

        # Run ingestion in background
        background_tasks.add_task(
            ingestion_service.ingest_book,
            max_urls=max_urls
        )

        return {
            "message": "Ingestion started in background",
            "status": "processing",
            "sitemap_url": settings.SITEMAP_URL,
            "collection_name": settings.COLLECTION_NAME
        }

    except Exception as e:
        logger.error(f"Error starting ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/url", response_model=Dict[str, Any])
async def ingest_single_url(request: SingleURLRequest):
    """
    Ingest content from a single URL
    """
    try:
        logger.info(f"Ingesting single URL: {request.url}")

        result = await ingestion_service.ingest_url(request.url)

        return {
            "url": request.url,
            "success": result["success"],
            "chunks_created": result["chunks_created"],
            "chunks_stored": result["chunks_stored"],
            "error": result["error"]
        }

    except Exception as e:
        logger.error(f"Error ingesting URL {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/status", response_model=Dict[str, Any])
async def get_ingestion_status():
    """
    Get current ingestion status
    """
    try:
        # Get collection stats
        stats = await ingestion_service.qdrant_client.get_collection_stats()

        return {
            "collection_name": settings.COLLECTION_NAME,
            "total_documents": stats.get("total_documents", 0),
            "collections": stats.get("collections", []),
            "sitemap_url": settings.SITEMAP_URL,
            "qdrant_url": settings.QDRANT_URL
        }

    except Exception as e:
        logger.error(f"Error getting ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/test", response_model=Dict[str, Any])
async def test_ingestion(limit: int = Query(5, description="Number of URLs to test")):
    """
    Test ingestion with a limited number of URLs
    """
    try:
        logger.info(f"Testing ingestion with {limit} URLs")

        result = await ingestion_service.ingest_book(max_urls=limit)

        return {
            "test_completed": True,
            "total_urls": result["total_urls"],
            "successful_urls": result["successful_urls"],
            "failed_urls": result["failed_urls"],
            "total_chunks": result["total_chunks"],
            "duration": result.get("duration"),
            "errors": result["errors"][:5]  # Limit errors shown
        }

    except Exception as e:
        logger.error(f"Error during test ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ingest/clear", response_model=Dict[str, Any])
async def clear_collection():
    """
    Clear the entire collection
    """
    try:
        logger.warning(f"Clearing collection: {settings.COLLECTION_NAME}")

        await ingestion_service.qdrant_client.delete_collection(settings.COLLECTION_NAME)

        return {
            "message": f"Collection {settings.COLLECTION_NAME} cleared successfully",
            "collection_name": settings.COLLECTION_NAME
        }

    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))