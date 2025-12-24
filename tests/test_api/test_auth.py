import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.magic_link import magic_link_service
from tests.mocks.email import mock_email_service


@pytest.fixture(autouse=True)
def mock_email_service_fixture(monkeypatch):
    """Replace email service with mock for all tests."""
    monkeypatch.setattr("app.api.v1.auth.email_service", mock_email_service)
    mock_email_service.clear_sent_emails()


class TestAuth:
    """Test authentication endpoints."""

    async def test_request_magic_link(self, client: AsyncClient, db: AsyncSession):
        """Test magic link request endpoint."""
        response = await client.post(
            "/api/v1/auth/request-magic-link", json={"email": "test@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Magic link sent to your email address."
        assert data["email"] == "test@example.com"

        # Check mock email was sent
        assert len(mock_email_service.sent_emails) == 1
        assert mock_email_service.sent_emails[0]["to"] == "test@example.com"

    async def test_verify_magic_link_creates_user_and_session(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test magic link verification creates user and session."""
        email = "newuser@example.com"

        # Create magic link token
        token = await magic_link_service.create_magic_link(db, email)

        # Verify magic link
        response = await client.post(
            "/api/v1/auth/verify-magic-link", json={"token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Authentication successful."
        assert data["email"] == email
        assert "user_id" in data

        # Check session cookie is set
        assert "session" in response.cookies

    async def test_verify_invalid_magic_link(self, client: AsyncClient):
        """Test verification with invalid token."""
        response = await client.post(
            "/api/v1/auth/verify-magic-link", json={"token": "invalid-token"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid or expired magic link token" in data["detail"]

    async def test_logout(self, client: AsyncClient, db: AsyncSession):
        """Test logout endpoint."""
        # First create a session by verifying magic link
        email = "logout@example.com"
        token = await magic_link_service.create_magic_link(db, email)

        auth_response = await client.post(
            "/api/v1/auth/verify-magic-link", json={"token": token}
        )

        # Get session cookie
        session_cookie = auth_response.cookies["session"]

        # Logout
        response = await client.post(
            "/api/v1/auth/logout", cookies={"session": session_cookie}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully."
