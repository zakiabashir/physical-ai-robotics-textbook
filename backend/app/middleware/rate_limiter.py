"""
Rate limiting middleware for API endpoints
"""

import time
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        # Store requests per IP: {ip: deque([timestamp1, timestamp2, ...])}
        self.requests: Dict[str, deque] = defaultdict(deque)
        # Default limits (requests per minute)
        self.default_limits = {
            "/chat": 30,  # 30 chat requests per minute
            "/ingestion": 10,  # 10 ingestion requests per minute
            "/analytics": 60,  # 60 analytics requests per minute
            "/health": 100,  # 100 health requests per minute
        }
        # Window size in seconds
        self.window_size = 60

    def is_allowed(self, key: str, path: str, limit: Optional[int] = None) -> bool:
        """
        Check if a request is allowed based on rate limit

        Args:
            key: Identifier (usually IP address)
            path: API path
            limit: Custom limit (overrides default)

        Returns:
            True if allowed, False otherwise
        """
        # Get appropriate limit
        if limit is None:
            limit = self.default_limits.get(path, 30)  # Default to 30 if path not found

        current_time = time.time()
        window_start = current_time - self.window_size

        # Clean old requests
        request_queue = self.requests[key]
        while request_queue and request_queue[0] < window_start:
            request_queue.popleft()

        # Check if under limit
        if len(request_queue) < limit:
            request_queue.append(current_time)
            return True

        return False

    def get_remaining(self, key: str, path: str, limit: Optional[int] = None) -> int:
        """
        Get number of requests remaining for this window

        Args:
            key: Identifier
            path: API path
            limit: Custom limit

        Returns:
            Number of requests remaining
        """
        if limit is None:
            limit = self.default_limits.get(path, 30)

        current_time = time.time()
        window_start = current_time - self.window_size

        # Count recent requests
        recent_count = sum(
            1 for req_time in self.requests[key]
            if req_time >= window_start
        )

        return max(0, limit - recent_count)

    def get_reset_time(self, key: str) -> float:
        """
        Get time until rate limit resets

        Args:
            key: Identifier

        Returns:
            Seconds until reset
        """
        if not self.requests[key]:
            return 0

        oldest_request = min(self.requests[key])
        return max(0, self.window_size - (time.time() - oldest_request))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""

    def __init__(self, app, limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.limiter = limiter or RateLimiter()

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client IP (considering proxies)
        client_ip = self._get_client_ip(request)

        # Get the API path
        path = request.url.path
        method = request.method

        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(path, method):
            return await call_next(request)

        # Check rate limit
        if not self.limiter.is_allowed(client_ip, path):
            # Get rate limit headers
            remaining = self.limiter.get_remaining(client_ip, path)
            reset_time = self.limiter.get_reset_time(client_ip)

            # Log rate limit violation
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {path}")

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(self.limiter.default_limits.get(path, 30)),
                    "X-RateLimit-Remaining": str(max(0, remaining - 1)),
                    "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                    "Retry-After": str(int(reset_time))
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        remaining = self.limiter.get_remaining(client_ip, path)
        reset_time = self.limiter.get_reset_time(client_ip)

        response.headers["X-RateLimit-Limit"] = str(self.limiter.default_limits.get(path, 30))
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_time))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering proxies"""
        # Check for forwarded IP headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the list
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to client host
        return request.client.host

    def _should_skip_rate_limit(self, path: str, method: str) -> bool:
        """Determine if path should skip rate limiting"""
        # Skip rate limiting for
        skip_patterns = [
            "/docs",  # API documentation
            "/openapi.json",  # OpenAPI spec
            "/redoc",  # ReDoc documentation
            "/favicon",  # Favicon
            "/static",  # Static files
        ]

        # Skip GET requests to health endpoints (they're lightweight)
        if method == "GET" and "/health" in path:
            return True

        # Skip based on patterns
        return any(pattern in path for pattern in skip_patterns)


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limiting decorator for endpoints
def rate_limit(limit: Optional[int] = None, per: str = "minute"):
    """
    Decorator for rate limiting specific endpoints

    Args:
        limit: Number of requests allowed
        per: Time period ("minute", "hour", "day")
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This is a simplified version - in production, you'd want more sophisticated rate limiting
            return await func(*args, **kwargs)
        return wrapper
    return decorator