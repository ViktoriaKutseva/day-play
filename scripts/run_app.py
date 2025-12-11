#!/usr/bin/env python
"""
Start the Day-Play application (combined API + Web interface).

This script runs the unified FastAPI application that serves:
- API endpoints at /api/*
- Web interface at /, /history, /settings
- Static files at /static/*
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "day_play.entrypoints.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
