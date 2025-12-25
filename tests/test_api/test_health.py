"""Tests for health check and monitoring endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test basic health check endpoint."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "response_time_ms" in data
    assert "checks" in data
    assert "database" in data["checks"]

    # Database check should have required fields
    db_check = data["checks"]["database"]
    assert "status" in db_check
    assert "details" in db_check
    assert "response_time_ms" in db_check


@pytest.mark.asyncio
async def test_readiness_endpoint(client: AsyncClient):
    """Test readiness probe endpoint."""
    response = await client.get("/api/v1/health/ready")

    # In test environment, migrations may not be applied, so 503 is expected
    assert response.status_code in [200, 503]
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "response_time_ms" in data
    assert "checks" in data

    # Should check both database and migrations
    assert "database" in data["checks"]
    assert "migrations" in data["checks"]

    # Each check should have status and details
    for check_name, check_data in data["checks"].items():
        assert "status" in check_data
        assert "details" in check_data


@pytest.mark.asyncio
async def test_liveness_endpoint(client: AsyncClient):
    """Test liveness probe endpoint."""
    response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "alive"
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_version_endpoint(client: AsyncClient):
    """Test version information endpoint."""
    response = await client.get("/api/v1/version")

    assert response.status_code == 200
    data = response.json()

    assert "application" in data
    assert "version" in data
    assert "commit" in data
    assert "build_time" in data
    assert "environment" in data

    assert data["application"] == "Stop Spying On Me"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """Test Prometheus metrics endpoint."""
    response = await client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    content = response.text

    # Check for expected Prometheus metrics
    assert "app_requests_total" in content
    assert "app_errors_total" in content
    assert "app_uptime_seconds" in content
    assert "app_info" in content

    # Check for metric types and help text
    assert "# HELP" in content
    assert "# TYPE" in content
    assert "counter" in content
    assert "gauge" in content


@pytest.mark.asyncio
async def test_metrics_tracking(client: AsyncClient):
    """Test that metrics are properly tracked."""
    # Make a request that causes an error
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
        assert error_count >= 1


@pytest.mark.asyncio
async def test_health_endpoint_response_format(client: AsyncClient):
    """Test that health endpoint returns proper RFC format."""
    response = await client.get("/api/v1/health")
    data = response.json()

    # Check response structure matches expected format
    assert isinstance(data["response_time_ms"], (int, float))
    assert data["response_time_ms"] > 0

    # Timestamp should be ISO format
    from datetime import datetime

    datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

    # Database check should have proper structure
    db_check = data["checks"]["database"]
    assert db_check["status"] in ["pass", "fail"]
    assert isinstance(db_check["response_time_ms"], (int, float))


@pytest.mark.asyncio
async def test_readiness_vs_health_difference(client: AsyncClient):
    """Test that readiness check includes migration check while health doesn't."""
    health_response = await client.get("/api/v1/health")
    ready_response = await client.get("/api/v1/health/ready")

    health_data = health_response.json()
    ready_data = ready_response.json()

    # Health should only check database
    assert "database" in health_data["checks"]
    assert "migrations" not in health_data["checks"]

    # Readiness should check both
    assert "database" in ready_data["checks"]
    assert "migrations" in ready_data["checks"]
