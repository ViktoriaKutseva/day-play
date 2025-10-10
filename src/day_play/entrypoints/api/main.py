"""Main FastAPI application."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from sqlmodel import Session, select

from ...config.settings import settings
from .dependencies import create_db_and_tables, engine
from .routes.tasks import router as tasks_router
from ...integrations.database.models import TaskDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    create_db_and_tables()
    
    # Create sample data if database is empty
    with Session(engine) as session:
        if not session.exec(select(TaskDB)).first():
            sample_tasks = [
                TaskDB(
                    task_name="Sample Task 1",
                    due_date=datetime(2025, 12, 31, tzinfo=timezone.utc)
                ),
                TaskDB(
                    task_name="Sample Task 2", 
                    completed=True,
                    due_date=datetime(2025, 11, 30, tzinfo=timezone.utc)
                ),
                TaskDB(
                    task_name="Sample Task 3",
                    due_date=datetime(2025, 10, 15, tzinfo=timezone.utc)
                )
            ]
            session.add_all(sample_tasks)
            session.commit()
    
    yield
    
    # Shutdown (if needed)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
        root_path="/api/v1",
        lifespan=lifespan
    )
    
    # Include routers
    app.include_router(tasks_router)
    
    # Health check endpoint
    @app.get("/")
    async def health_check():
        """Health check endpoint."""
        return {"message": "Day Play API is running!", "version": settings.version}
    
    return app


# Create the app instance
app = create_app()