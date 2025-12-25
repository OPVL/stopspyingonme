from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses."""

    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorResponse(BaseModel):
    """Schema for RFC7807 error responses."""

    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    error_code: str | None = None
    request_id: str | None = None
    errors: list[dict[str, str]] | None = None


class MessageResponse(BaseModel):
    """Schema for simple message responses."""

    message: str
