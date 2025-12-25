"""Tests for custom exceptions."""

from app.exceptions import (
    AliasNotFoundError,
    APIException,
    ConflictError,
    EmailDeliveryError,
    ForbiddenError,
    InvalidTokenError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnauthorizedError,
    UserNotFoundError,
    ValidationError,
)


def test_api_exception_base():
    """Test base APIException functionality."""
    exc = APIException("Test message", 400, "TEST_ERROR", {"key": "value"})

    assert str(exc) == "Test message"
    assert exc.message == "Test message"
    assert exc.status_code == 400
    assert exc.error_code == "TEST_ERROR"
    assert exc.details == {"key": "value"}


def test_api_exception_defaults():
    """Test APIException with default values."""
    exc = APIException("Test message")

    assert exc.status_code == 500
    assert exc.error_code == "API_500"
    assert exc.details == {}


def test_not_found_error():
    """Test NotFoundError exception."""
    exc = NotFoundError()

    assert exc.status_code == 404
    assert exc.error_code == "RESOURCE_NOT_FOUND"
    assert exc.message == "Resource not found"


def test_not_found_error_custom():
    """Test NotFoundError with custom message."""
    exc = NotFoundError("Custom not found", "CUSTOM_NOT_FOUND", {"id": "123"})

    assert exc.message == "Custom not found"
    assert exc.error_code == "CUSTOM_NOT_FOUND"
    assert exc.details == {"id": "123"}


def test_unauthorized_error():
    """Test UnauthorizedError exception."""
    exc = UnauthorizedError()

    assert exc.status_code == 401
    assert exc.error_code == "UNAUTHORIZED"
    assert exc.message == "Authentication required"


def test_forbidden_error():
    """Test ForbiddenError exception."""
    exc = ForbiddenError()

    assert exc.status_code == 403
    assert exc.error_code == "FORBIDDEN"
    assert exc.message == "Access forbidden"


def test_validation_error():
    """Test ValidationError exception."""
    exc = ValidationError()

    assert exc.status_code == 422
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.message == "Validation failed"


def test_conflict_error():
    """Test ConflictError exception."""
    exc = ConflictError()

    assert exc.status_code == 409
    assert exc.error_code == "CONFLICT"
    assert exc.message == "Resource conflict"


def test_rate_limit_error():
    """Test RateLimitError exception."""
    exc = RateLimitError()

    assert exc.status_code == 429
    assert exc.error_code == "RATE_LIMIT_EXCEEDED"
    assert exc.message == "Rate limit exceeded"


def test_service_unavailable_error():
    """Test ServiceUnavailableError exception."""
    exc = ServiceUnavailableError()

    assert exc.status_code == 503
    assert exc.error_code == "SERVICE_UNAVAILABLE"
    assert exc.message == "Service temporarily unavailable"


def test_invalid_token_error():
    """Test InvalidTokenError exception."""
    exc = InvalidTokenError()

    assert exc.status_code == 401
    assert exc.error_code == "INVALID_TOKEN"
    assert exc.message == "Invalid or expired token"


def test_email_delivery_error():
    """Test EmailDeliveryError exception."""
    exc = EmailDeliveryError()

    assert exc.status_code == 500
    assert exc.error_code == "EMAIL_DELIVERY_FAILED"
    assert exc.message == "Failed to send email"


def test_alias_not_found_error():
    """Test AliasNotFoundError exception."""
    exc = AliasNotFoundError("test-alias")

    assert exc.status_code == 404
    assert exc.error_code == "ALIAS_NOT_FOUND"
    assert exc.message == "Alias 'test-alias' not found"
    assert exc.details == {"alias": "test-alias"}


def test_user_not_found_error():
    """Test UserNotFoundError exception."""
    exc = UserNotFoundError()

    assert exc.status_code == 404
    assert exc.error_code == "USER_NOT_FOUND"
    assert exc.message == "User not found"
    assert exc.details == {}


def test_user_not_found_error_with_email():
    """Test UserNotFoundError with email."""
    exc = UserNotFoundError("test@example.com")

    assert exc.message == "User with email 'test@example.com' not found"
    assert exc.details == {"email": "test@example.com"}
