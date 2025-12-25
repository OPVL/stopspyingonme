"""Health check and monitoring endpoints."""

import time
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text

from app.config import get_settings
from app.db.session import AsyncSessionLocal
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()

# Build info - would be set by CI/CD
BUILD_INFO = {
    "version": "0.1.0",
    "commit": "dev",
    "build_time": datetime.now(timezone.utc).isoformat(),
}

# Simple metrics storage (in production, use proper metrics system)
metrics = {
    "requests_total": 0,
    "errors_total": 0,
    "start_time": time.time(),
}


async def check_database() -> tuple[bool, str, float]:
    """Check database connectivity and response time."""
    start_time = time.time()
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connectivity
            result = await session.execute(text("SELECT 1"))
            row = result.fetchone()  # Don't await this
            assert row is not None and row[0] == 1
            response_time = time.time() - start_time
            return True, "connected", response_time
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Database health check failed: {e}")
        return False, f"error: {str(e)}", response_time


async def check_migrations() -> tuple[bool, str]:
    """Check if database migrations are up to date."""
    try:
        async with AsyncSessionLocal() as session:
            # Check if alembic_version table exists and has current version
            result = await session.execute(
                text(
                    "SELECT version_num FROM alembic_version "
                    + "ORDER BY version_num DESC LIMIT 1"
                )
            )
            version = result.fetchone()  # Don't await this
            if version:
                return True, f"current: {version[0]}"
            else:
                return False, "no migrations applied"
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return False, f"error: {str(e)}"


@router.get("/health")
async def health_check() -> JSONResponse:
    """Comprehensive health check with database connectivity."""
    start_time = time.time()

    # Check database
    db_healthy, db_status, db_response_time = await check_database()

    # Overall health status
    healthy = db_healthy
    status_code = 200 if healthy else 503

    response_time = time.time() - start_time

    response_data = {
        "status": "healthy" if healthy else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "response_time_ms": round(response_time * 1000, 2),
        "checks": {
            "database": {
                "status": "pass" if db_healthy else "fail",
                "details": db_status,
                "response_time_ms": round(db_response_time * 1000, 2),
            },
        },
    }

    if healthy:
        logger.debug(
            "Health check passed", extra={"response_time_ms": response_time * 1000}
        )
    else:
        logger.error("Health check failed", extra={"checks": response_data["checks"]})

    return JSONResponse(status_code=status_code, content=response_data)


@router.get("/health/ready")
async def readiness_check() -> JSONResponse:
    """Readiness probe - checks if app is ready to serve traffic."""
    start_time = time.time()

    # Check database connectivity
    db_healthy, db_status, db_response_time = await check_database()

    # Check migrations
    migrations_ok, migration_status = await check_migrations()

    # App is ready if database is connected and migrations are applied
    ready = db_healthy and migrations_ok
    status_code = 200 if ready else 503

    response_time = time.time() - start_time

    response_data = {
        "status": "ready" if ready else "not_ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "response_time_ms": round(response_time * 1000, 2),
        "checks": {
            "database": {
                "status": "pass" if db_healthy else "fail",
                "details": db_status,
                "response_time_ms": round(db_response_time * 1000, 2),
            },
            "migrations": {
                "status": "pass" if migrations_ok else "fail",
                "details": migration_status,
            },
        },
    }

    return JSONResponse(status_code=status_code, content=response_data)


@router.get("/health/live")
async def liveness_check() -> JSONResponse:
    """Liveness probe - basic app responsiveness without external dependencies."""
    # Simple check that doesn't depend on external services
    return JSONResponse(
        status_code=200,
        content={
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.time() - metrics["start_time"], 2),
        },
    )


@router.get("/version")
async def version_info() -> JSONResponse:
    """Application version and build information."""
    return JSONResponse(
        status_code=200,
        content={
            "application": settings.app_name,
            "version": BUILD_INFO["version"],
            "commit": BUILD_INFO["commit"],
            "build_time": BUILD_INFO["build_time"],
            "environment": settings.environment,
        },
    )


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint() -> str:
    """Basic metrics in Prometheus format."""
    uptime = time.time() - metrics["start_time"]

    # In production, these would come from proper metrics collection
    prometheus_metrics = f"""# HELP app_requests_total Total number of requests
# TYPE app_requests_total counter
app_requests_total {metrics['requests_total']}

# HELP app_errors_total Total number of errors
# TYPE app_errors_total counter
app_errors_total {metrics['errors_total']}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime:.2f}

# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="{BUILD_INFO['version']}",
commit="{BUILD_INFO['commit']}",
environment="{settings.environment}"}} 1
"""

    return prometheus_metrics


def increment_request_counter() -> None:
    """Increment request counter (called by middleware)."""
    metrics["requests_total"] += 1


def increment_error_counter() -> None:
    """Increment error counter (called by exception handlers)."""
    metrics["errors_total"] += 1
