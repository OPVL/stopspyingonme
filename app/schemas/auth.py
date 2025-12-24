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
