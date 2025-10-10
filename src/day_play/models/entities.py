"""Core entities for the Day Play application."""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    """Task entity representing a user task."""

    task_id: Optional[int] = None
    task_name: str = Field(..., min_length=1, max_length=255)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, v: str) -> str:
        """Validate task name is not empty."""
        if not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.completed

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None:
            return False
        return datetime.now(timezone.utc) > self.due_date and not self.completed

    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.completed = True