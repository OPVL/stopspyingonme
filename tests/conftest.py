import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test environment variables before importing app modules
os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RELAY_HOST"] = "smtp.example.com"
os.environ["RELAY_USER"] = "test@example.com"
os.environ["RELAY_PASSWORD"] = "test-password"
os.environ["FROM_EMAIL"] = "test@example.com"

from app.db.base import Base
from app.dependencies import get_db
from app.main import app
from app.models.alias import Alias
from app.models.destination import Destination
from app.models.user import User
from tests.factories import AliasFactory, DestinationFactory, UserFactory
from tests.mocks.email import mock_email_service

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create engine for this test
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=None,  # Use NullPool for SQLite
    )

    # Create session factory
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        # Create tables
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        # Provide session
        async with SessionLocal() as session:
            yield session

        # Drop tables
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

    finally:
        # Always dispose engine
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database dependency override."""
    # Import here to avoid circular imports
    from app.api.v1 import auth
    from app.services import email

    async def override_get_db():
        yield db

    # Override email service with mock
    original_email_service = email.email_service
    email.email_service = mock_email_service
    auth.email_service = mock_email_service

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        email.email_service = original_email_service
        mock_email_service.clear_sent_emails()


@pytest_asyncio.fixture
async def user(db: AsyncSession) -> User:
    """Create a test user."""
    return await UserFactory.create(db, email="test@example.com")


@pytest_asyncio.fixture
async def destination(db: AsyncSession, user: User) -> Destination:
    """Create a test destination."""
    return await DestinationFactory.create(
        db, user=user, email="destination@example.com"
    )


@pytest_asyncio.fixture
async def alias(db: AsyncSession, user: User, destination: Destination) -> Alias:
    """Create a test alias."""
    return await AliasFactory.create(
        db, user=user, destination=destination, name="testalias"
    )


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient, user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated test client with session cookie."""
    # Create a magic link and verify it to establish session
    response = await client.post(
        "/api/v1/auth/request-magic-link",
        json={"email": user.email},
    )
    assert response.status_code == 200

    # Get the token from the mock email service
    from tests.mocks.email import mock_email_service

    assert len(mock_email_service.sent_emails) > 0
    token = mock_email_service.sent_emails[-1]["token"]

    # Verify the magic link to create session
    response = await client.post(
        "/api/v1/auth/verify-magic-link",
        json={"token": token},
    )
    assert response.status_code == 200

    yield client
