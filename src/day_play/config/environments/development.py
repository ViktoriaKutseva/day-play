"""Development environment settings."""
from .base import BaseEnvironmentSettings


class DevelopmentSettings(BaseEnvironmentSettings):
    """Settings for development environment."""

    debug: bool = True
    database_url: str = "sqlite:///dev.db"
    log_level: str = "DEBUG"
    api_host: str = "127.0.0.1"
    api_port: int = 8000