from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_db
from app.schemas.auth import (
    AuthResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    VerifyMagicLinkRequest,
)
from app.services.email import email_service
from app.services.magic_link import magic_link_service
from app.services.session import session_service

settings = get_settings()
router = APIRouter()


@router.post("/request-magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> MagicLinkResponse:
    """Request a magic link for passwordless authentication."""

    # Create magic link token
    token = await magic_link_service.create_magic_link(db, request.email)

    # Send email (async in background in production)
    email_sent = await email_service.send_magic_link(request.email, token)

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send magic link email. Please try again.",
        )

    return MagicLinkResponse(
        message="Magic link sent to your email address.",
        email=request.email,
    )


@router.post("/verify-magic-link", response_model=AuthResponse)
async def verify_magic_link(
    request: VerifyMagicLinkRequest,
    response: Response,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Verify magic link token and create session."""

    # Verify magic link token
    email = await magic_link_service.verify_magic_link(db, request.token)

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired magic link token.",
        )

    # Get or create user
    user = await magic_link_service.get_or_create_user(db, email)

    # Create session
    user_agent = http_request.headers.get("user-agent")
    ip_address = http_request.client.host if http_request.client else None

    signed_token, session = await session_service.create_session(
        db, user.id, user_agent, ip_address
    )

    # Set session cookie
    response.set_cookie(
        key="session",
        value=signed_token,
        max_age=settings.session_max_age,
        httponly=settings.session_httponly,
        secure=settings.session_secure,
        samesite=settings.session_samesite,
    )

    return AuthResponse(
        message="Authentication successful.",
        user_id=user.id,
        email=user.email,
    )


@router.post("/logout")
async def logout(
    response: Response,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Logout user and destroy session."""

    session_cookie = http_request.cookies.get("session")

    if session_cookie:
        await session_service.destroy_session(db, session_cookie)

    # Clear session cookie
    response.delete_cookie(
        key="session",
        httponly=settings.session_httponly,
        secure=settings.session_secure,
        samesite=settings.session_samesite,
    )

    return {"message": "Logged out successfully."}
