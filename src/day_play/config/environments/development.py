from day_play.config.environments.base import BaseEnvironmentSettings


class DevelopmentSettings(BaseEnvironmentSettings):
    """Development environment settings."""

    debug: bool = True
    database_url: str = "sqlite:///./data/dev.db"
    log_level: str = "DEBUG"
