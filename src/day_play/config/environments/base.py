"""Base settings for all environments."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvironmentSettings(BaseSettings):
    """Base settings shared across all environments."""

    # Application settings
    app_name: str = Field(default="Day Play", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Database settings
    database_url: str = Field(
        default="sqlite:///dev.db",
        description="Database connection URL"
    )

    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=[".env.local", ".env"],
        case_sensitive=False,
        env_nested_delimiter="__"
    )