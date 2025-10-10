"""Main settings configuration with dynamic environment selection."""
import os

from .environments.base import BaseEnvironmentSettings
from .environments.development import DevelopmentSettings
from .environments.production import ProductionSettings
from .environments.testing import TestingSettings


def get_settings() -> BaseEnvironmentSettings:
    """Get settings based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "testing": TestingSettings,
        "production": ProductionSettings,
    }
    
    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


# Global settings instance
settings = get_settings()