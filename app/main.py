import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1.health import increment_error_counter, increment_request_counter
from app.api.v1.router import api_router
from app.config import get_settings
from app.exceptions import APIException
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


# Metrics Middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Increment request counter
        increment_request_counter()

        response = await call_next(request)

        # Increment error counter for 4xx/5xx responses
        if response.status_code >= 400:
            increment_error_counter()

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

# Metrics Middleware
app.add_middleware(MetricsMiddleware)

# Session Middleware
app.add_middleware(SessionMiddleware)


# Exception Handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    request_id = getattr(request.state, "request_id", None)
    increment_error_counter()

    logger.warning(
        f"API exception: {exc.error_code}",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://quitspyingon.me/errors/{exc.error_code.lower()}",
            "title": exc.message,
            "status": exc.status_code,
            "detail": exc.message,
            "instance": str(request.url),
            "error_code": exc.error_code,
            "request_id": request_id,
            **(exc.details if exc.details else {}),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = getattr(request.state, "request_id", None)
    increment_error_counter()

    # Format validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(
            {
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "Request validation failed",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id,
            "validation_errors": errors,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "type": "https://tools.ietf.org/html/rfc4918#section-11.2",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed",
            "instance": str(request.url),
            "error_code": "VALIDATION_ERROR",
            "request_id": request_id,
            "errors": errors,
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle 404 Not Found errors."""
    request_id = getattr(request.state, "request_id", None)
    increment_error_counter()

    logger.warning(
        "Resource not found",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=404,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.4",
            "title": "Not Found",
            "status": 404,
            "detail": "The requested resource was not found",
            "instance": str(request.url),
            "error_code": "RESOURCE_NOT_FOUND",
            "request_id": request_id,
        },
    )


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle 401 Unauthorized errors."""
    request_id = getattr(request.state, "request_id", None)
    increment_error_counter()

    logger.warning(
        "Unauthorized access attempt",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=401,
        content={
            "type": "https://tools.ietf.org/html/rfc7235#section-3.1",
            "title": "Unauthorized",
            "status": 401,
            "detail": "Authentication required",
            "instance": str(request.url),
            "error_code": "UNAUTHORIZED",
            "request_id": request_id,
        },
    )


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle 403 Forbidden errors."""
    request_id = getattr(request.state, "request_id", None)
    increment_error_counter()

    logger.warning(
        "Forbidden access attempt",
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=403,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.3",
            "title": "Forbidden",
            "status": 403,
            "detail": "Access to this resource is forbidden",
            "instance": str(request.url),
            "error_code": "FORBIDDEN",
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())
    increment_error_counter()

    logger.error(
        "Internal server error",
        exc_info=True,
        extra={
            "path": str(request.url),
            "method": request.method,
            "request_id": request_id,
            "exception_type": type(exc).__name__,
        },
    )

    # In production, don't expose internal error details
    detail = (
        "An internal server error occurred. Please contact support with request ID."
        if not settings.debug
        else f"Internal error: {str(exc)}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "type": "https://tools.ietf.org/html/rfc7231#section-6.6.1",
            "title": "Internal Server Error",
            "status": 500,
            "detail": detail,
            "instance": str(request.url),
            "error_code": "INTERNAL_SERVER_ERROR",
            "request_id": request_id,
        },
    )


# API Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {"message": "Stop Spying On Me - Email Privacy Service"}
