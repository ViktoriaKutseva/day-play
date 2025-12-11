from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from day_play.business.gamification_engine import GamificationEngine
from day_play.models.entities import Task
from day_play.models.enums import (
    Priority,
    RecurrencePattern,
    TaskStatus,
    Urgency,
)


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title",
        examples=["Complete project documentation"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detailed task description",
    )
    priority: Priority = Field(
        default=Priority.LOW,
        description="Task priority level (low, medium, high)",
    )
    urgency: Urgency = Field(
        default=Urgency.LOW,
        description="Task urgency level (low, medium, high)",
    )
    due_date: datetime | None = Field(
        default=None,
        description="When the task is due (ISO 8601 format)",
    )
    recurrence_pattern: RecurrencePattern = Field(
        default=RecurrencePattern.NONE,
        description="Recurrence pattern (none, daily, weekly, monthly)",
    )
    recurrence_rule_on_complete: bool = Field(
        default=False,
        description="If true, recurring task only reappears after completion",
    )
    custom_xp: int | None = Field(
        default=None,
        description="Custom XP value (overrides calculated XP)",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or just whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Review project requirements",
                    "description": "Read through all project docs",
                    "priority": "high",
                    "urgency": "medium",
                    "due_date": "2025-12-05T10:00:00",
                    "recurrence_pattern": "none",
                    "custom_xp": None,
                }
            ]
        }
    }

    def to_entity(self, user_id: int = 1) -> Task:
        """Convert schema to Task entity."""
        return Task(
            title=self.title,
            description=self.description,
            priority=self.priority,
            urgency=self.urgency,
            due_date=self.due_date,
            recurrence_pattern=self.recurrence_pattern,
            recurrence_rule_on_complete=self.recurrence_rule_on_complete,
            custom_xp=self.custom_xp,
            user_id=user_id,
        )

class TaskUpdate(BaseModel):
    """Schema for updating an existing task (partial updates)."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New task title",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="New task description",
    )
    priority: Priority | None = Field(
        default=None,
        description="New priority level",
    )
    urgency: Urgency | None = Field(
        default=None,
        description="New urgency level",
    )
    due_date: datetime | None = Field(
        default=None,
        description="New due date",
    )
    recurrence_pattern: RecurrencePattern | None = Field(
        default=None,
        description="New recurrence pattern",
    )
    custom_xp: int | None = Field(
        default=None,
        description="New custom XP value",
    )
    recurrence_rule_on_complete: bool | None = Field(
        default=None,
        description="Update whether recurring task only reappears after completion",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Ensure title is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or just whitespace")
        return v.strip() if v else v

    def apply_to(self, task:Task) -> Task:
        if self.title is not None:
            task.title = self.title
        if self.description is not None:
            task.description = self.description
        if self.priority is not None:
            task.priority = self.priority
        if self.urgency is not None:
            task.urgency = self.urgency
        if self.due_date is not None:
            task.due_date = self.due_date
        if self.recurrence_pattern is not None:
            task.recurrence_pattern = self.recurrence_pattern
        if self.custom_xp is not None:
            task.custom_xp = self.custom_xp
        if self.recurrence_rule_on_complete is not None:
            task.recurrence_rule_on_complete = self.recurrence_rule_on_complete
        return task


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str | None = Field(description="Task description")
    priority: Priority = Field(description="Task priority")
    urgency: Urgency = Field(description="Task urgency")
    status: TaskStatus = Field(description="Current task status")
    due_date: datetime | None = Field(description="Task due date")
    recurrence_pattern: RecurrencePattern = Field(description="Recurrence pattern")
    recurrence_rule_on_complete: bool = Field(
        description="If true, recurring task only reappears after completion"
    )
    next_occurrence: datetime | None = Field(description="Next occurrence for recurring tasks")
    custom_xp: int | None = Field(description="Custom XP value if set")
    xp_value: int = Field(description="XP earned on completion (computed)")
    is_overdue: bool = Field(description="Whether task is past due (computed)")
    user_id: int | None = Field(description="User who owns this task")
    created_at: datetime = Field(description="When task was created")
    updated_at: datetime | None = Field(description="When task was last updated")
    completed_at: datetime | None = Field(description="When task was completed")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Review project requirements",
                    "description": "Read through all project docs",
                    "priority": "high",
                    "urgency": "medium",
                    "status": "pending",
                    "due_date": "2025-12-05T10:00:00",
                    "recurrence_pattern": "none",
                    "recurrence_rule_on_complete": False,
                    "next_occurrence": None,
                    "custom_xp": None,
                    "xp_value": 30,
                    "is_overdue": False,
                    "user_id": 1,
                    "created_at": "2025-12-03T09:00:00",
                    "updated_at": None,
                    "completed_at": None,
                }
            ]
        }
    }

    @classmethod
    def from_entity(cls, task: Task, gamification: GamificationEngine) -> "TaskResponse":
        """Create TaskResponse from Task entity."""
        return cls(
            id=task.id or 0,
            title=task.title,
            description=task.description,
            priority=task.priority,
            urgency=task.urgency,
            status=task.status,
            due_date=task.due_date,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_rule_on_complete=task.recurrence_rule_on_complete,
            next_occurrence=task.next_occurrence,
            custom_xp=task.custom_xp,
            xp_value=gamification.calculate_xp(task),
            is_overdue=task.is_overdue(),
            user_id=task.user_id,
            created_at=task.created_at or datetime.now(),
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )
