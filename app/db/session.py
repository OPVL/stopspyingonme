from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()

# Create async engine with proper configuration
if settings.database_url.startswith("sqlite"):
    # SQLite configuration
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        poolclass=NullPool,
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.db_pool_size,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def check_db_health() -> bool:
    """Check if database is accessible."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
