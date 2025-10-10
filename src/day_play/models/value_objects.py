"""Value objects for the Day Play application."""
from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Value object for creating a new task."""
    
    task_name: str = Field(..., min_length=1, max_length=255)
    completed: bool = Field(default=False)
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Value object for updating an existing task."""
    
    task_name: str | None = Field(None, min_length=1, max_length=255)
    completed: bool | None = None
    due_date: datetime | None = None