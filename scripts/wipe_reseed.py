#!/usr/bin/env python3
"""Wipe and reseed database script."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from app.config import get_settings

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


async def wipe_and_reseed() -> None:
    """Wipe database and reseed with default data."""
    settings = get_settings()
    if settings.environment == "production":
        print("❌ Cannot wipe production database")
        sys.exit(1)

    print("🔄 Starting wipe and reseed process...")

    # Run scripts in sequence
    scripts = [
        ["python", "scripts/wipe_db.py"],
        ["python", "scripts/init_db.py"],
        ["alembic", "upgrade", "head"],
        ["python", "scripts/seed_db.py", "--scenario", "default"],
    ]

    for script in scripts:
        result = subprocess.run(script, cwd=project_root)
        if result.returncode != 0:
            print(f"❌ Failed at step: {' '.join(script)}")
            sys.exit(1)

    print("✅ Wipe and reseed completed successfully")


if __name__ == "__main__":
    asyncio.run(wipe_and_reseed())
