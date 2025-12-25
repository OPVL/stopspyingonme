#!/usr/bin/env python3
"""Initialize database and run migrations."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings


async def init_database():
    """Initialize database and run migrations."""
    settings = get_settings()

    # Create engine
    engine = create_async_engine(str(settings.database_url))

    try:
        # Test connection and enable pgcrypto extension
        async with engine.begin() as conn:
            # Enable pgcrypto extension for encryption
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
            print("✓ Database connection successful")
            print("✓ pgcrypto extension enabled")

    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    finally:
        await engine.dispose()

    return True


if __name__ == "__main__":
    success = asyncio.run(init_database())
    if success:
        print("\n✓ Database initialized successfully")
        print("Run 'alembic upgrade head' to apply migrations")
    else:
        print("\n✗ Database initialization failed")
        sys.exit(1)
