# config/settings.py - All settings using Pydantic

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot settings with validation"""
    
    telegram_bot_token: SecretStr = Field(
        ...,
        description="Telegram Bot API token from BotFather"
    )
    database_url: str = Field(
        default="sqlite:///bot.db",
        description="Database connection URL"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields in .env
    }


# Global settings instance
settings = Settings()