"""Dynamic settings configuration based on environment."""
import os
from typing import Type

from .environments.base import BaseEnvironmentSettings
from .environments.development import DevelopmentSettings
from .environments.testing import TestingSettings
from .environments.production import ProductionSettings


def get_settings() -> BaseEnvironmentSettings:
    """Get settings based on the current environment."""
    env = os.getenv("ENVIRONMENT", "development").lower().strip()

    settings_map: dict[str, Type[BaseEnvironmentSettings]] = {
        "development": DevelopmentSettings,
        "testing": TestingSettings,
        "production": ProductionSettings,
    }

    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


# Global settings instance
settings = get_settings()