#!/usr/bin/env python3
"""Database seeding script for development data."""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models import Alias, Destination, MagicLinkToken, Passkey, Session, User

# Clear problematic environment variables
if "DEBUG" in os.environ and os.environ["DEBUG"] not in [
    "true",
    "false",
    "True",
    "False",
    "1",
    "0",
]:
    del os.environ["DEBUG"]

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

fake = Faker()


class DatabaseSeeder:
    """Database seeding utility for development data."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users: List[User] = []
        self.destinations: List[Destination] = []
        self.aliases: List[Alias] = []

    async def seed_all(self, scenario: str = "default") -> None:
        """Seed database with comprehensive test data."""
        print(f"🌱 Seeding database with '{scenario}' scenario...")

        # Check if we're in production
        settings = get_settings()
        if settings.environment == "production":
            print("❌ Seeding is disabled in production environment")
            return

        # Clear existing data if requested
        await self._clear_data()

        # Seed based on scenario
        if scenario == "default":
            await self._seed_default_scenario()
        elif scenario == "edge_cases":
            await self._seed_edge_cases()
        elif scenario == "performance":
            await self._seed_performance_data()
        else:
            print(f"❌ Unknown scenario: {scenario}")
            return

        await self.session.commit()
        print("✅ Database seeding completed successfully")

    async def _clear_data(self) -> None:
        """Clear existing test data."""
        print("🧹 Clearing existing data...")

        # Delete in reverse dependency order
        await self.session.execute(text("DELETE FROM passkeys"))
        await self.session.execute(text("DELETE FROM sessions"))
        await self.session.execute(text("DELETE FROM magic_link_tokens"))
        await self.session.execute(text("DELETE FROM aliases"))
        await self.session.execute(text("DELETE FROM destinations"))
        await self.session.execute(text("DELETE FROM users"))

        await self.session.commit()
        print("✅ Existing data cleared")

    async def _seed_default_scenario(self) -> None:
        """Seed default development scenario."""
        print("📊 Creating default development data...")

        # Create sample users
        await self._create_sample_users()

        # Create destinations for each user
        await self._create_sample_destinations()

        # Create aliases with various states
        await self._create_sample_aliases()

        # Create some sessions and tokens
        await self._create_sample_auth_data()

    async def _seed_edge_cases(self) -> None:
        """Seed edge case scenarios for testing."""
        print("⚠️ Creating edge case test data...")

        # User with many aliases (approaching limits)
        power_user = await self._create_user("poweruser@example.com")
        power_dest = await self._create_destination(power_user, "poweruser@gmail.com")

        # Create 50 aliases for power user
        for i in range(50):
            await self._create_alias(
                power_user, power_dest, f"alias{i:02d}", "quitspyingon.me"
            )

        # User with unverified destinations
        unverified_user = await self._create_user("unverified@example.com")
        await self._create_destination(
            unverified_user, "unverified@gmail.com", verified=False
        )

        # User with expired tokens
        expired_user = await self._create_user("expired@example.com")
        await self._create_expired_magic_link(expired_user.email)

    async def _seed_performance_data(self) -> None:
        """Seed large dataset for performance testing."""
        print("🚀 Creating performance test data...")

        # Create 100 users with realistic data
        for i in range(100):
            user = await self._create_user(f"user{i:03d}@example.com")

            # Each user has 1-3 destinations
            dest_count = fake.random_int(min=1, max=3)
            for j in range(dest_count):
                dest = await self._create_destination(
                    user, f"user{i:03d}.dest{j}@{fake.domain_name()}"
                )

                # Each destination has 2-10 aliases
                alias_count = fake.random_int(min=2, max=10)
                for k in range(alias_count):
                    await self._create_alias(
                        user,
                        dest,
                        f"alias{k}",
                        "quitspyingon.me",
                        is_active=fake.boolean(chance_of_getting_true=80),
                    )

    async def _create_sample_users(self) -> None:
        """Create sample users with realistic data."""
        sample_emails = [
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com",
            "diana@example.com",
            "eve@example.com",
        ]

        for email in sample_emails:
            user = await self._create_user(email)
            self.users.append(user)

    async def _create_sample_destinations(self) -> None:
        """Create sample destinations for users."""
        for user in self.users:
            # Primary destination (verified)
            primary_dest = await self._create_destination(
                user, user.email.replace("example.com", "gmail.com")
            )
            self.destinations.append(primary_dest)

            # Secondary destination (some unverified)
            if fake.boolean(chance_of_getting_true=70):
                secondary_dest = await self._create_destination(
                    user,
                    user.email.replace("example.com", fake.domain_name()),
                    verified=fake.boolean(chance_of_getting_true=60),
                )
                self.destinations.append(secondary_dest)

    async def _create_sample_aliases(self) -> None:
        """Create sample aliases with various states."""
        alias_patterns = [
            "shopping",
            "newsletter",
            "social",
            "work",
            "personal",
            "temp",
            "signup",
            "test",
            "backup",
            "spam",
        ]

        for user in self.users:
            user_destinations = [d for d in self.destinations if d.user_id == user.id]
            if not user_destinations:
                continue

            # Create 3-8 aliases per user
            alias_count = fake.random_int(min=3, max=8)
            for i in range(alias_count):
                pattern = fake.random_element(alias_patterns)
                suffix = f"{i}" if i > 0 else ""

                alias = await self._create_alias(
                    user,
                    fake.random_element(user_destinations),
                    f"{pattern}{suffix}",
                    "quitspyingon.me",
                    is_active=fake.boolean(chance_of_getting_true=85),
                )
                self.aliases.append(alias)

    async def _create_sample_auth_data(self) -> None:
        """Create sample authentication data."""
        for user in self.users[:3]:  # Only for first 3 users
            # Create active session
            if fake.boolean(chance_of_getting_true=60):
                await self._create_session(user)

            # Create passkey for some users
            if fake.boolean(chance_of_getting_true=40):
                await self._create_passkey(user)

    async def _create_user(self, email: str) -> User:
        """Create a user with the given email."""
        user = User(email=email)
        self.session.add(user)
        await self.session.flush()
        return user

    async def _create_destination(
        self, user: User, email: str, verified: bool = True
    ) -> Destination:
        """Create a destination for the user."""
        destination = Destination(
            user_id=user.id,
            email=email,
            verified_at=datetime.now(timezone.utc) if verified else None,
        )
        self.session.add(destination)
        await self.session.flush()
        return destination

    async def _create_alias(
        self,
        user: User,
        destination: Destination,
        name: str,
        domain: str,
        is_active: bool = True,
    ) -> Alias:
        """Create an alias for the user."""
        alias = Alias(
            user_id=user.id,
            destination_id=destination.id,
            name=name,
            domain=domain,
            is_active=is_active,
        )
        self.session.add(alias)
        await self.session.flush()
        return alias

    async def _create_session(self, user: User) -> Session:
        """Create an active session for the user."""
        session = Session(
            user_id=user.id,
            token_hash=fake.sha256(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.session.add(session)
        await self.session.flush()
        return session

    async def _create_passkey(self, user: User) -> Passkey:
        """Create a passkey for the user."""
        passkey = Passkey(
            user_id=user.id,
            credential_id=fake.binary(length=32),
            public_key=fake.binary(length=64),
            name=f"{fake.word().title()} Key",
            sign_count=0,
        )
        self.session.add(passkey)
        await self.session.flush()
        return passkey

    async def _create_expired_magic_link(self, email: str) -> MagicLinkToken:
        """Create an expired magic link token."""
        token = MagicLinkToken(
            email=email,
            token_hash=fake.sha256(),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        self.session.add(token)
        await self.session.flush()
        return token


async def main():
    """Main seeding function."""
    parser = argparse.ArgumentParser(description="Seed development database")
    parser.add_argument(
        "--scenario",
        choices=["default", "edge_cases", "performance"],
        default="default",
        help="Seeding scenario to run",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force seeding even if data exists"
    )

    args = parser.parse_args()

    # Check environment
    settings = get_settings()
    if settings.environment == "production":
        print("❌ Cannot seed production database")
        sys.exit(1)

    print("🌱 Stop Spying On Me - Database Seeder")
    print(f"Environment: {settings.environment}")
    print(f"Database: {settings.database_url}")
    print()

    try:
        async with AsyncSessionLocal() as session:
            seeder = DatabaseSeeder(session)
            await seeder.seed_all(args.scenario)
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
