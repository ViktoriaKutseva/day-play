"""Dependency injection composition for the API layer."""
from src.day_play.business.services import TaskService
from src.day_play.integrations.database.repositories import SQLiteTaskRepository
from src.day_play.config.settings import settings


def get_task_repository() -> SQLiteTaskRepository:
    """Create and return a task repository instance."""
    return SQLiteTaskRepository(settings.database_url)


def get_task_service() -> TaskService:
    """Create and return a task service instance."""
    repository = get_task_repository()
    return TaskService(repository)