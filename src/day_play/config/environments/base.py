from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvironmentSettings(BaseSettings):
    """Base settings for all environments."""

    # Application metadata
    app_name: str = "day-play"
    version: str = "0.1.0"

    # Database configuration
    database_url: str = "sqlite:///./day_play.db"

    # Logging configuration
    log_level: str = "INFO"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=[".env.local", ".env"],
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )
