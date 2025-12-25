"""Test data factories for creating realistic test data."""

from datetime import datetime, timezone
from typing import Optional

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alias import Alias
from app.models.destination import Destination
from app.models.magic_link_token import MagicLinkToken
from app.models.passkey import Passkey
from app.models.session import Session
from app.models.user import User

fake = Faker()


class UserFactory:
    """Factory for creating User instances."""

    @staticmethod
    async def create(
        db: AsyncSession,
        email: Optional[str] = None,
        **kwargs,
    ) -> User:
        """Create a user with realistic data."""
        user = User(
            email=email or fake.email(),
            **kwargs,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


class DestinationFactory:
    """Factory for creating Destination instances."""

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        email: Optional[str] = None,
        verified: bool = True,
        **kwargs,
    ) -> Destination:
        """Create a destination with realistic data."""
        destination = Destination(
            user_id=user.id,
            email=email or fake.email(),
            verified_at=datetime.now(timezone.utc) if verified else None,
            **kwargs,
        )
        db.add(destination)
        await db.commit()
        await db.refresh(destination)
        return destination


class AliasFactory:
    """Factory for creating Alias instances."""

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        destination: Destination,
        name: Optional[str] = None,
        domain: str = "example.com",
        is_active: bool = True,
        **kwargs,
    ) -> Alias:
        """Create an alias with realistic data."""
        alias = Alias(
            user_id=user.id,
            destination_id=destination.id,
            name=name or fake.user_name().lower(),
            domain=domain,
            is_active=is_active,
            **kwargs,
        )
        db.add(alias)
        await db.commit()
        await db.refresh(alias)
        return alias


class SessionFactory:
    """Factory for creating Session instances."""

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        token_hash: Optional[str] = None,
        **kwargs,
    ) -> Session:
        """Create a session with realistic data."""
        session = Session(
            user_id=user.id,
            token_hash=token_hash or fake.sha256(),
            expires_at=datetime.now(timezone.utc),
            **kwargs,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session


class MagicLinkTokenFactory:
    """Factory for creating MagicLinkToken instances."""

    @staticmethod
    async def create(
        db: AsyncSession,
        email: Optional[str] = None,
        token_hash: Optional[str] = None,
        **kwargs,
    ) -> MagicLinkToken:
        """Create a magic link token with realistic data."""
        token = MagicLinkToken(
            email=email or fake.email(),
            token_hash=token_hash or fake.sha256(),
            expires_at=datetime.now(timezone.utc),
            **kwargs,
        )
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token


class PasskeyFactory:
    """Factory for creating Passkey instances."""

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        credential_id: Optional[bytes] = None,
        public_key: Optional[bytes] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> Passkey:
        """Create a passkey with realistic data."""
        passkey = Passkey(
            user_id=user.id,
            credential_id=credential_id or fake.binary(length=32),
            public_key=public_key or fake.binary(length=64),
            name=name or f"{fake.word().title()} Key",
            sign_count=0,
            **kwargs,
        )
        db.add(passkey)
        await db.commit()
        await db.refresh(passkey)
        return passkey
