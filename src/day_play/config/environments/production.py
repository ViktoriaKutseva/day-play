"""Production environment settings."""
from pydantic import Field, SecretStr

from .base import BaseEnvironmentSettings


class ProductionSettings(BaseEnvironmentSettings):
    """Settings for production environment."""

    debug: bool = False
    database_url: SecretStr = Field(..., description="Production database URL")
    log_level: str = "WARNING"
    api_host: str = "0.0.0.0"
    api_port: int = 8000