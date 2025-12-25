from app.schemas.alias import AliasCreate, AliasListResponse, AliasResponse, AliasUpdate
from app.schemas.auth import (
    AuthResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    PasskeyAuthenticateRequest,
    PasskeyRegisterRequest,
    PasskeyResponse,
    SessionResponse,
    VerifyMagicLinkRequest,
)
from app.schemas.base import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.schemas.destination import (
    DestinationCreate,
    DestinationListResponse,
    DestinationResponse,
    DestinationUpdate,
)

__all__ = [
    # Auth schemas
    "AuthResponse",
    "MagicLinkRequest",
    "MagicLinkResponse",
    "PasskeyAuthenticateRequest",
    "PasskeyRegisterRequest",
    "PasskeyResponse",
    "SessionResponse",
    "VerifyMagicLinkRequest",
    # Alias schemas
    "AliasCreate",
    "AliasListResponse",
    "AliasResponse",
    "AliasUpdate",
    # Destination schemas
    "DestinationCreate",
    "DestinationListResponse",
    "DestinationResponse",
    "DestinationUpdate",
    # Base schemas
    "ErrorResponse",
    "MessageResponse",
    "PaginatedResponse",
    "PaginationParams",
]
