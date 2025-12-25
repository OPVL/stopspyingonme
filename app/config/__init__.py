"""Configuration package."""

from app.config.environments import (
    BaseAppSettings,
    DevelopmentSettings,
    ProductionSettings,
    StagingSettings,
    TestingSettings,
    get_settings_for_environment,
)
from app.config.main import get_settings

# Backward compatibility
Settings = BaseAppSettings

__all__ = [
    "BaseAppSettings",
    "Settings",
    "DevelopmentSettings",
    "ProductionSettings",
    "StagingSettings",
    "TestingSettings",
    "get_settings_for_environment",
    "get_settings",
]
