from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()

# Create async engine with conservative connection pooling for shared hosting
engine_kwargs = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}

# Add PostgreSQL-specific settings if using PostgreSQL & not in debug mode
if settings.database_url.startswith("postgresql") and not settings.debug:
    engine_kwargs.update(
        {
            "pool_size": settings.db_pool_size,  # type: ignore
            "max_overflow": 0,  # No overflow connections for shared hosting
            "pool_recycle": 3600,  # Recycle connections every hour
        }
    )
else:
    # Use NullPool for SQLite or debug mode
    engine_kwargs["poolclass"] = NullPool  # type: ignore

engine = create_async_engine(settings.database_url, **engine_kwargs)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_health() -> bool:
    """Check database connectivity for health checks."""
    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
