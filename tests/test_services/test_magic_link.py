from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.magic_link import magic_link_service


class TestMagicLinkService:
    """Test magic link authentication service."""

    async def test_create_magic_link(self, db: AsyncSession):
        """Test magic link creation."""
        email = "magic@example.com"

        token = await magic_link_service.create_magic_link(db, email)

        assert token is not None
        assert len(token) > 20  # Should be a substantial token

    async def test_verify_magic_link(self, db: AsyncSession):
        """Test magic link verification."""
        email = "verify@example.com"

        # Create magic link
        token = await magic_link_service.create_magic_link(db, email)

        # Verify it
        verified_email = await magic_link_service.verify_magic_link(db, token)

        assert verified_email == email

    async def test_verify_invalid_magic_link(self, db: AsyncSession):
        """Test verification with invalid token."""
        result = await magic_link_service.verify_magic_link(db, "invalid-token")
        assert result is None

    async def test_magic_link_single_use(self, db: AsyncSession):
        """Test that magic links can only be used once."""
        email = "single@example.com"

        # Create and verify magic link
        token = await magic_link_service.create_magic_link(db, email)
        first_result = await magic_link_service.verify_magic_link(db, token)

        assert first_result == email

        # Try to use it again
        second_result = await magic_link_service.verify_magic_link(db, token)
        assert second_result is None

    async def test_get_or_create_user_existing(self, db: AsyncSession):
        """Test getting existing user."""
        email = "existing@example.com"

        # Create user first
        user = User(email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Get user
        retrieved_user = await magic_link_service.get_or_create_user(db, email)

        assert retrieved_user.id == user.id
        assert retrieved_user.email == email

    async def test_get_or_create_user_new(self, db: AsyncSession):
        """Test creating new user."""
        email = "new@example.com"

        # Get/create user
        user = await magic_link_service.get_or_create_user(db, email)

        assert user.id is not None
        assert user.email == email
