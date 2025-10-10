"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ...models.entities import Task


class TaskResponse(BaseModel):
    """Response model for Task."""
    task_id: Optional[int] = Field(None, description="Unique identifier for the task")
    task_name: str = Field(..., description="Name of the task")
    completed: bool = Field(default=False, description="Whether the task is completed")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")
    created_at: datetime = Field(..., description="When the task was created")

    @classmethod
    def from_entity(cls, task: "Task") -> "TaskResponse":
        """Create a response from a Task entity."""
        return cls(
            task_id=task.task_id,
            task_name=task.task_name,
            completed=task.completed,
            due_date=task.due_date,
            created_at=task.created_at
        )


class TaskListResponse(BaseModel):
    """Response model for a list of tasks."""
    data: list[TaskResponse] = Field(..., description="List of tasks")


class TaskSingleResponse(BaseModel):
    """Response model for a single task."""
    data: TaskResponse = Field(..., description="Task data")


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")