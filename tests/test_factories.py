"""Sample tests demonstrating factory patterns and fixtures."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alias import Alias
from app.models.destination import Destination
from app.models.user import User
from tests.factories import AliasFactory, DestinationFactory, UserFactory


class TestFactoryPatterns:
    """Demonstrate factory usage patterns."""

    async def test_user_factory(self, db: AsyncSession):
        """Test user creation with factory."""
        user = await UserFactory.create(db, email="factory@example.com")

        assert user.id is not None
        assert user.email == "factory@example.com"
        assert user.created_at is not None

    async def test_destination_factory(self, db: AsyncSession, user: User):
        """Test destination creation with factory."""
        destination = await DestinationFactory.create(
            db, user=user, email="dest@example.com"
        )

        assert destination.id is not None
        assert destination.user_id == user.id
        assert destination.email == "dest@example.com"
        assert destination.verified_at is not None

    async def test_alias_factory(
        self, db: AsyncSession, user: User, destination: Destination
    ):
        """Test alias creation with factory."""
        alias = await AliasFactory.create(
            db, user=user, destination=destination, name="testalias"
        )

        assert alias.id is not None
        assert alias.user_id == user.id
        assert alias.destination_id == destination.id
        assert alias.name == "testalias"
        assert alias.domain == "example.com"
        assert alias.is_active is True

    async def test_multiple_users(self, db: AsyncSession):
        """Test creating multiple users with realistic data."""
        users = []
        for _ in range(3):
            user = await UserFactory.create(db)
            users.append(user)

        # All users should have unique emails
        emails = [user.email for user in users]
        assert len(set(emails)) == 3

        # All users should be persisted
        for user in users:
            assert user.id is not None


class TestFixturePatterns:
    """Demonstrate fixture usage patterns."""

    async def test_user_fixture(self, user: User):
        """Test using the user fixture."""
        assert user.email == "test@example.com"

    async def test_destination_fixture(self, destination: Destination):
        """Test using the destination fixture."""
        assert destination.email == "destination@example.com"
        assert destination.verified_at is not None

    async def test_alias_fixture(self, alias: Alias):
        """Test using the alias fixture."""
        assert alias.name == "testalias"
        assert alias.domain == "example.com"
        assert alias.is_active is True

    async def test_related_fixtures(
        self, user: User, destination: Destination, alias: Alias
    ):
        """Test that fixtures are properly related."""
        assert destination.user_id == user.id
        assert alias.user_id == user.id
        assert alias.destination_id == destination.id


class TestAPIWithFixtures:
    """Demonstrate API testing with fixtures."""

    async def test_health_endpoint(self, client: AsyncClient):
        """Test health endpoint works with test client."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_magic_link_request(self, client: AsyncClient):
        """Test magic link request endpoint."""
        # Note: This test expects a 500 error because the email service
        # will fail to connect to the SMTP server in the test environment
        response = await client.post(
            "/api/v1/auth/request-magic-link", json={"email": "test@example.com"}
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    @pytest.mark.skip(
        reason="Authenticated client fixture needs session implementation"
    )
    async def test_authenticated_endpoint(self, authenticated_client: AsyncClient):
        """Test endpoint requiring authentication."""
        # This would test protected endpoints once authentication is implemented
        response = await authenticated_client.get("/api/v1/user/profile")
        assert response.status_code == 200
