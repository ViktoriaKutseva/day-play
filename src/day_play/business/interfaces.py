"""Business logic interfaces for the task management system."""
from typing import Protocol
from abc import abstractmethod

from ..models.entities import Task, TaskCreate, TaskUpdate


class TaskRepository(Protocol):
    """Interface for task data access operations."""

    @abstractmethod
    async def save(self, task: Task) -> None:
        """Save a task to the repository."""
        ...

    @abstractmethod
    async def get_by_id(self, task_id: int) -> Task | None:
        """Get a task by its ID."""
        ...

    @abstractmethod
    async def get_all(self) -> list[Task]:
        """Get all tasks."""
        ...

    @abstractmethod
    async def update(self, task_id: int, updates: TaskUpdate) -> Task | None:
        """Update a task with the given updates."""
        ...

    @abstractmethod
    async def delete(self, task_id: int) -> bool:
        """Delete a task by its ID. Returns True if deleted, False if not found."""
        ...


class TaskServiceProtocol(Protocol):
    """Interface for task business logic operations."""

    @abstractmethod
    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        ...

    @abstractmethod
    async def get_task(self, task_id: int) -> Task:
        """Get a task by ID."""
        ...

    @abstractmethod
    async def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        ...

    @abstractmethod
    async def update_task(self, task_id: int, updates: TaskUpdate) -> Task:
        """Update an existing task."""
        ...

    @abstractmethod
    async def delete_task(self, task_id: int) -> None:
        """Delete a task by ID."""
        ...