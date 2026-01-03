from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import AliasFactory, DestinationFactory


class TestAliasAPI:
    """Test alias API endpoints."""

    async def test_create_alias_success(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test successful alias creation."""
        user, headers = authenticated_user
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        response = await client.post(
            "/api/v1/aliases/",
            json={
                "name": "test-alias",
                "domain": "example.com",
                "destination_id": destination.id,
                "note": "Test note",
                "labels": ["test", "example"],
            },
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-alias"
        assert data["domain"] == "example.com"
        assert data["full_address"] == "test-alias@example.com"
        assert data["note"] == "Test note"
        assert data["labels"] == ["test", "example"]
        assert data["is_active"] is True

    async def test_create_alias_invalid_name(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test alias creation with invalid name."""
        user, headers = authenticated_user
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        # Test reserved name
        response = await client.post(
            "/api/v1/aliases/",
            json={
                "name": "admin",
                "domain": "example.com",
                "destination_id": destination.id,
            },
            headers=headers,
        )

        assert response.status_code == 400
        assert "reserved name" in response.json()["detail"]

    async def test_create_alias_duplicate(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test alias creation with duplicate name."""
        user, headers = authenticated_user
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

        # Try to create duplicate
        response = await client.post(
            "/api/v1/aliases/",
            json={
                "name": "test-alias",
                "domain": "example.com",
                "destination_id": destination.id,
            },
            headers=headers,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_list_aliases(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test listing aliases."""
        user, headers = authenticated_user
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )

        # Create test aliases
        alias1 = await AliasFactory.create_async(
            db_session,
            user_id=user.id,
            destination_id=destination.id,
            labels=["work"],
            is_active=True,
        )
        await AliasFactory.create_async(
            db_session,
            user_id=user.id,
            destination_id=destination.id,
            labels=["personal"],
            is_active=False,
        )

        # Test basic listing
        response = await client.get("/api/v1/aliases/", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["aliases"]) == 2
        assert data["page"] == 1
        assert data["per_page"] == 20

        # Test filtering by label
        response = await client.get("/api/v1/aliases/?label=work", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["aliases"][0]["id"] == alias1.id

        # Test filtering by active status
        response = await client.get(
            "/api/v1/aliases/?active_only=true", headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["aliases"][0]["id"] == alias1.id

    async def test_get_alias(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test getting a specific alias."""
        user, headers = authenticated_user
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )
        alias = await AliasFactory.create_async(
            db_session, user_id=user.id, destination_id=destination.id
        )

        response = await client.get(f"/api/v1/aliases/{alias.id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == alias.id
        assert data["name"] == alias.name
        assert data["domain"] == alias.domain

    async def test_get_alias_not_found(self, client: AsyncClient, authenticated_user):
        """Test getting non-existent alias."""
        user, headers = authenticated_user

        response = await client.get("/api/v1/aliases/999", headers=headers)
        assert response.status_code == 404

    async def test_update_alias(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test updating an alias."""
        user, headers = authenticated_user
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

        response = await client.patch(
            f"/api/v1/aliases/{alias.id}",
            json={
                "destination_id": destination2.id,
                "note": "Updated note",
                "labels": ["new", "updated"],
                "is_active": False,
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["destination_id"] == destination2.id
        assert data["note"] == "Updated note"
        assert data["labels"] == ["new", "updated"]
        assert data["is_active"] is False

    async def test_delete_alias(
        self, client: AsyncClient, db_session: AsyncSession, authenticated_user
    ):
        """Test deleting an alias."""
        user, headers = authenticated_user
        destination = await DestinationFactory.create_async(
            db_session, user_id=user.id, verified_at=datetime.utcnow()
        )
        alias = await AliasFactory.create_async(
            db_session, user_id=user.id, destination_id=destination.id
        )

        response = await client.delete(f"/api/v1/aliases/{alias.id}", headers=headers)
        assert response.status_code == 204

        # Verify it's gone
        response = await client.get(f"/api/v1/aliases/{alias.id}", headers=headers)
        assert response.status_code == 404

    async def test_generate_random_alias(self, client: AsyncClient, authenticated_user):
        """Test random alias generation."""
        user, headers = authenticated_user

        response = await client.post(
            "/api/v1/aliases/generate",
            json={"domain": "example.com"},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["domain"] == "example.com"
        assert data["full_address"] == f"{data['name']}@example.com"
        assert len(data["name"]) >= 3
        assert len(data["name"]) <= 32

    async def test_generate_random_alias_with_prefix(
        self, client: AsyncClient, authenticated_user
    ):
        """Test random alias generation with prefix."""
        user, headers = authenticated_user

        response = await client.post(
            "/api/v1/aliases/generate",
            json={
                "domain": "example.com",
                "prefix": "test",
                "length": 15,
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"].startswith("test-")
        assert len(data["name"]) <= 15

    async def test_unauthenticated_access(self, client: AsyncClient):
        """Test that unauthenticated requests are rejected."""
        response = await client.get("/api/v1/aliases/")
        assert response.status_code == 401

        response = await client.post(
            "/api/v1/aliases/",
            json={
                "name": "test",
                "domain": "example.com",
                "destination_id": 1,
            },
        )
        assert response.status_code == 401
