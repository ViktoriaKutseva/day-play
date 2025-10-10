from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from sqlmodel import SQLModel, Field as SQLField


class Task(SQLModel, table=True):
    """Task entity representing a task in the system."""
    task_id: int | None = SQLField(default=None, primary_key=True)
    task_name: str = SQLField(..., min_length=1, max_length=255, description="Name of the task")
    completed: bool = SQLField(default=False, description="Whether the task is completed")
    due_date: datetime | None = SQLField(default=None, description="Due date for the task")
    created_at: datetime = SQLField(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        description="When the task was created"
    )

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, v: str) -> str:
        """Validate task name is not empty and within length limits."""
        if not v or not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()


class TaskCreate(BaseModel):
    """DTO for creating a new task."""
    task_name: str = Field(..., min_length=1, max_length=255, description="Name of the task")
    completed: bool = Field(default=False, description="Whether the task is completed")
    due_date: datetime | None = Field(default=None, description="Due date for the task")

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, v: str) -> str:
        """Validate task name is not empty and within length limits."""
        if not v or not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    """DTO for updating an existing task."""
    task_name: str | None = Field(None, min_length=1, max_length=255, description="Name of the task")
    completed: bool | None = Field(None, description="Whether the task is completed")
    due_date: datetime | None = Field(None, description="Due date for the task")

    @field_validator("task_name")
    @classmethod
    def validate_task_name(cls, v: str | None) -> str | None:
        """Validate task name if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Task name cannot be empty")
        return v.strip() if v else v