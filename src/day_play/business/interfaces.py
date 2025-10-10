"""Business logic interfaces (Protocol definitions)."""
from typing import Protocol, List, Optional
from ..models.entities import Task
from ..models.value_objects import TaskCreate, TaskUpdate


class TaskRepository(Protocol):
    """Interface for task repository operations."""
    
    async def get_all(self) -> List[Task]:
        """Get all tasks."""
        ...
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        ...
    
    async def create(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        ...
    
    async def update(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task."""
        ...
    
    async def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""
        ...