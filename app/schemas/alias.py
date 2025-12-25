from pydantic import BaseModel, ConfigDict, Field, field_validator


class AliasCreate(BaseModel):
    """Schema for creating a new alias."""

    name: str = Field(..., min_length=1, max_length=64)
    domain: str = Field(..., min_length=1, max_length=255)
    destination_id: int = Field(..., gt=0)
    description: str | None = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_alias_name(cls, v: str) -> str:
        """Validate alias name according to alias-naming-rules.md."""
        if not v.replace("-", "").replace("_", "").replace(".", "").isalnum():
            raise ValueError(
                "Alias name can only contain letters, numbers, hyphens, "
                "underscores, and dots"
            )
        if v.startswith(("-", "_", ".")) or v.endswith(("-", "_", ".")):
            raise ValueError(
                "Alias name cannot start or end with hyphens, underscores, or dots"
            )
        if ".." in v or "--" in v or "__" in v:
            raise ValueError("Alias name cannot contain consecutive special characters")
        return v.lower()


class AliasUpdate(BaseModel):
    """Schema for updating an alias."""

    destination_id: int | None = Field(None, gt=0)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class AliasResponse(BaseModel):
    """Schema for alias responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str
    full_address: str
    destination_id: int
    description: str | None
    is_active: bool
    created_at: str
    updated_at: str


class AliasListResponse(BaseModel):
    """Schema for paginated alias list responses."""

    aliases: list[AliasResponse]
    total: int
    page: int
    per_page: int
    pages: int
