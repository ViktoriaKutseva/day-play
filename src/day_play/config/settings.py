import os

from day_play.config.environments.base import BaseEnvironmentSettings
from day_play.config.environments.development import DevelopmentSettings
from day_play.config.environments.production import ProductionSettings
from day_play.config.environments.testing import ConfigForTesting


def get_settings() -> BaseEnvironmentSettings:
    """
    Get settings based on ENVIRONMENT variable.

    Returns appropriate settings class based on environment:
    - development: DevelopmentSettings (default)
    - testing: ConfigForTesting
    - production: ProductionSettings
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    settings_map: dict[str, type[BaseEnvironmentSettings]] = {
        "development": DevelopmentSettings,
        "testing": ConfigForTesting,
        "production": ProductionSettings,
    }
    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


# Global settings instance
settings = get_settings()
