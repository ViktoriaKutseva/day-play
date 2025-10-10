"""Pydantic schemas for API requests and responses."""
from typing import Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel

from ...models.entities import Task

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """Generic response wrapper."""
    data: T


class TaskResponse(BaseModel):
    """Task response schema."""
    task_id: int | None
    task_name: str
    completed: bool
    due_date: datetime | None
    created_at: datetime
    
    @classmethod
    def from_entity(cls, task: Task) -> "TaskResponse":
        """Create response from entity."""
        return cls(
            task_id=task.task_id,
            task_name=task.task_name,
            completed=task.completed,
            due_date=task.due_date,
            created_at=task.created_at
        )


class TaskCreateRequest(BaseModel):
    """Request schema for creating a task."""
    task_name: str
    completed: bool = False
    due_date: datetime | None = None


class TaskUpdateRequest(BaseModel):
    """Request schema for updating a task."""
    task_name: str | None = None
    completed: bool | None = None
    due_date: datetime | None = None