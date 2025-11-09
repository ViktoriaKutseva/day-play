import sys

from loguru import logger


def configure_logging(log_file: str | None = None, log_level: str = "INFO") -> None:
    """
    Configure logging with loguru.

    Args:
        log_file: Path to log file. If not specified, logging will be console-only.
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Remove default loguru handler
    logger.remove()

    # Add handler for console output
    logger.add(
        sys.stdout,
        level=log_level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}:{line}</cyan> - "
            "<white>{message}</white> | "
            "{extra}"
        ),
    )

    if log_file:
        # Add handler for file writing
        logger.add(
            log_file,
            level=log_level,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{name}:{function}:{line} - "
                "{message} | "
                "{extra}"
            ),
            rotation="10 MB",
            retention=1,
            enqueue=True,
            serialize=False,
        )
        logger.info(f"File logging enabled: {log_file}")

    logger.info(f"Logging configured with level: {log_level}")
