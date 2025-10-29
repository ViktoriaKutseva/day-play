import sys
from typing import Optional
from loguru import logger


def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Centralized logging configuration using loguru.

    Args:
        log_file: Path to log file. If not specified, logging will be console-only.
    """
    # Remove default loguru handler to prevent duplication
    logger.remove(0)

    # Add handler for console output (INFO and above)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    if log_file:
        # Add handler for file writing
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="10 MB",
            retention=1,
            enqueue=True,
            serialize=False,
        )