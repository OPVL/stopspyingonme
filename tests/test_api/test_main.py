from httpx import AsyncClient


class TestMainAPI:
    """Test main API endpoints."""

    async def test_root_endpoint(self, client: AsyncClient):
        """Test the root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Stop Spying On Me - Email Privacy Service"
        }

    async def test_health_check_endpoint(self, client: AsyncClient):
        """Test the health check endpoint."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
