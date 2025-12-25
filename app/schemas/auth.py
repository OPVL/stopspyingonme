from typing import Any

from pydantic import BaseModel, EmailStr


class MagicLinkRequest(BaseModel):
    """Request schema for magic link authentication."""

    email: EmailStr


class MagicLinkResponse(BaseModel):
    """Response schema for magic link request."""

    message: str
    email: str


class VerifyMagicLinkRequest(BaseModel):
    """Request schema for magic link verification."""

    token: str


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""

    message: str
    user_id: int
    email: str


class PasskeyRegisterRequest(BaseModel):
    """Request schema for passkey registration."""

    name: str
    credential: dict[str, Any]
    challenge: str


class PasskeyAuthenticateRequest(BaseModel):
    """Request schema for passkey authentication."""

    credential: dict[str, Any]
    challenge: str


class PasskeyResponse(BaseModel):
    """Response schema for passkey operations."""

    id: int
    name: str
    created_at: str
    last_used_at: str | None


class SessionResponse(BaseModel):
    """Response schema for session information."""

    user_id: int
    email: str
    authenticated: bool
