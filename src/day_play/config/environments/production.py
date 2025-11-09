from typing import Any

from pydantic import Field, SecretStr, field_validator

from day_play.config.environments.base import BaseEnvironmentSettings


class ProductionSettings(BaseEnvironmentSettings):
    """Production environment settings."""

    debug: bool = False
    database_url: str = Field(default="", alias="DATABASE_URL")
    log_level: str = "WARNING"
    _secret_database_url: SecretStr | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: Any) -> str:
        """Validate that database URL is provided in production."""
        if isinstance(v, SecretStr):
            return v.get_secret_value()
        if not v or v == "":
            raise ValueError("DATABASE_URL must be set in production environment")
        return str(v)

    def get_secret_database_url(self) -> SecretStr:
        """Get database URL as SecretStr for secure handling."""
        if self._secret_database_url is None:
            self._secret_database_url = SecretStr(self.database_url)
        return self._secret_database_url
