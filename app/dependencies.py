from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db as _get_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async for session in _get_db():
        yield session
