"""Request logging middleware for tracking HTTP requests."""

import time
import uuid
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import LogContext, get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests with timing and correlation."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with logging."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extract user info if available
        user_id = getattr(request.state, "user_id", None)

        # Start timing
        start_time = time.time()

        # Log request start
        with LogContext(request_id=request_id, user_id=user_id):
            logger.info(
                "Request started",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "client_ip": self._get_client_ip(request),
                    "user_agent": request.headers.get("user-agent"),
                },
            )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log successful response
            with LogContext(request_id=request_id, user_id=user_id):
                logger.info(
                    "Request completed",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                    },
                )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            with LogContext(request_id=request_id, user_id=user_id):
                logger.error(
                    "Request failed",
                    exc_info=True,
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": round(duration * 1000, 2),
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                    },
                )

            # Re-raise the exception
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"
