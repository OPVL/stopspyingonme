from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.session import session_service


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """FastAPI dependency to get current authenticated user."""
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = await session_service.get_user_from_session(db, session_cookie)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user


async def get_current_user_optional(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User | None:
    """FastAPI dependency to optionally get current authenticated user."""
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None

    return await session_service.get_user_from_session(db, session_cookie)


def require_auth(user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency that requires authentication."""
    return user


def get_client_ip(request: Request) -> str | None:
    """Get client IP address from request."""
    # Check for forwarded headers first (reverse proxy)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fallback to direct client IP
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    """Get user agent from request headers."""
    return request.headers.get("user-agent")
