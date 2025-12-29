#!/usr/bin/env python3
"""Wipe database script."""


import asyncio
import os
import sys

from sqlalchemy import text

from app.config import get_settings
from app.db.session import AsyncSessionLocal

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


async def wipe_database() -> None:
    """Wipe all database data."""
    settings = get_settings()
    if settings.environment == "production":
        print("❌ Cannot wipe production database")
        sys.exit(1)

    print("🧹 Wiping database...")

    async with AsyncSessionLocal() as session:
        await session.execute(text("DROP SCHEMA public CASCADE"))
        await session.execute(text("CREATE SCHEMA public"))
        await session.commit()

    print("✅ Database wiped successfully")


if __name__ == "__main__":
    asyncio.run(wipe_database())
