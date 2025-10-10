"""Main entry point for the Day Play application."""
import uvicorn

from src.day_play.entrypoints.api.main import create_app
from src.day_play.config.settings import settings
from src.day_play.config.logging_config import setup_logging

# Configure logging
setup_logging(
    log_level=settings.log_level,
    app_name=settings.app_name
)

# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
