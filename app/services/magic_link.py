import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.magic_link_token import MagicLinkToken
from app.models.user import User

settings = get_settings()


class MagicLinkService:
    """Service for managing magic link authentication."""

    def _hash_token(self, token: str) -> str:
        """Hash a magic link token for database storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_magic_link(
        self,
        db: AsyncSession,
        email: str,
    ) -> str:
        """Create a magic link token for email authentication."""
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)

        # Clean up any existing tokens for this email
        await db.execute(delete(MagicLinkToken).where(MagicLinkToken.email == email))

        # Create new token
        magic_token = MagicLinkToken(
            email=email,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=settings.magic_link_ttl),
        )

        db.add(magic_token)
        await db.commit()

        return token

    async def verify_magic_link(
        self,
        db: AsyncSession,
        token: str,
    ) -> Optional[str]:
        """Verify a magic link token and return the email if valid."""
        token_hash = self._hash_token(token)

        # Find valid token
        result = await db.execute(
            select(MagicLinkToken).where(
                MagicLinkToken.token_hash == token_hash,
                MagicLinkToken.expires_at > datetime.now(timezone.utc),
                MagicLinkToken.used_at.is_(None),
            )
        )

        magic_token = result.scalar_one_or_none()
        if not magic_token:
            return None

        # Mark token as used
        magic_token.used_at = datetime.now(timezone.utc)
        await db.commit()

        return magic_token.email

    async def get_or_create_user(
        self,
        db: AsyncSession,
        email: str,
    ) -> User:
        """Get existing user or create new one for email."""
        # Try to find existing user
        result = await db.execute(select(User).where(User.email == email))

        user = result.scalar_one_or_none()
        if user:
            return user

        # Create new user
        user = User(email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def cleanup_expired_tokens(self, db: AsyncSession) -> int:
        """Remove expired magic link tokens."""
        result = await db.execute(
            delete(MagicLinkToken).where(
                MagicLinkToken.expires_at <= datetime.now(timezone.utc)
            )
        )
        await db.commit()
        return result.rowcount or 0  # type: ignore[attr-defined]


# Global magic link service instance
magic_link_service = MagicLinkService()
