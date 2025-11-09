from day_play.config.environments.base import BaseEnvironmentSettings


class ConfigForTesting(BaseEnvironmentSettings):
    """Configuration settings for testing environment."""

    debug: bool = True
    database_url: str = "sqlite:///:memory:"  # In-memory database for tests
    log_level: str = "DEBUG"
    skip_auth: bool = True  # Disable authentication for faster tests
