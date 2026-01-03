from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.alias import AliasService
from tests.factories import AliasFactory, DestinationFactory, UserFactory


class TestAliasService:
    """Test alias service functionality."""

    async def test_create_alias_success(self, db_session: AsyncSession):
        """Test successful alias creation."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        service = AliasService(db_session)
        alias = await service.create_alias(
            user_id=user.id,
            name="test-alias",
            domain="example.com",
            destination_id=destination.id,
            note="Test note",
            labels=["test", "example"],
        )

        assert alias.name == "test-alias"
        assert alias.domain == "example.com"
        assert alias.user_id == user.id
        assert alias.destination_id == destination.id
        assert alias.note == "Test note"
        assert alias.labels == ["test", "example"]
        assert alias.is_active is True

    async def test_create_alias_invalid_name(self, db_session: AsyncSession):
        """Test alias creation with invalid name."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        service = AliasService(db_session)

        # Test reserved name
        with pytest.raises(ValueError, match="reserved name"):
            await service.create_alias(
                user_id=user.id,
                name="admin",
                domain="example.com",
                destination_id=destination.id,
            )

        # Test invalid characters
        with pytest.raises(ValueError, match="can only contain"):
            await service.create_alias(
                user_id=user.id,
                name="test@alias",
                domain="example.com",
                destination_id=destination.id,
            )

        # Test too short
        with pytest.raises(ValueError, match="between 3 and 32"):
            await service.create_alias(
                user_id=user.id,
                name="ab",
                domain="example.com",
                destination_id=destination.id,
            )

    async def test_create_alias_duplicate(self, db_session: AsyncSession):
        """Test alias creation with duplicate name."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        # Create first alias
        await AliasFactory.create_async(
            db_session,
            user_id=user.id,
            name="test-alias",
            domain="example.com",
            destination_id=destination.id,
        )

        service = AliasService(db_session)

        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            await service.create_alias(
                user_id=user.id,
                name="test-alias",
                domain="example.com",
                destination_id=destination.id,
            )

    async def test_create_alias_unverified_destination(self, db_session: AsyncSession):
        """Test alias creation with unverified destination."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=None
        )

        service = AliasService(db_session)

        with pytest.raises(ValueError, match="not found or not verified"):
            await service.create_alias(
                user_id=user.id,
                name="test-alias",
                domain="example.com",
                destination_id=destination.id,
            )

    async def test_list_aliases(self, db_session: AsyncSession):
        """Test listing aliases with pagination and filtering."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        # Create test aliases
        alias1 = await AliasFactory.create_async(
            db_session,
            user_id=user.id,
            destination_id=destination.id,
            labels=["work", "important"],
            is_active=True,
        )
        await AliasFactory.create_async(
            db_session,
            user_id=user.id,
            destination_id=destination.id,
            labels=["personal"],
            is_active=False,
        )

        service = AliasService(db_session)

        # Test basic listing
        aliases, total = await service.list_aliases(user.id)
        assert total == 2
        assert len(aliases) == 2

        # Test filtering by label
        aliases, total = await service.list_aliases(user.id, label="work")
        assert total == 1
        assert aliases[0].id == alias1.id

        # Test filtering by active status
        aliases, total = await service.list_aliases(user.id, active_only=True)
        assert total == 1
        assert aliases[0].id == alias1.id

    async def test_update_alias(self, db_session: AsyncSession):
        """Test updating an alias."""
        user = await UserFactory.create_async(db_session)
        destination1 = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )
        destination2 = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        alias = await AliasFactory.create_async(
            db_session,
            user_id=user.id,
            destination_id=destination1.id,
            note="Original note",
            labels=["old"],
        )

        service = AliasService(db_session)

        # Update alias
        updated_alias = await service.update_alias(
            alias.id,
            user.id,
            destination_id=destination2.id,
            note="Updated note",
            labels=["new", "updated"],
            is_active=False,
        )

        assert updated_alias is not None
        assert updated_alias.destination_id == destination2.id
        assert updated_alias.note == "Updated note"
        assert updated_alias.labels == ["new", "updated"]
        assert updated_alias.is_active is False

    async def test_delete_alias(self, db_session: AsyncSession):
        """Test deleting an alias."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )
        alias = await AliasFactory.create_async(
            db_session, user_id=user.id, destination_id=destination.id
        )

        service = AliasService(db_session)

        # Delete alias
        success = await service.delete_alias(alias.id, user.id)
        assert success is True

        # Verify it's gone
        deleted_alias = await service.get_alias(alias.id, user.id)
        assert deleted_alias is None

    async def test_generate_random_alias(self, db_session: AsyncSession):
        """Test random alias generation."""
        service = AliasService(db_session)

        # Test basic generation
        name = await service.generate_random_alias("example.com")
        assert len(name) >= 3
        assert len(name) <= 32
        assert "-" in name  # Should be readable format

        # Test with prefix
        name = await service.generate_random_alias("example.com", prefix="test")
        assert name.startswith("test-")

        # Test with custom length
        name = await service.generate_random_alias("example.com", length=8)
        assert len(name) <= 8

    async def test_generate_random_alias_collision_handling(
        self, db_session: AsyncSession
    ):
        """Test random alias generation handles collisions."""
        user = await UserFactory.create_async(db_session)
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        service = AliasService(db_session)

        # Create many aliases to increase collision probability
        for i in range(5):
            name = await service.generate_random_alias("example.com", length=6)
            await service.create_alias(
                user_id=user.id,
                name=name,
                domain="example.com",
                destination_id=destination.id,
            )

        # Should still be able to generate new ones
        new_name = await service.generate_random_alias("example.com", length=6)
        assert new_name is not None
        assert len(new_name) <= 6
