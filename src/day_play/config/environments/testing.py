"""Testing environment settings."""
from .base import BaseEnvironmentSettings


class TestingSettings(BaseEnvironmentSettings):
    """Settings for testing environment."""

    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    log_level: str = "DEBUG"
    api_host: str = "127.0.0.1"
    api_port: int = 8001