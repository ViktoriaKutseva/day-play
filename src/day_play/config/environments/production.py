"""Production environment settings."""
from .base import BaseEnvironmentSettings


class ProductionSettings(BaseEnvironmentSettings):
    """Settings for production environment."""
    
    debug: bool = False
    database_url: str = "sqlite:///database.db"
    database_echo: bool = False
    log_level: str = "WARNING"