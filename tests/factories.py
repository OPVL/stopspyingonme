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
    async def create_async(
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

    @staticmethod
    async def create(
        db: AsyncSession,
        user: Optional[User] = None,
        email: Optional[str] = None,
        **kwargs,
    ) -> User:
        """Create a user with realistic data (backward compatibility)."""
        return await UserFactory.create_async(db, email=email, **kwargs)


class DestinationFactory:
    """Factory for creating Destination instances."""

    @staticmethod
    async def create_async(
        db: AsyncSession,
        user_id: Optional[int] = None,
        user: Optional[User] = None,
        email: Optional[str] = None,
        verified_at: Optional[datetime] = None,
        verified: bool = True,
        **kwargs,
    ) -> Destination:
        """Create a destination with realistic data."""
        if user_id is None and user is not None:
            user_id = user.id
        elif user_id is None:
            # Create a user if none provided
            user = await UserFactory.create_async(db)
            user_id = user.id

        destination = Destination(
            user_id=user_id,
            email=email or fake.email(),
            verified_at=(
                verified_at
                if verified_at is not None
                else (datetime.now(timezone.utc) if verified else None)
            ),
            **kwargs,
        )
        db.add(destination)
        await db.commit()
        await db.refresh(destination)
        return destination

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        email: Optional[str] = None,
        verified: bool = True,
        **kwargs,
    ) -> Destination:
        """Create a destination with realistic data (backward compatibility)."""
        return await DestinationFactory.create_async(
            db, user_id=user.id, email=email, verified=verified, **kwargs
        )


class AliasFactory:
    """Factory for creating Alias instances."""

    @staticmethod
    async def create_async(
        db: AsyncSession,
        user_id: Optional[int] = None,
        user: Optional[User] = None,
        destination_id: Optional[int] = None,
        destination: Optional[Destination] = None,
        name: Optional[str] = None,
        domain: str = "example.com",
        is_active: bool = True,
        note: Optional[str] = None,
        labels: Optional[list[str]] = None,
        expires_at: Optional[datetime] = None,
        **kwargs,
    ) -> Alias:
        """Create an alias with realistic data."""
        if user_id is None and user is not None:
            user_id = user.id
        elif user_id is None:
            # Create a user if none provided
            user = await UserFactory.create_async(db)
            user_id = user.id

        if destination_id is None and destination is not None:
            destination_id = destination.id
        elif destination_id is None:
            # Create a destination if none provided
            destination = await DestinationFactory.create_async(
                db, user_id=user_id, verified=True
            )
            destination_id = destination.id

        # Generate a valid alias name
        if name is None:
            name = fake.user_name().lower().replace("_", "-").replace(".", "-")
            # Ensure it's valid length and format
            if len(name) < 3:
                name = f"alias-{fake.random_int(10, 99)}"
            elif len(name) > 32:
                name = name[:29] + f"-{fake.random_int(10, 99)}"
            # Remove any invalid characters
            name = "".join(c for c in name if c.isalnum() or c == "-")
            # Ensure no consecutive hyphens
            while "--" in name:
                name = name.replace("--", "-")
            # Ensure doesn't start/end with hyphen
            name = name.strip("-")
            if len(name) < 3:
                name = f"test-alias-{fake.random_int(100, 999)}"

        alias = Alias(
            user_id=user_id,
            destination_id=destination_id,
            name=name,
            domain=domain,
            is_active=is_active,
            note=note,
            labels=labels or [],
            expires_at=expires_at,
            **kwargs,
        )
        db.add(alias)
        await db.commit()
        await db.refresh(alias)
        return alias

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
        """Create an alias with realistic data (backward compatibility)."""
        return await AliasFactory.create_async(
            db,
            user_id=user.id,
            destination_id=destination.id,
            name=name,
            domain=domain,
            is_active=is_active,
            **kwargs,
        )


class SessionFactory:
    """Factory for creating Session instances."""

    @staticmethod
    async def create_async(
        db: AsyncSession,
        user_id: Optional[int] = None,
        user: Optional[User] = None,
        token_hash: Optional[str] = None,
        **kwargs,
    ) -> Session:
        """Create a session with realistic data."""
        if user_id is None and user is not None:
            user_id = user.id
        elif user_id is None:
            user = await UserFactory.create_async(db)
            user_id = user.id

        session = Session(
            user_id=user_id,
            token_hash=token_hash or fake.sha256(),
            expires_at=datetime.now(timezone.utc),
            **kwargs,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        token_hash: Optional[str] = None,
        **kwargs,
    ) -> Session:
        """Create a session with realistic data (backward compatibility)."""
        return await SessionFactory.create_async(
            db, user_id=user.id, token_hash=token_hash, **kwargs
        )


class MagicLinkTokenFactory:
    """Factory for creating MagicLinkToken instances."""

    @staticmethod
    async def create_async(
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

    @staticmethod
    async def create(
        db: AsyncSession,
        email: Optional[str] = None,
        token_hash: Optional[str] = None,
        **kwargs,
    ) -> MagicLinkToken:
        """Create a magic link token with realistic data (backward compatibility)."""
        return await MagicLinkTokenFactory.create_async(
            db, email=email, token_hash=token_hash, **kwargs
        )


class PasskeyFactory:
    """Factory for creating Passkey instances."""

    @staticmethod
    async def create_async(
        db: AsyncSession,
        user_id: Optional[int] = None,
        user: Optional[User] = None,
        credential_id: Optional[bytes] = None,
        public_key: Optional[bytes] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> Passkey:
        """Create a passkey with realistic data."""
        if user_id is None and user is not None:
            user_id = user.id
        elif user_id is None:
            user = await UserFactory.create_async(db)
            user_id = user.id

        passkey = Passkey(
            user_id=user_id,
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

    @staticmethod
    async def create(
        db: AsyncSession,
        user: User,
        credential_id: Optional[bytes] = None,
        public_key: Optional[bytes] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> Passkey:
        """Create a passkey with realistic data (backward compatibility)."""
        return await PasskeyFactory.create_async(
            db,
            user_id=user.id,
            credential_id=credential_id,
            public_key=public_key,
            name=name,
            **kwargs,
        )
