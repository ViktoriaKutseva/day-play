"""Business services for task management."""
from typing import List

from ..models.entities import Task
from ..models.value_objects import TaskCreate, TaskUpdate
from ..models.exceptions import TaskNotFoundError, InvalidTaskDataError
from .interfaces import TaskRepository


class TaskService:
    """Service for task business logic."""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    async def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        tasks = await self._task_repository.get_all()
        return tasks
    
    async def get_task_by_id(self, task_id: int) -> Task:
        """Get a task by ID."""
        
        if task_id <= 0:
            raise InvalidTaskDataError("Task ID must be positive")
        
        task = await self._task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        
        return task
    
    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        
        # Business logic validation
        if not task_data.task_name.strip():
            raise InvalidTaskDataError("Task name cannot be empty")
        
        task = await self._task_repository.create(task_data)
        return task
    
    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Task:
        """Update an existing task."""
        
        if task_id <= 0:
            raise InvalidTaskDataError("Task ID must be positive")
        
        # Check if task exists first
        existing_task = await self._task_repository.get_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        
        # Business logic validation
        if task_data.task_name is not None and not task_data.task_name.strip():
            raise InvalidTaskDataError("Task name cannot be empty")
        
        updated_task = await self._task_repository.update(task_id, task_data)
        if not updated_task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        
        return updated_task
    
    async def delete_task(self, task_id: int) -> None:
        """Delete a task."""
        
        if task_id <= 0:
            raise InvalidTaskDataError("Task ID must be positive")
        
        deleted = await self._task_repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")