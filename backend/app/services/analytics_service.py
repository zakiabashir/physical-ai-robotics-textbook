"""
Analytics service for tracking RAG usage and performance
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RAGAnalytics:
    """Analytics service for RAG system"""

    def __init__(self):
        # In-memory storage for analytics (in production, use a database)
        self.query_history = deque(maxlen=10000)  # Store last 10k queries
        self.session_stats = defaultdict(dict)
        self.daily_stats = defaultdict(lambda: {
            "queries": 0,
            "avg_retrieval_time": 0,
            "avg_generation_time": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "fallbacks": 0,
            "popular_queries": defaultdict(int),
            "error_count": 0
        })

        # Performance metrics
        self.performance_metrics = {
            "total_queries": 0,
            "avg_response_time": 0,
            "p95_response_time": 0,
            "p99_response_time": 0,
            "cache_hit_rate": 0,
            "error_rate": 0
        }

        # Query analytics
        self.query_analytics = {
            "query_lengths": [],
            "retrieval_counts": [],
            "relevance_scores": [],
            "source_clicks": defaultdict(int),
            "feedback_scores": []
        }

    def track_query(self, query: str, session_id: str, user_id: Optional[str] = None) -> str:
        """Track a new query"""
        query_id = str(uuid.uuid4())
        timestamp = time.time()

        # Store query details
        self.query_history.append({
            "query_id": query_id,
            "session_id": session_id,
            "user_id": user_id,
            "query": query,
            "timestamp": timestamp,
            "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        })

        # Update session
        self.session_stats[session_id]["start_time"] = timestamp
        self.session_stats[session_id]["query_count"] = self.session_stats[session_id].get("query_count", 0) + 1

        # Update daily stats
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        self.daily_stats[date_str]["queries"] += 1
        self.daily_stats[date_str]["popular_queries"][query.lower()] += 1

        # Track query length
        self.query_analytics["query_lengths"].append(len(query))

        # Keep only recent query lengths
        if len(self.query_analytics["query_lengths"]) > 1000:
            self.query_analytics["query_lengths"] = self.query_analytics["query_lengths"][-1000:]

        return query_id

    def track_retrieval(self, query_id: str, retrieval_time: float,
                        retrieved_count: int, avg_score: float):
        """Track retrieval performance"""
        # Update query record
        for query in reversed(self.query_history):
            if query["query_id"] == query_id:
                query["retrieval_time"] = retrieval_time
                query["retrieved_count"] = retrieved_count
                query["avg_score"] = avg_score
                break

        # Track metrics
        self.query_analytics["retrieval_counts"].append(retrieved_count)
        self.query_analytics["relevance_scores"].append(avg_score)

        # Keep only recent metrics
        if len(self.query_analytics["retrieval_counts"]) > 1000:
            self.query_analytics["retrieval_counts"] = self.query_analytics["retrieval_counts"][-1000:]
        if len(self.query_analytics["relevance_scores"]) > 1000:
            self.query_analytics["relevance_scores"] = self.query_analytics["relevance_scores"][-1000:]

        # Update daily stats
        date_str = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
        daily = self.daily_stats[date_str]

        # Update average retrieval time
        if daily["queries"] > 0:
            daily["avg_retrieval_time"] = (
                (daily["avg_retrieval_time"] * (daily["queries"] - 1) + retrieval_time) /
                daily["queries"]
            )

    def track_generation(self, query_id: str, generation_time: float,
                         token_count: int, use_fallback: bool):
        """Track generation performance"""
        # Update query record
        for query in reversed(self.query_history):
            if query["query_id"] == query_id:
                query["generation_time"] = generation_time
                query["token_count"] = token_count
                query["use_fallback"] = use_fallback
                query["completed"] = True
                break

        # Update daily stats
        date_str = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
        daily = self.daily_stats[date_str]

        if use_fallback:
            daily["fallbacks"] += 1

        # Update average generation time
        if daily["queries"] > 0:
            daily["avg_generation_time"] = (
                (daily["avg_generation_time"] * (daily["queries"] - 1) + generation_time) /
                daily["queries"]
            )

        # Update overall performance metrics
        self._update_performance_metrics()

    def track_cache_hit(self, query_id: str, hit: bool):
        """Track cache performance"""
        date_str = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")

        if hit:
            self.daily_stats[date_str]["cache_hits"] += 1
        else:
            self.daily_stats[date_str]["cache_misses"] += 1

    def track_source_click(self, source_url: str, query_id: str):
        """Track when user clicks on a source"""
        self.query_analytics["source_clicks"][source_url] += 1

        # Update query record
        for query in reversed(self.query_history):
            if query["query_id"] == query_id:
                if "source_clicks" not in query:
                    query["source_clicks"] = []
                query["source_clicks"].append({
                    "source_url": source_url,
                    "timestamp": time.time()
                })
                break

    def track_feedback(self, query_id: str, score: int, comment: Optional[str] = None):
        """Track user feedback"""
        self.query_analytics["feedback_scores"].append(score)

        # Update query record
        for query in reversed(self.query_history):
            if query["query_id"] == query_id:
                query["feedback"] = {
                    "score": score,
                    "comment": comment,
                    "timestamp": time.time()
                }
                break

    def track_error(self, query_id: str, error_type: str, error_message: str):
        """Track errors"""
        date_str = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
        self.daily_stats[date_str]["error_count"] += 1

        # Update query record
        for query in reversed(self.query_history):
            if query["query_id"] == query_id:
                query["error"] = {
                    "type": error_type,
                    "message": error_message,
                    "timestamp": time.time()
                }
                break

    def _update_performance_metrics(self):
        """Calculate overall performance metrics"""
        completed_queries = [
            q for q in self.query_history
            if q.get("completed") and "retrieval_time" in q and "generation_time" in q
        ]

        if not completed_queries:
            return

        # Calculate response times
        response_times = [
            q["retrieval_time"] + q["generation_time"]
            for q in completed_queries
        ]

        # Update metrics
        self.performance_metrics["total_queries"] = len(completed_queries)
        self.performance_metrics["avg_response_time"] = sum(response_times) / len(response_times)

        # Calculate percentiles
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        self.performance_metrics["p95_response_time"] = sorted_times[int(0.95 * n)] if n > 0 else 0
        self.performance_metrics["p99_response_time"] = sorted_times[int(0.99 * n)] if n > 0 else 0

        # Calculate cache hit rate
        total_cache_ops = 0
        cache_hits = 0
        for daily in self.daily_stats.values():
            total_cache_ops += daily["cache_hits"] + daily["cache_misses"]
            cache_hits += daily["cache_hits"]

        self.performance_metrics["cache_hit_rate"] = cache_hits / total_cache_ops if total_cache_ops > 0 else 0

        # Calculate error rate
        total_errors = sum(daily["error_count"] for daily in self.daily_stats.values())
        self.performance_metrics["error_rate"] = total_errors / self.performance_metrics["total_queries"] if self.performance_metrics["total_queries"] > 0 else 0

    def get_analytics_dashboard(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Generate date range
        date_range = []
        current = start_date
        while current <= end_date:
            date_range.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # Collect daily stats
        daily_data = []
        for date_str in date_range:
            if date_str in self.daily_stats:
                stats = self.daily_stats[date_str].copy()
                stats["date"] = date_str
                daily_data.append(stats)

        # Calculate popular queries
        all_popular = defaultdict(int)
        for daily in self.daily_stats.values():
            for query, count in daily["popular_queries"].items():
                all_popular[query] += count

        top_queries = sorted(all_popular.items(), key=lambda x: x[1], reverse=True)[:10]

        # Calculate popular sources
        top_sources = sorted(
            self.query_analytics["source_clicks"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Calculate feedback distribution
        feedback_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for score in self.query_analytics["feedback_scores"]:
            if 1 <= score <= 5:
                feedback_dist[score] += 1

        return {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days": days
            },
            "daily_stats": daily_data,
            "performance_metrics": self.performance_metrics,
            "top_queries": top_queries,
            "top_sources": top_sources,
            "feedback_distribution": feedback_dist,
            "query_analytics": {
                "avg_query_length": sum(self.query_analytics["query_lengths"]) / len(self.query_analytics["query_lengths"]) if self.query_analytics["query_lengths"] else 0,
                "avg_retrieval_count": sum(self.query_analytics["retrieval_counts"]) / len(self.query_analytics["retrieval_counts"]) if self.query_analytics["retrieval_counts"] else 0,
                "avg_relevance_score": sum(self.query_analytics["relevance_scores"]) / len(self.query_analytics["relevance_scores"]) if self.query_analytics["relevance_scores"] else 0,
                "avg_feedback_score": sum(self.query_analytics["feedback_scores"]) / len(self.query_analytics["feedback_scores"]) if self.query_analytics["feedback_scores"] else 0
            }
        }

    def export_analytics(self, format: str = "json") -> str:
        """Export analytics data"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "performance_metrics": self.performance_metrics,
            "daily_stats": dict(self.daily_stats),
            "query_analytics": self.query_analytics,
            "recent_queries": list(self.query_history)[-1000:]  # Last 1000 queries
        }

        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global analytics instance
rag_analytics = RAGAnalytics()