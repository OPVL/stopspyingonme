import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test environment variables before importing app modules
os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RELAY_HOST"] = "smtp.example.com"
os.environ["RELAY_USER"] = "test@example.com"
os.environ["RELAY_PASSWORD"] = "test-password"
os.environ["FROM_EMAIL"] = "test@example.com"

from app.config import get_settings
from app.db.base import Base
from app.dependencies import get_db
from app.main import app

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

        async with TestSessionLocal() as session:
            yield session

        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Create a test client with database dependency override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
