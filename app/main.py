from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.session import check_db_health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint that tests database connectivity."""
    db_healthy = await check_db_health()

    if db_healthy:
        return {"status": "healthy", "database": "connected"}
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
            },
        )


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Stop Spying On Me - Email Privacy Service"}
