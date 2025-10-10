"""Development environment settings."""
from .base import BaseEnvironmentSettings


class DevelopmentSettings(BaseEnvironmentSettings):
    """Settings for development environment."""
    
    debug: bool = True
    database_url: str = "sqlite:///dev.db"
    database_echo: bool = True
    log_level: str = "DEBUG"