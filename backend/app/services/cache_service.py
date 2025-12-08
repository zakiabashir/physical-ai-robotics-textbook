"""
Caching service for RAG queries to improve performance
"""

import hashlib
import json
import logging
import time
from typing import Optional, Dict, Any, List
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """Simple in-memory caching service for RAG queries"""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = 1000  # Maximum number of cached items

    def _generate_key(self, query: str, params: Dict[str, Any] = None) -> str:
        """Generate a cache key from query and parameters"""
        key_data = {
            "query": query.lower().strip(),
            "params": params or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, query: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Get cached result"""
        key = self._generate_key(query, params)

        if key in self.cache:
            cached_item = self.cache[key]

            # Check if expired
            if time.time() - cached_item["timestamp"] > cached_item["ttl"]:
                del self.cache[key]
                logger.debug(f"Cache expired for query: {query[:50]}...")
                return None

            logger.debug(f"Cache hit for query: {query[:50]}...")
            return cached_item["data"]

        return None

    def set(self, query: str, data: Any, params: Dict[str, Any] = None, ttl: Optional[int] = None) -> None:
        """Cache a result"""
        key = self._generate_key(query, params)

        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
            logger.debug("Evicted oldest cache item")

        self.cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl or self.default_ttl
        }
        logger.debug(f"Cached result for query: {query[:50]}...")

    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "memory_usage": sum(len(str(v)) for v in self.cache.values())
        }


# Global cache instance
cache_service = CacheService()


def cached_result(ttl: int = 300, cache_params: List[str] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract cache key parameters
            params = {}
            if cache_params:
                for param in cache_params:
                    if param in kwargs:
                        params[param] = kwargs[param]

            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}_{str(args)}_{str(sorted(params.items()))}"

            # Try to get from cache
            cached = cache_service.get(cache_key, params)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache the result
            cache_service.set(cache_key, result, params, ttl)

            return result
        return wrapper
    return decorator