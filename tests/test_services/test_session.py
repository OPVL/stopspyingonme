from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.session import session_service


class TestSessionService:
    """Test session management service."""

    async def test_create_session(self, db: AsyncSession):
        """Test session creation."""
        # Create a user first
        user = User(email="test@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create session
        signed_token, session = await session_service.create_session(
            db, user.id, "test-agent", "127.0.0.1"
        )

        assert signed_token is not None
        assert session.user_id == user.id
        assert session.user_agent == "test-agent"
        assert session.ip_address == "127.0.0.1"
        assert session.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)

    async def test_verify_session(self, db: AsyncSession):
        """Test session verification."""
        # Create user and session
        user = User(email="verify@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        signed_token, _ = await session_service.create_session(db, user.id)

        # Verify session
        result = await session_service.verify_session(db, signed_token)

        assert result is not None
        session, verified_user = result
        assert verified_user.id == user.id
        assert verified_user.email == user.email

    async def test_verify_invalid_session(self, db: AsyncSession):
        """Test verification with invalid token."""
        result = await session_service.verify_session(db, "invalid-token")
        assert result is None

    async def test_destroy_session(self, db: AsyncSession):
        """Test session destruction."""
        # Create user and session
        user = User(email="destroy@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        signed_token, _ = await session_service.create_session(db, user.id)

        # Destroy session
        success = await session_service.destroy_session(db, signed_token)
        assert success is True

        # Verify session is gone
        result = await session_service.verify_session(db, signed_token)
        assert result is None
