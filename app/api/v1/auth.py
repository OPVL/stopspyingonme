from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_client_ip, get_current_user, get_db, get_user_agent
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    PasskeyAuthenticateRequest,
    PasskeyRegisterRequest,
    PasskeyResponse,
    VerifyMagicLinkRequest,
)
from app.services.email import email_service
from app.services.magic_link import magic_link_service
from app.services.session import session_service
from app.services.webauthn import webauthn_service

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
    user_agent = get_user_agent(http_request)
    ip_address = get_client_ip(http_request)

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

    return {"message": "Signed out successfully."}


@router.post("/passkey/register-options")
async def passkey_register_options(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Generate WebAuthn registration options."""
    return await webauthn_service.generate_registration_options(
        current_user.id, current_user.email
    )


@router.post("/passkey/register", response_model=PasskeyResponse)
async def passkey_register(
    request: PasskeyRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PasskeyResponse:
    """Register a new passkey."""
    try:
        passkey = await webauthn_service.verify_registration(
            db, current_user.id, request.credential, request.challenge, request.name
        )
        return PasskeyResponse(
            id=passkey.id,
            name=passkey.name,
            created_at=passkey.created_at.isoformat(),
            last_used_at=(
                passkey.last_used_at.isoformat() if passkey.last_used_at else None
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/passkey/authenticate-options")
async def passkey_authenticate_options(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Generate WebAuthn authentication options."""
    # Get user by email
    user = await magic_link_service.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await webauthn_service.generate_authentication_options(db, user.id)


@router.post("/passkey/authenticate", response_model=AuthResponse)
async def passkey_authenticate(
    request: PasskeyAuthenticateRequest,
    response: Response,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Authenticate with passkey."""
    try:
        user = await webauthn_service.verify_authentication(
            db, request.credential, request.challenge
        )

        if not user:
            raise HTTPException(status_code=401, detail="Authentication failed")

        # Create session
        user_agent = get_user_agent(http_request)
        ip_address = get_client_ip(http_request)

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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
