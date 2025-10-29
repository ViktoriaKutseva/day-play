#!/usr/bin/env python3
"""Script to start the FastAPI server."""
import uvicorn
from loguru import logger

if __name__ == "__main__":
    logger.info("Starting FastAPI server on http://localhost:8000")
    uvicorn.run(
        "src.day_play.entrypoints.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
