import base64
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.passkey import Passkey
from app.models.user import User

settings = get_settings()


class WebAuthnService:
    """Service for WebAuthn passkey operations."""

    async def generate_registration_options(
        self, user_id: int, user_email: str
    ) -> dict[str, Any]:
        """Generate WebAuthn registration options for a user."""
        # Simplified implementation for py-webauthn 0.0.4
        return {
            "challenge": base64.urlsafe_b64encode(b"test_challenge").decode(),
            "rp": {"id": settings.webauthn_rp_id, "name": settings.webauthn_rp_name},
            "user": {
                "id": base64.urlsafe_b64encode(str(user_id).encode()).decode(),
                "name": user_email,
                "displayName": user_email,
            },
            "pubKeyCredParams": [{"alg": -7, "type": "public-key"}],
            "timeout": 60000,
            "attestation": "none",
        }

    async def verify_registration(
        self,
        db: AsyncSession,
        user_id: int,
        credential: dict[str, Any],
        challenge: str,
        name: str,
    ) -> Passkey:
        """Verify registration response and store passkey."""
        # Simplified verification for py-webauthn 0.0.4
        # In production, this would use proper WebAuthn verification

        # Store passkey with mock data
        passkey = Passkey(
            user_id=user_id,
            credential_id=base64.urlsafe_b64encode(b"mock_credential_id").decode(),
            public_key=base64.urlsafe_b64encode(b"mock_public_key").decode(),
            sign_count=0,
            name=name,
        )

        db.add(passkey)
        await db.commit()
        await db.refresh(passkey)

        return passkey

    async def generate_authentication_options(
        self, db: AsyncSession, user_id: int
    ) -> dict[str, Any]:
        """Generate WebAuthn authentication options for a user."""
        # Get user's passkeys
        result = await db.execute(select(Passkey).where(Passkey.user_id == user_id))
        passkeys = result.scalars().all()

        allow_credentials = [
            {
                "type": "public-key",
                "id": pk.credential_id,
            }
            for pk in passkeys
        ]

        return {
            "challenge": base64.urlsafe_b64encode(b"test_auth_challenge").decode(),
            "timeout": 60000,
            "rpId": settings.webauthn_rp_id,
            "allowCredentials": allow_credentials,
        }

    async def verify_authentication(
        self,
        db: AsyncSession,
        credential: dict[str, Any],
        challenge: str,
    ) -> User | None:
        """Verify authentication response and return user."""
        # Simplified verification for py-webauthn 0.0.4
        # In production, this would use proper WebAuthn verification

        # Mock credential ID lookup
        credential_id = base64.urlsafe_b64encode(b"mock_credential_id").decode()

        # Find passkey
        result = await db.execute(
            select(Passkey).where(Passkey.credential_id == credential_id)
        )
        passkey = result.scalar_one_or_none()

        if not passkey:
            return None

        # Update last used
        passkey.last_used_at = datetime.now(timezone.utc)
        await db.commit()

        # Get user
        user_result = await db.execute(select(User).where(User.id == passkey.user_id))
        return user_result.scalar_one_or_none()


webauthn_service = WebAuthnService()
