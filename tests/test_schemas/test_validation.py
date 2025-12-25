import pytest
from pydantic import ValidationError

from app.schemas.alias import AliasCreate, AliasUpdate
from app.schemas.auth import MagicLinkRequest, PasskeyRegisterRequest
from app.schemas.base import PaginationParams
from app.schemas.destination import DestinationCreate, DestinationUpdate


class TestAliasSchemas:
    """Test alias schema validation."""

    def test_alias_create_valid(self) -> None:
        """Test valid alias creation."""
        alias = AliasCreate(
            name="test-alias",
            domain="example.com",
            destination_id=1,
            description="Test alias",
        )

        assert alias.name == "test-alias"
        assert alias.domain == "example.com"
        assert alias.destination_id == 1

    def test_alias_create_name_validation_lowercase(self) -> None:
        """Test alias name is converted to lowercase."""
        alias = AliasCreate(name="TEST-ALIAS", domain="example.com", destination_id=1)

        assert alias.name == "test-alias"

    def test_alias_create_invalid_characters(self) -> None:
        """Test alias name validation rejects invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            AliasCreate(name="test@alias", domain="example.com", destination_id=1)

        assert "can only contain letters, numbers" in str(exc_info.value)

    def test_alias_create_invalid_start_end(self) -> None:
        """Test alias name validation rejects invalid start/end characters."""
        with pytest.raises(ValidationError) as exc_info:
            AliasCreate(name="-test-alias", domain="example.com", destination_id=1)

        assert "cannot start or end with" in str(exc_info.value)

    def test_alias_create_consecutive_special_chars(self) -> None:
        """Test alias name validation rejects consecutive special characters."""
        with pytest.raises(ValidationError) as exc_info:
            AliasCreate(name="test--alias", domain="example.com", destination_id=1)

        assert "consecutive special characters" in str(exc_info.value)

    def test_alias_update_partial(self) -> None:
        """Test partial alias update."""
        update = AliasUpdate(description="Updated description")

        assert update.description == "Updated description"
        assert update.destination_id is None
        assert update.is_active is None


class TestAuthSchemas:
    """Test authentication schema validation."""

    def test_magic_link_request_valid_email(self) -> None:
        """Test valid email in magic link request."""
        request = MagicLinkRequest(email="test@example.com")

        assert request.email == "test@example.com"

    def test_magic_link_request_invalid_email(self) -> None:
        """Test invalid email in magic link request."""
        with pytest.raises(ValidationError):
            MagicLinkRequest(email="invalid-email")

    def test_passkey_register_request(self) -> None:
        """Test passkey registration request validation."""
        request = PasskeyRegisterRequest(
            name="My Security Key",
            credential={"id": "test", "response": {}},
            challenge="test_challenge",
        )

        assert request.name == "My Security Key"
        assert request.credential == {"id": "test", "response": {}}
        assert request.challenge == "test_challenge"


class TestDestinationSchemas:
    """Test destination schema validation."""

    def test_destination_create_valid(self) -> None:
        """Test valid destination creation."""
        destination = DestinationCreate(email="test@example.com", name="Primary Email")

        assert destination.email == "test@example.com"
        assert destination.name == "Primary Email"

    def test_destination_create_invalid_email(self) -> None:
        """Test invalid email in destination creation."""
        with pytest.raises(ValidationError):
            DestinationCreate(email="invalid-email", name="Primary Email")

    def test_destination_update_partial(self) -> None:
        """Test partial destination update."""
        update = DestinationUpdate(name="Updated Name")

        assert update.name == "Updated Name"
        assert update.is_verified is None


class TestBaseSchemas:
    """Test base schema validation."""

    def test_pagination_params_defaults(self) -> None:
        """Test pagination parameters with defaults."""
        params = PaginationParams()

        assert params.page == 1
        assert params.per_page == 20

    def test_pagination_params_custom(self) -> None:
        """Test pagination parameters with custom values."""
        params = PaginationParams(page=2, per_page=50)

        assert params.page == 2
        assert params.per_page == 50

    def test_pagination_params_validation(self) -> None:
        """Test pagination parameter validation."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)  # Must be >= 1

        with pytest.raises(ValidationError):
            PaginationParams(per_page=101)  # Must be <= 100
