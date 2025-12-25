"""Tests for API error handling."""

import pytest
from httpx import AsyncClient

from app.exceptions import NotFoundError


@pytest.mark.asyncio
async def test_404_error_format(client: AsyncClient):
    """Test 404 error returns proper RFC7807 format."""
    response = await client.get("/api/v1/nonexistent")

    assert response.status_code == 404
    data = response.json()

    # Check RFC7807 fields
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert "detail" in data
    assert "instance" in data
    assert "error_code" in data
    assert "request_id" in data

    assert data["status"] == 404
    assert data["title"] == "Not Found"
    assert data["error_code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in data["detail"].lower()
    assert "/api/v1/nonexistent" in data["instance"]


@pytest.mark.asyncio
async def test_validation_error_format(client: AsyncClient):
    """Test validation error returns proper format with field details."""
    # Send invalid data to magic link endpoint
    response = await client.post(
        "/api/v1/auth/request-magic-link",
        json={"email": "invalid-email"},
    )

    assert response.status_code == 422
    data = response.json()

    # Check RFC7807 fields
    assert data["status"] == 422
    assert data["title"] == "Validation Error"
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "errors" in data

    # Check validation errors format
    errors = data["errors"]
    assert isinstance(errors, list)
    assert len(errors) > 0

    # Each error should have field, message, and type
    for error in errors:
        assert "field" in error
        assert "message" in error
        assert "type" in error


@pytest.mark.asyncio
async def test_validation_error_missing_field(client: AsyncClient):
    """Test validation error for missing required field."""
    response = await client.post(
        "/api/v1/auth/request-magic-link",
        json={},  # Missing email field
    )

    assert response.status_code == 422
    data = response.json()

    # Should have error for missing email field
    errors = data["errors"]
    email_errors = [e for e in errors if "email" in e["field"]]
    assert len(email_errors) > 0

    email_error = email_errors[0]
    assert (
        "required" in email_error["message"].lower()
        or "missing" in email_error["message"].lower()
    )


@pytest.mark.asyncio
async def test_internal_server_error_format(client: AsyncClient):
    """Test 500 error returns proper format without exposing internals."""
    # Use pytest.raises to catch the exception and verify the handler works
    with pytest.raises(Exception):
        # Create a test endpoint that raises an exception
        from app.main import app

        @app.get("/test-error")
        async def test_error_endpoint():
            raise Exception("Test internal error")

        # This will raise an exception, but we want to test the handler
        await client.get("/test-error")

    # Instead, let's test by mocking the exception handler directly
    from unittest.mock import Mock

    from fastapi import Request

    from app.main import general_exception_handler

    # Create a mock request
    mock_request = Mock(spec=Request)
    mock_request.url = "http://test.com/test-error"
    mock_request.method = "GET"
    mock_request.state = Mock()
    mock_request.state.request_id = "test-request-id"

    # Test the exception handler directly
    test_exception = Exception("Test internal error")
    response = await general_exception_handler(mock_request, test_exception)

    assert response.status_code == 500
    data = response.body.decode()
    import json

    data = json.loads(data)

    # Check RFC7807 fields
    assert data["status"] == 500
    assert data["title"] == "Internal Server Error"
    assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    assert data["request_id"] == "test-request-id"
    assert "detail" in data


@pytest.mark.asyncio
async def test_custom_api_exception_handling(client: AsyncClient, monkeypatch):
    """Test custom APIException is properly handled."""

    async def mock_create_magic_link(db, email):
        raise NotFoundError("User not found", "USER_NOT_FOUND", {"email": email})

    # Mock the magic link service
    from app.services import magic_link

    monkeypatch.setattr(
        magic_link.magic_link_service, "create_magic_link", mock_create_magic_link
    )

    response = await client.post(
        "/api/v1/auth/request-magic-link",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 404
    data = response.json()

    # Check custom exception handling
    assert data["status"] == 404
    assert data["title"] == "User not found"
    assert data["error_code"] == "USER_NOT_FOUND"
    assert data["email"] == "test@example.com"  # From exception details


@pytest.mark.asyncio
async def test_error_logging_includes_request_id(client: AsyncClient, caplog):
    """Test that error responses include request IDs for tracking."""
    response = await client.get("/api/v1/nonexistent")

    assert response.status_code == 404
    data = response.json()

    # Should have request ID
    assert "request_id" in data
    assert data["request_id"] is not None

    # Request ID should be in logs
    request_id = data["request_id"]
    log_records = [record for record in caplog.records if hasattr(record, "request_id")]
    assert any(
        getattr(record, "request_id", None) == request_id for record in log_records
    )


@pytest.mark.asyncio
async def test_error_response_consistency(client: AsyncClient):
    """Test that all error responses follow the same format."""
    # Test different error types
    test_cases = [
        ("/api/v1/nonexistent", 404),
        (
            "/api/v1/auth/request-magic-link",
            422,
        ),  # Invalid JSON will cause validation error
    ]

    for url, expected_status in test_cases:
        if expected_status == 422:
            response = await client.post(url, json={"email": "invalid"})
        else:
            response = await client.get(url)

        assert response.status_code == expected_status
        data = response.json()

        # All errors should have these RFC7807 fields
        required_fields = [
            "type",
            "title",
            "status",
            "detail",
            "instance",
            "error_code",
        ]
        for field in required_fields:
            assert field in data, f"Missing {field} in {expected_status} error response"

        # Status should match HTTP status code
        assert data["status"] == expected_status

        # Instance should be the request URL
        assert url in data["instance"]


@pytest.mark.asyncio
async def test_error_type_urls(client: AsyncClient):
    """Test that error type URLs follow expected format."""
    response = await client.get("/api/v1/nonexistent")
    data = response.json()

    # Type URL should point to our error documentation
    assert data["type"].startswith("https://")
    assert "error" in data["type"].lower() or "rfc" in data["type"].lower()


@pytest.mark.asyncio
async def test_metrics_error_tracking(client: AsyncClient):
    """Test that errors are tracked in metrics."""
    # Cause an error
    await client.get("/api/v1/nonexistent")

    # Check metrics endpoint
    response = await client.get("/api/v1/metrics")
    content = response.text

    # Should have some requests and errors tracked
    assert "app_requests_total" in content
    assert "app_errors_total" in content

    # Extract error count - should be at least 1
    import re

    error_match = re.search(r"app_errors_total (\d+)", content)
    if error_match:
        error_count = int(error_match.group(1))
        assert error_count >= 1, f"Expected at least 1 error, got {error_count}"
