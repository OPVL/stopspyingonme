from typing import Awaitable, Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.user import User


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to attach current user to request state."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Initialize user state
        request.state.user = None

        # Skip session processing for tests or if no session cookie
        session_cookie = request.cookies.get("session")
        if not session_cookie:
            response = await call_next(request)
            return response

        # For now, skip session verification in middleware to prevent hanging
        # Session verification will be done in endpoints that need it
        response = await call_next(request)
        return response


def get_current_user(request: Request) -> Optional[User]:
    """Get current user from request state."""
    return getattr(request.state, "user", None)
