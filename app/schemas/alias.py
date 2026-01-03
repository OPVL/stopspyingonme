import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Reserved local-parts that cannot be used as alias names
RESERVED_NAMES = {
    "admin",
    "support",
    "postmaster",
    "abuse",
    "help",
    "security",
    "billing",
    "sales",
    "info",
    "contact",
    "hostmaster",
    "webmaster",
    "root",
    "mailer-daemon",
    "no-reply",
    "noreply",
}

# Regex for valid alias names: 3-32 chars, a-z, 0-9, hyphen,
# no start/end hyphen, no consecutive hyphens
ALIAS_NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


def validate_alias_name(name: str) -> str:
    """Validate alias name according to alias-naming-rules.md."""
    name = name.lower().strip()

    # Length check
    if len(name) < 3 or len(name) > 32:
        raise ValueError("Alias name must be between 3 and 32 characters")

    # Character and pattern check
    if not ALIAS_NAME_PATTERN.match(name):
        raise ValueError(
            "Alias name can only contain lowercase letters, numbers, and hyphens. "
            "Cannot start or end with hyphen, and cannot contain consecutive hyphens."
        )

    # Reserved names check
    if name in RESERVED_NAMES:
        raise ValueError(f"'{name}' is a reserved name and cannot be used as an alias")

    return name


class AliasCreate(BaseModel):
    """Schema for creating a new alias."""

    name: str = Field(..., min_length=3, max_length=32)
    domain: str = Field(..., min_length=1, max_length=255)
    destination_id: int = Field(..., gt=0)
    note: str | None = Field(None, max_length=1000)
    labels: list[str] | None = Field(None, max_length=10)
    expires_at: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_alias_name(v)

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        # Normalise labels to lowercase and remove duplicates
        normalised = [label.lower().strip() for label in v if label.strip()]
        return list(
            dict.fromkeys(normalised)
        )  # Remove duplicates while preserving order


class AliasUpdate(BaseModel):
    """Schema for updating an alias."""

    destination_id: int | None = Field(None, gt=0)
    note: str | None = Field(None, max_length=1000)
    labels: list[str] | None = Field(None, max_length=10)
    is_active: bool | None = None
    expires_at: datetime | None = None

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        # Normalise labels to lowercase and remove duplicates
        normalised = [label.lower().strip() for label in v if label.strip()]
        return list(
            dict.fromkeys(normalised)
        )  # Remove duplicates while preserving order


class AliasResponse(BaseModel):
    """Schema for alias responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str
    full_address: str
    destination_id: int
    note: str | None
    labels: list[str] | None
    is_active: bool
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AliasListResponse(BaseModel):
    """Schema for paginated alias list responses."""

    aliases: list[AliasResponse]
    total: int
    page: int
    per_page: int
    pages: int


class RandomAliasRequest(BaseModel):
    """Schema for random alias generation request."""

    domain: str = Field(..., min_length=1, max_length=255)
    prefix: str | None = Field(None, min_length=1, max_length=10)
    length: int = Field(default=12, ge=3, le=32)

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Validate prefix follows same rules as alias names (but shorter)
        if not re.match(r"^[a-z0-9]+$", v.lower()):
            raise ValueError("Prefix can only contain lowercase letters and numbers")
        return v.lower()


class RandomAliasResponse(BaseModel):
    """Schema for random alias generation response."""

    name: str
    domain: str
    full_address: str
