"""Logging configuration for the application."""
import sys
from typing import Optional
from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    app_name: str = "day-play"
) -> None:
    """Configure logging for the application.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
        app_name: Application name for log formatting
    """
    # Remove default loguru handler
    logger.remove()

    # Convert string log level to loguru level
    level_map = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL"
    }
    level = level_map.get(log_level.upper(), "INFO")

    # Add console handler
    logger.add(
        sys.stdout,
        level=level,
        colorize=True,
        format=f"<green>{{time:YYYY-MM-DD HH:mm:ss.SSS}}</green> | <level>{{level: <8}}</level> | <cyan>{app_name}</cyan> - <white>{{message}}</white> | {{extra}}",
    )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
            rotation="10 MB",
            retention=5,
            enqueue=True,
            serialize=False,
        )