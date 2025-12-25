import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.passkey import Passkey
from app.models.user import User
from app.services.webauthn import webauthn_service


class TestWebAuthnService:
    """Test WebAuthn service functionality."""

    @pytest.fixture
    async def user(self, db: AsyncSession) -> User:
        """Create test user."""
        user = User(email="test@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def test_generate_registration_options(self, user: User) -> None:
        """Test WebAuthn registration options generation."""
        options = await webauthn_service.generate_registration_options(
            user.id, user.email
        )

        assert "challenge" in options
        assert "rp" in options
        assert "user" in options
        assert "pubKeyCredParams" in options
        assert options["rp"]["id"] == "localhost"
        assert options["user"]["name"] == user.email

    async def test_verify_registration_success(
        self, db: AsyncSession, user: User
    ) -> None:
        """Test successful passkey registration."""
        credential = {"id": "test_credential", "response": {"clientDataJSON": "test"}}

        passkey = await webauthn_service.verify_registration(
            db, user.id, credential, "test_challenge", "Test Key"
        )

        assert passkey.user_id == user.id
        assert passkey.name == "Test Key"
        assert passkey.credential_id is not None
        assert passkey.public_key is not None
        assert passkey.sign_count == 0

    async def test_generate_authentication_options_no_passkeys(
        self, db: AsyncSession, user: User
    ) -> None:
        """Test authentication options with no existing passkeys."""
        options = await webauthn_service.generate_authentication_options(db, user.id)

        assert "challenge" in options
        assert "allowCredentials" in options
        assert options["allowCredentials"] == []

    async def test_generate_authentication_options_with_passkeys(
        self, db: AsyncSession, user: User
    ) -> None:
        """Test authentication options with existing passkeys."""
        # Create a passkey first
        passkey = Passkey(
            user_id=user.id,
            credential_id="test_cred_id",
            public_key="test_public_key",
            sign_count=0,
            name="Test Key",
        )
        db.add(passkey)
        await db.commit()

        options = await webauthn_service.generate_authentication_options(db, user.id)

        assert "allowCredentials" in options
        assert len(options["allowCredentials"]) == 1
        assert options["allowCredentials"][0]["id"] == "test_cred_id"

    async def test_verify_authentication_success(
        self, db: AsyncSession, user: User
    ) -> None:
        """Test successful passkey authentication."""
        # Create a passkey first
        passkey = Passkey(
            user_id=user.id,
            credential_id="bW9ja19jcmVkZW50aWFsX2lk",  # b64 encoded mock_credential_id
            public_key="test_public_key",
            sign_count=0,
            name="Test Key",
        )
        db.add(passkey)
        await db.commit()

        credential = {"id": "test_credential", "response": {"signature": "test"}}

        authenticated_user = await webauthn_service.verify_authentication(
            db, credential, "test_challenge"
        )

        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == user.email

    async def test_verify_authentication_invalid_credential(
        self, db: AsyncSession, user: User
    ) -> None:
        """Test authentication with invalid credential."""
        credential = {"id": "invalid_credential", "response": {"signature": "test"}}

        authenticated_user = await webauthn_service.verify_authentication(
            db, credential, "test_challenge"
        )

        assert authenticated_user is None

    async def test_passkey_last_used_updated(
        self, db: AsyncSession, user: User
    ) -> None:
        """Test that last_used_at is updated on authentication."""
        # Create a passkey first
        passkey = Passkey(
            user_id=user.id,
            credential_id="bW9ja19jcmVkZW50aWFsX2lk",
            public_key="test_public_key",
            sign_count=0,
            name="Test Key",
        )
        db.add(passkey)
        await db.commit()

        assert passkey.last_used_at is None

        credential = {"id": "test_credential", "response": {"signature": "test"}}
        await webauthn_service.verify_authentication(db, credential, "test_challenge")

        await db.refresh(passkey)
        assert passkey.last_used_at is not None
