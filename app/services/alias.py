import random
import secrets
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alias import Alias
from app.models.destination import Destination
from app.schemas.alias import validate_alias_name

# Word lists for readable alias generation
ADJECTIVES = [
    "brave",
    "calm",
    "clever",
    "cool",
    "eager",
    "fair",
    "fast",
    "fine",
    "glad",
    "good",
    "great",
    "happy",
    "kind",
    "light",
    "mint",
    "nice",
    "quick",
    "quiet",
    "safe",
    "smart",
    "swift",
    "warm",
    "wise",
    "young",
]

NOUNS = [
    "bear",
    "bird",
    "cat",
    "deer",
    "duck",
    "fish",
    "fox",
    "frog",
    "hawk",
    "lion",
    "owl",
    "seal",
    "swan",
    "wolf",
    "ant",
    "bee",
    "crab",
    "dove",
    "elk",
    "goat",
    "hare",
    "jay",
    "kite",
    "lynx",
    "mole",
    "newt",
    "orca",
    "puma",
    "quail",
    "ram",
    "stag",
    "tuna",
]


class AliasService:
    """Service for alias operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alias(
        self,
        user_id: int,
        name: str,
        domain: str,
        destination_id: int,
        note: str | None = None,
        labels: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> Alias:
        """Create a new alias."""
        # Validate the name
        validated_name = validate_alias_name(name)

        # Check if alias already exists (case-insensitive)
        existing = await self.db.execute(
            select(Alias).where(
                and_(
                    func.lower(Alias.name) == validated_name.lower(),
                    func.lower(Alias.domain) == domain.lower(),
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Alias '{validated_name}@{domain}' already exists")

        # Verify destination exists and belongs to user
        destination = await self.db.execute(
            select(Destination).where(
                and_(
                    Destination.id == destination_id,
                    Destination.user_id == user_id,
                    Destination.verified_at.is_not(None),
                )
            )
        )
        if not destination.scalar_one_or_none():
            raise ValueError("Destination not found or not verified")

        # Create the alias
        alias = Alias(
            user_id=user_id,
            name=validated_name,
            domain=domain.lower(),
            destination_id=destination_id,
            note=note,
            labels=labels or [],
            expires_at=expires_at,
        )

        self.db.add(alias)
        await self.db.commit()
        await self.db.refresh(alias)
        return alias

    async def get_alias(self, alias_id: int, user_id: int) -> Alias | None:
        """Get an alias by ID for a specific user."""
        result = await self.db.execute(
            select(Alias).where(and_(Alias.id == alias_id, Alias.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def list_aliases(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        label: str | None = None,
        active_only: bool | None = None,
    ) -> tuple[list[Alias], int]:
        """List aliases for a user with pagination and filtering."""
        query = select(Alias).where(Alias.user_id == user_id)

        # Apply filters
        if label:
            query = query.where(Alias.labels.contains([label.lower()]))

        if active_only is not None:
            query = query.where(Alias.is_active == active_only)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Alias.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        aliases = result.scalars().all()

        return list(aliases), total

    async def update_alias(
        self,
        alias_id: int,
        user_id: int,
        **updates: Any,
    ) -> Alias | None:
        """Update an alias."""
        alias = await self.get_alias(alias_id, user_id)
        if not alias:
            return None

        # If updating destination, verify it exists and belongs to user
        if "destination_id" in updates:
            destination = await self.db.execute(
                select(Destination).where(
                    and_(
                        Destination.id == updates["destination_id"],
                        Destination.user_id == user_id,
                        Destination.verified_at.is_not(None),
                    )
                )
            )
            if not destination.scalar_one_or_none():
                raise ValueError("Destination not found or not verified")

        # Apply updates
        for key, value in updates.items():
            if hasattr(alias, key) and value is not None:
                setattr(alias, key, value)

        await self.db.commit()
        await self.db.refresh(alias)
        return alias

    async def delete_alias(self, alias_id: int, user_id: int) -> bool:
        """Delete an alias."""
        alias = await self.get_alias(alias_id, user_id)
        if not alias:
            return False

        await self.db.delete(alias)
        await self.db.commit()
        return True

    async def generate_random_alias(
        self,
        domain: str,
        prefix: str | None = None,
        length: int = 12,
        max_attempts: int = 10,
    ) -> str:
        """Generate a random alias name that doesn't conflict with existing aliases."""
        domain = domain.lower()

        for attempt in range(max_attempts):
            if prefix:
                # Generate with prefix
                remaining_length = length - len(prefix) - 1  # -1 for hyphen
                if remaining_length < 2:
                    remaining_length = 2

                # Use readable pattern: prefix-adjective-noun-number
                adjective = random.choice(ADJECTIVES)
                noun = random.choice(NOUNS)
                number = random.randint(10, 99)

                name = f"{prefix}-{adjective}-{noun}-{number}"

                # Truncate if too long
                if len(name) > length:
                    name = f"{prefix}-{secrets.token_hex(3)}"
            else:
                # Generate readable pattern: adjective-noun-number
                adjective = random.choice(ADJECTIVES)
                noun = random.choice(NOUNS)
                number = random.randint(10, 999)

                name = f"{adjective}-{noun}-{number}"

                # If too long, use shorter random string
                if len(name) > length:
                    name = secrets.token_hex(length // 2)[:length]

            # Ensure it meets validation rules
            try:
                validated_name = validate_alias_name(name)
            except ValueError:
                continue

            # Check if it already exists
            existing = await self.db.execute(
                select(Alias).where(
                    and_(
                        func.lower(Alias.name) == validated_name.lower(),
                        func.lower(Alias.domain) == domain,
                    )
                )
            )

            if not existing.scalar_one_or_none():
                return validated_name

        # If we couldn't generate a unique name, raise an error
        raise ValueError("Unable to generate unique alias name after maximum attempts")
