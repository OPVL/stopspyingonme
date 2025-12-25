"""Custom exceptions for the Stop Spying On Me API."""

from typing import Any


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"API_{status_code}"
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(APIException):
    """Exception for 404 Not Found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "RESOURCE_NOT_FOUND",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 404, error_code, details)


class UnauthorizedError(APIException):
    """Exception for 401 Unauthorized errors."""

    def __init__(
        self,
        message: str = "Authentication required",
        error_code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 401, error_code, details)


class ForbiddenError(APIException):
    """Exception for 403 Forbidden errors."""

    def __init__(
        self,
        message: str = "Access forbidden",
        error_code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 403, error_code, details)


class ValidationError(APIException):
    """Exception for 422 Validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 422, error_code, details)


class ConflictError(APIException):
    """Exception for 409 Conflict errors."""

    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 409, error_code, details)


class RateLimitError(APIException):
    """Exception for 429 Rate Limit errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 429, error_code, details)


class ServiceUnavailableError(APIException):
    """Exception for 503 Service Unavailable errors."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        error_code: str = "SERVICE_UNAVAILABLE",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 503, error_code, details)


# Specific domain exceptions
class InvalidTokenError(UnauthorizedError):
    """Exception for invalid authentication tokens."""

    def __init__(
        self,
        message: str = "Invalid or expired token",
        error_code: str = "INVALID_TOKEN",
    ) -> None:
        super().__init__(message, error_code)


class EmailDeliveryError(APIException):
    """Exception for email delivery failures."""

    def __init__(
        self,
        message: str = "Failed to send email",
        error_code: str = "EMAIL_DELIVERY_FAILED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, 500, error_code, details)


class AliasNotFoundError(NotFoundError):
    """Exception for alias not found errors."""

    def __init__(
        self,
        alias_name: str,
        error_code: str = "ALIAS_NOT_FOUND",
    ) -> None:
        super().__init__(
            f"Alias '{alias_name}' not found",
            error_code,
            {"alias": alias_name},
        )


class UserNotFoundError(NotFoundError):
    """Exception for user not found errors."""

    def __init__(
        self,
        email: str | None = None,
        error_code: str = "USER_NOT_FOUND",
    ) -> None:
        message = f"User with email '{email}' not found" if email else "User not found"
        details = {"email": email} if email else {}
        super().__init__(message, error_code, details)
