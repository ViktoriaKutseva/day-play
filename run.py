#!/usr/bin/env python3
"""Entry point script for running the Day Play application."""

if __name__ == "__main__":
    import uvicorn
    from src.day_play.entrypoints.api.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )