"""Base settings for all environments."""
from pydantic import BaseModel


class BaseEnvironmentSettings(BaseModel):
    """Base settings shared across all environments."""
    
    app_name: str = "day-play"
    version: str = "0.1.0"
    description: str = "Personal project for gamified task management and FastAPI learning"
    
    # Database settings
    database_url: str = "sqlite:///database.db"
    database_echo: bool = False
    
    # Logging settings
    log_level: str = "INFO"