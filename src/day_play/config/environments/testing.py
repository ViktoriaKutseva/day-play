"""Testing environment settings."""
from .base import BaseEnvironmentSettings


class TestingSettings(BaseEnvironmentSettings):
    """Settings for testing environment."""
    
    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    database_echo: bool = False
    log_level: str = "DEBUG"