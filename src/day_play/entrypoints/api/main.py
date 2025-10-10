"""FastAPI application for the task management system."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.day_play.entrypoints.api.routes.tasks import router as tasks_router
from src.day_play.integrations.database.repositories import SQLiteTaskRepository
from src.day_play.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Initialize database
    repository = SQLiteTaskRepository(settings.database_url)
    repository.create_tables()
    repository.seed_initial_data()

    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="A RESTful API for daily task management built with FastAPI, SQLModel, and SQLite",
        version=settings.version,
        root_path="/api/v1",
        debug=settings.debug,
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(tasks_router, prefix="", tags=["tasks"])

    return app