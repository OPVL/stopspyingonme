from typing import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1.router import api_router
from app.config import get_settings
from app.db.session import check_db_health
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.session import SessionMiddleware
from app.utils.logging import get_logger, setup_logging

# Setup logging before creating app
setup_logging()
logger = get_logger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

# Templates
templates = Jinja2Templates(directory="app/templates")


# Request ID Middleware (kept for backward compatibility)
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # RequestLoggingMiddleware now handles request IDs
        response = await call_next(request)
        return response


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware (includes request ID generation)
app.add_middleware(RequestLoggingMiddleware)

# Session Middleware
app.add_middleware(SessionMiddleware)


# Exception Handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "Resource not found",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
    return JSONResponse(
        status_code=404,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.4",
            "title": "Not Found",
            "status": 404,
            "detail": "The requested resource was not found.",
            "instance": str(request.url),
        },
    )


@app.exception_handler(422)
async def validation_error_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    logger.warning(
        "Validation error",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": getattr(request.state, "request_id", None),
            "errors": getattr(exc, "detail", None),
        },
    )
    return JSONResponse(
        status_code=422,
        content={
            "type": "https://tools.ietf.org/html/rfc4918#section-11.2",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": str(request.url),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Internal server error",
        exc_info=True,
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": getattr(request.state, "request_id", None),
            "exception_type": type(exc).__name__,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.6.1",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An internal server error occurred.",
            "instance": str(request.url),
        },
    )


# API Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint that tests database connectivity."""
    db_healthy = await check_db_health()

    if db_healthy:
        logger.debug("Health check passed")
        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "database": "connected"},
        )
    else:
        logger.error("Health check failed - database disconnected")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
            },
        )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {"message": "Stop Spying On Me - Email Privacy Service"}
