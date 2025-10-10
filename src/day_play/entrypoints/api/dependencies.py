"""Dependency injection for API endpoints."""
from sqlmodel import Session, create_engine
from fastapi import Depends
from typing import Annotated

from ...config.settings import settings
from ...business.services import TaskService
from ...integrations.database.repositories import SQLModelTaskRepository


# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.database_echo
)


def create_db_and_tables():
    """Create database tables."""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_task_service(session: SessionDep) -> TaskService:
    """Create task service with dependencies."""
    task_repository = SQLModelTaskRepository(session)
    return TaskService(task_repository)