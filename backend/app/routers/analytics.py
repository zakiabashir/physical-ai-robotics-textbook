"""
Analytics router for RAG system
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging

from app.services.analytics_service import rag_analytics
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Model for feedback submission"""
    query_id: str = Field(..., description="ID of the query being rated")
    score: int = Field(..., ge=1, le=5, description="Feedback score from 1 to 5")
    comment: Optional[str] = Field(None, description="Optional feedback comment")
    source_clicks: Optional[List[str]] = Field(default=[], description="List of source URLs clicked")


class FeedbackResponse(BaseModel):
    """Response for feedback submission"""
    message: str = Field(..., description="Success message")
    query_id: str = Field(..., description="Query ID that was rated")


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_analytics_dashboard(
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get analytics dashboard data

    Args:
        days: Number of days to analyze (1-365)

    Returns:
        Analytics dashboard data including metrics, top queries, and trends
    """
    try:
        # Validate days parameter
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )

        # Get analytics data
        dashboard_data = rag_analytics.get_analytics_dashboard(days=days)

        logger.info(f"Retrieved analytics dashboard for {days} days")
        return dashboard_data

    except Exception as e:
        logger.error(f"Error retrieving analytics dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics data"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback for a query response

    Args:
        feedback: Feedback data including query ID, score, and optional comment

    Returns:
        Confirmation of feedback submission
    """
    try:
        # Validate query ID format
        if not feedback.query_id or len(feedback.query_id) < 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid query ID"
            )

        # Track feedback
        rag_analytics.track_feedback(
            query_id=feedback.query_id,
            score=feedback.score,
            comment=feedback.comment
        )

        # Track source clicks if provided
        for source_url in feedback.source_clicks:
            rag_analytics.track_source_click(source_url, feedback.query_id)

        logger.info(f"Received feedback for query {feedback.query_id}: score={feedback.score}")

        return FeedbackResponse(
            message="Feedback submitted successfully",
            query_id=feedback.query_id
        )

    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit feedback"
        )


@router.get("/export", response_model=Dict[str, Any])
async def export_analytics(
    format: str = Query(default="json", regex="^(json|csv)$", description="Export format")
):
    """
    Export analytics data

    Args:
        format: Export format (json or csv)

    Returns:
        Exported analytics data
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(
                status_code=400,
                detail="Format must be 'json' or 'csv'"
            )

        # Export data
        exported_data = rag_analytics.export_analytics(format=format)

        logger.info(f"Exported analytics data in {format} format")
        return {"data": exported_data, "format": format}

    except Exception as e:
        logger.error(f"Error exporting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export analytics data"
        )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_performance_metrics():
    """
    Get current performance metrics

    Returns:
        Real-time performance metrics
    """
    try:
        # Get current performance metrics
        metrics = rag_analytics.performance_metrics.copy()

        # Add current time
        metrics["timestamp"] = rag_analytics.query_analytics.get("timestamp", 0)

        return metrics

    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve performance metrics"
        )


@router.get("/popular", response_model=Dict[str, Any])
async def get_popular_content(
    limit: int = Query(default=10, ge=1, le=50, description="Number of items to return")
):
    """
    Get popular queries and sources

    Args:
        limit: Number of items to return (1-50)

    Returns:
        Popular queries and sources with counts
    """
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 50"
            )

        # Get recent analytics data
        dashboard_data = rag_analytics.get_analytics_dashboard(days=30)  # Last 30 days

        # Limit results
        popular_queries = dashboard_data["top_queries"][:limit]
        popular_sources = dashboard_data["top_sources"][:limit]

        return {
            "popular_queries": [
                {"query": query, "count": count}
                for query, count in popular_queries
            ],
            "popular_sources": [
                {"source": source, "clicks": clicks}
                for source, clicks in popular_sources
            ],
            "period": "Last 30 days"
        }

    except Exception as e:
        logger.error(f"Error getting popular content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve popular content"
        )


@router.get("/health", response_model=Dict[str, Any])
async def analytics_health():
    """
    Health check for analytics service

    Returns:
        Health status of analytics service
    """
    try:
        # Basic health check
        cache_stats = rag_analytics.cache_service.get_stats()

        return {
            "status": "healthy",
            "service": "analytics",
            "cache_stats": cache_stats,
            "tracked_queries": len(rag_analytics.query_history),
            "daily_stats_count": len(rag_analytics.daily_stats)
        }

    except Exception as e:
        logger.error(f"Error in analytics health check: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "error": str(e)
        }


@router.post("/reset", response_model=Dict[str, Any])
async def reset_analytics(
    confirm: bool = Query(..., description="Confirmation token (must be True)")
):
    """
    Reset all analytics data (admin only)

    Args:
        confirm: Must be True to confirm reset

    Returns:
        Confirmation of reset
    """
    # In production, you'd want proper authentication here
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation token required"
        )

    try:
        # Clear analytics data
        rag_analytics.query_history.clear()
        rag_analytics.session_stats.clear()
        rag_analytics.daily_stats.clear()
        rag_analytics.performance_metrics = {
            "total_queries": 0,
            "avg_response_time": 0,
            "p95_response_time": 0,
            "p99_response_time": 0,
            "cache_hit_rate": 0,
            "error_rate": 0
        }
        rag_analytics.query_analytics = {
            "query_lengths": [],
            "retrieval_counts": [],
            "relevance_scores": [],
            "source_clicks": {},
            "feedback_scores": []
        }

        logger.warning("Analytics data reset by administrator")

        return {
            "message": "Analytics data successfully reset",
            "timestamp": rag_analytics.query_analytics.get("timestamp", 0)
        }

    except Exception as e:
        logger.error(f"Error resetting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reset analytics data"
        )