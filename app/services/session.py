import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.session import Session
from app.models.user import User

settings = get_settings()


class SessionService:
    """Service for managing user sessions with signed cookies."""

    def __init__(self) -> None:
        self.serializer = URLSafeTimedSerializer(settings.secret_key)
        self.max_age = settings.session_max_age

    def _hash_token(self, token: str) -> str:
        """Hash a session token for database storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_session(
        self,
        db: AsyncSession,
        user_id: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[str, Session]:
        """Create a new session and return signed token."""
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)

        # Create session record
        session = Session(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.max_age),
            user_agent=user_agent,
            ip_address=ip_address,
            last_activity=datetime.now(timezone.utc),
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        # Create signed cookie value
        signed_token = self.serializer.dumps({"token": token, "session_id": session.id})

        return signed_token, session

    async def verify_session(
        self,
        db: AsyncSession,
        signed_token: str,
    ) -> Optional[tuple[Session, User]]:
        """Verify a signed session token and return session + user."""
        try:
            # Verify signature and extract token
            data = self.serializer.loads(signed_token, max_age=self.max_age)
            token = data["token"]
            session_id = data["session_id"]
            token_hash = self._hash_token(token)

            # Query session with user
            result = await db.execute(
                select(Session, User)
                .join(User, Session.user_id == User.id)
                .where(
                    Session.id == session_id,
                    Session.token_hash == token_hash,
                    Session.expires_at > datetime.now(timezone.utc),
                )
            )

            row = result.first()
            if not row:
                return None

            session, user = row

            # Update last activity
            session.last_activity = datetime.now(timezone.utc)
            await db.commit()

            return session, user

        except (BadSignature, SignatureExpired, KeyError):
            return None

    async def destroy_session(
        self,
        db: AsyncSession,
        signed_token: str,
    ) -> bool:
        """Destroy a session."""
        try:
            data = self.serializer.loads(signed_token, max_age=self.max_age)
            session_id = data["session_id"]

            result = await db.execute(delete(Session).where(Session.id == session_id))
            await db.commit()
            return bool(result.rowcount)  # type: ignore[attr-defined]

        except (BadSignature, SignatureExpired, KeyError):
            return False

    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """Remove expired sessions from database."""
        result = await db.execute(
            delete(Session).where(Session.expires_at <= datetime.now(timezone.utc))
        )
        await db.commit()
        return result.rowcount or 0  # type: ignore[attr-defined]


# Global session service instance
session_service = SessionService()
