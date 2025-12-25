from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DestinationCreate(BaseModel):
    """Schema for creating a new destination."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class DestinationUpdate(BaseModel):
    """Schema for updating a destination."""

    name: str | None = Field(None, min_length=1, max_length=100)
    is_verified: bool | None = None


class DestinationResponse(BaseModel):
    """Schema for destination responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    is_verified: bool
    created_at: str
    updated_at: str


class DestinationListResponse(BaseModel):
    """Schema for paginated destination list responses."""

    destinations: list[DestinationResponse]
    total: int
    page: int
    per_page: int
    pages: int
