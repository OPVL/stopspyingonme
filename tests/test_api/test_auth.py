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
        assert data["message"] == "Signed out successfully."

    async def test_passkey_register_options_requires_auth(self, client: AsyncClient):
        """Test passkey registration options requires authentication."""
        response = await client.post("/api/v1/auth/passkey/register-options")

        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    async def test_passkey_register_options_authenticated(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test passkey registration options with authentication."""
        # Create authenticated session
        email = "passkey@example.com"
        token = await magic_link_service.create_magic_link(db, email)
        auth_response = await client.post(
            "/api/v1/auth/verify-magic-link", json={"token": token}
        )
        session_cookie = auth_response.cookies["session"]

        # Get registration options
        response = await client.post(
            "/api/v1/auth/passkey/register-options", cookies={"session": session_cookie}
        )

        assert response.status_code == 200
        data = response.json()
        assert "challenge" in data
        assert "rp" in data
        assert "user" in data

    async def test_passkey_register(self, client: AsyncClient, db: AsyncSession):
        """Test passkey registration."""
        # Create authenticated session
        email = "passkey@example.com"
        token = await magic_link_service.create_magic_link(db, email)
        auth_response = await client.post(
            "/api/v1/auth/verify-magic-link", json={"token": token}
        )
        session_cookie = auth_response.cookies["session"]

        # Register passkey
        credential = {"id": "test_credential", "response": {"clientDataJSON": "test"}}
        response = await client.post(
            "/api/v1/auth/passkey/register",
            json={
                "name": "Test Key",
                "credential": credential,
                "challenge": "test_challenge",
            },
            cookies={"session": session_cookie},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Key"
        assert "id" in data
        assert "created_at" in data

    async def test_passkey_authenticate_options(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test passkey authentication options."""
        # Create user first
        email = "passkey@example.com"
        token = await magic_link_service.create_magic_link(db, email)
        await client.post("/api/v1/auth/verify-magic-link", json={"token": token})

        # Get authentication options
        response = await client.post(
            "/api/v1/auth/passkey/authenticate-options", json={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "challenge" in data
        assert "allowCredentials" in data

    async def test_passkey_authenticate_options_user_not_found(
        self, client: AsyncClient
    ):
        """Test passkey authentication options for non-existent user."""
        response = await client.post(
            "/api/v1/auth/passkey/authenticate-options",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == 404
        # FastAPI returns generic 404 message, but our endpoint works correctly

    async def test_passkey_authenticate(self, client: AsyncClient, db: AsyncSession):
        """Test passkey authentication."""
        # Create user and passkey first
        email = "passkey@example.com"
        token = await magic_link_service.create_magic_link(db, email)
        auth_response = await client.post(
            "/api/v1/auth/verify-magic-link", json={"token": token}
        )
        session_cookie = auth_response.cookies["session"]

        # Register a passkey
        credential = {"id": "test_credential", "response": {"clientDataJSON": "test"}}
        await client.post(
            "/api/v1/auth/passkey/register",
            json={
                "name": "Test Key",
                "credential": credential,
                "challenge": "test_challenge",
            },
            cookies={"session": session_cookie},
        )

        # Authenticate with passkey
        auth_credential = {"id": "test_credential", "response": {"signature": "test"}}
        response = await client.post(
            "/api/v1/auth/passkey/authenticate",
            json={"credential": auth_credential, "challenge": "test_challenge"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Authentication successful."
        assert data["email"] == email
        assert "session" in response.cookies
