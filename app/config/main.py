import os
from functools import lru_cache

from app.config.environments import BaseAppSettings, get_settings_for_environment


@lru_cache()
def get_settings() -> BaseAppSettings:
    """Get settings with environment-specific overrides."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return get_settings_for_environment(env)
