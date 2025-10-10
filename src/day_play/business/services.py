"""Business logic services for task management."""
from datetime import datetime, timezone

from .interfaces import TaskRepository, TaskServiceProtocol
from ..models.entities import Task, TaskCreate, TaskUpdate
from ..models.exceptions import TaskNotFoundError


class TaskService(TaskServiceProtocol):
    """Service for task business logic operations."""

    def __init__(self, repository: TaskRepository) -> None:
        """Initialize the task service with a repository."""
        self._repository = repository

    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task with business logic validation."""
        # Create the task entity
        task = Task.model_validate(task_data)

        # Business logic: ensure created_at is set
        if task.created_at is None:
            task.created_at = datetime.now(timezone.utc)

        # Save the task
        await self._repository.save(task)

        return task

    async def get_task(self, task_id: int) -> Task:
        """Get a task by ID with business logic validation."""
        task = await self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    async def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return await self._repository.get_all()

    async def update_task(self, task_id: int, updates: TaskUpdate) -> Task:
        """Update an existing task with business logic validation."""
        # Apply updates
        updated_task = await self._repository.update(task_id, updates)
        if updated_task is None:
            raise TaskNotFoundError(task_id)

        return updated_task

    async def delete_task(self, task_id: int) -> None:
        """Delete a task by ID with business logic validation."""
        # Check if task exists before deleting
        await self.get_task(task_id)  # This will raise if not found

        # Delete the task
        deleted = await self._repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(task_id)