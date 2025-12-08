"""
Error handling middleware for Physical AI Textbook API
"""

import logging
import traceback
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler middleware for the API"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions"""
        start_time = time.time()

        try:
            response = await call_next(request)

            # Add processing time header
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except HTTPException as exc:
            # Handle HTTP exceptions with custom response
            return self._handle_http_exception(exc, request, start_time)

        except Exception as exc:
            # Handle unexpected errors
            return self._handle_unexpected_error(exc, request, start_time)

    def _handle_http_exception(
        self, exc: HTTPException, request: Request, start_time: float
    ) -> JSONResponse:
        """Handle known HTTP exceptions"""

        process_time = time.time() - start_time

        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail} "
            f"at {request.method} {request.url}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "type": self._get_error_type(exc.status_code),
                    "timestamp": time.time(),
                    "path": str(request.url),
                    "method": request.method,
                    "process_time": process_time
                }
            }
        )

    def _handle_unexpected_error(
        self, exc: Exception, request: Request, start_time: float
    ) -> JSONResponse:
        """Handle unexpected server errors"""

        process_time = time.time() - start_time

        # Log the full error for debugging
        logger.error(
            f"Unexpected error at {request.method} {request.url}: "
            f"{str(exc)}\n{traceback.format_exc()}"
        )

        # Return generic error to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "type": "server_error",
                    "timestamp": time.time(),
                    "path": str(request.url),
                    "method": request.method,
                    "process_time": process_time
                }
            }
        )

    def _get_error_type(self, status_code: int) -> str:
        """Categorize HTTP status codes into error types"""

        if 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown"


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """Handle validation errors from Pydantic"""

    logger.warning(f"Validation error at {request.method} {request.url}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "type": "validation_error",
                "details": exc.errors() if hasattr(exc, 'errors') else str(exc),
                "timestamp": time.time(),
                "path": str(request.url),
                "method": request.method
            }
        }
    )


async def not_found_handler(request: Request, exc) -> JSONResponse:
    """Handle 404 errors"""

    logger.info(f"404 Not Found: {request.method} {request.url}")

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested resource was not found",
                "type": "client_error",
                "timestamp": time.time(),
                "path": str(request.url),
                "method": request.method
            }
        }
    )


async def method_not_allowed_handler(request: Request, exc) -> JSONResponse:
    """Handle 405 errors"""

    logger.info(f"405 Method Not Allowed: {request.method} {request.url}")

    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": f"Method {request.method} is not allowed for this endpoint",
                "type": "client_error",
                "timestamp": time.time(),
                "path": str(request.url),
                "method": request.method
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""

    logger.info(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "type": "client_error" if 400 <= exc.status_code < 500 else "server_error",
                "timestamp": time.time(),
                "path": str(request.url),
                "method": request.method
            }
        }
    )