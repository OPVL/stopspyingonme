from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_client_ip,
    get_current_user,
    get_current_user_optional,
    get_user_agent,
)
from app.models.user import User
from app.services.magic_link import magic_link_service
from app.services.session import session_service


class TestDependencies:
    """Test FastAPI dependencies."""

    @pytest.fixture
    async def user_with_session(self, db: AsyncSession) -> tuple[User, str]:
        """Create user with valid session."""
        # Create user
        user = await magic_link_service.get_or_create_user(db, "test@example.com")

        # Create session
        signed_token, _ = await session_service.create_session(
            db, user.id, "test-agent", "127.0.0.1"
        )

        return user, signed_token

    def test_get_client_ip_x_forwarded_for(self) -> None:
        """Test client IP extraction from X-Forwarded-For header."""
        request = MagicMock(spec=Request)
        request.headers = {"x-forwarded-for": "192.168.1.1, 10.0.0.1"}

        ip = get_client_ip(request)

        assert ip == "192.168.1.1"

    def test_get_client_ip_x_real_ip(self) -> None:
        """Test client IP extraction from X-Real-IP header."""
        request = MagicMock(spec=Request)
        request.headers = {"x-real-ip": "192.168.1.1"}

        ip = get_client_ip(request)

        assert ip == "192.168.1.1"

    def test_get_client_ip_direct(self) -> None:
        """Test client IP extraction from direct connection."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client.host = "127.0.0.1"

        ip = get_client_ip(request)

        assert ip == "127.0.0.1"

    def test_get_client_ip_no_client(self) -> None:
        """Test client IP when no client info available."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = None

        ip = get_client_ip(request)

        assert ip is None

    def test_get_user_agent(self) -> None:
        """Test user agent extraction."""
        request = MagicMock(spec=Request)
        request.headers = {"user-agent": "Mozilla/5.0 Test Browser"}

        user_agent = get_user_agent(request)

        assert user_agent == "Mozilla/5.0 Test Browser"

    def test_get_user_agent_missing(self) -> None:
        """Test user agent when header missing."""
        request = MagicMock(spec=Request)
        request.headers = {}

        user_agent = get_user_agent(request)

        assert user_agent is None

    async def test_get_current_user_valid_session(
        self, db: AsyncSession, user_with_session: tuple[User, str]
    ) -> None:
        """Test get_current_user with valid session."""
        user, signed_token = user_with_session

        request = MagicMock(spec=Request)
        request.cookies = {"session": signed_token}

        current_user = await get_current_user(request, db)

        assert current_user.id == user.id
        assert current_user.email == user.email

    async def test_get_current_user_no_session_cookie(self, db: AsyncSession) -> None:
        """Test get_current_user without session cookie."""
        request = MagicMock(spec=Request)
        request.cookies = {}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request, db)

        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail

    async def test_get_current_user_invalid_session(self, db: AsyncSession) -> None:
        """Test get_current_user with invalid session."""
        request = MagicMock(spec=Request)
        request.cookies = {"session": "invalid_token"}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request, db)

        assert exc_info.value.status_code == 401
        assert "Invalid session" in exc_info.value.detail

    async def test_get_current_user_optional_valid_session(
        self, db: AsyncSession, user_with_session: tuple[User, str]
    ) -> None:
        """Test get_current_user_optional with valid session."""
        user, signed_token = user_with_session

        request = MagicMock(spec=Request)
        request.cookies = {"session": signed_token}

        current_user = await get_current_user_optional(request, db)

        assert current_user is not None
        assert current_user.id == user.id

    async def test_get_current_user_optional_no_session(self, db: AsyncSession) -> None:
        """Test get_current_user_optional without session."""
        request = MagicMock(spec=Request)
        request.cookies = {}

        current_user = await get_current_user_optional(request, db)

        assert current_user is None

    async def test_get_current_user_optional_invalid_session(
        self, db: AsyncSession
    ) -> None:
        """Test get_current_user_optional with invalid session."""
        request = MagicMock(spec=Request)
        request.cookies = {"session": "invalid_token"}

        current_user = await get_current_user_optional(request, db)

        assert current_user is None
