from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency


class Task(BaseModel):
    id: int | None = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    priority: Priority = Priority.MEDIUM
    urgency: Urgency = Urgency.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    due_date: datetime | None = None
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    next_occurrence: datetime | None = None
    custom_xp: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    user_id: int | None = None
    def is_overdue(self) -> bool:
        """Check if task is overdue (past due date and not completed)."""
        if self.due_date is None or self.status == TaskStatus.COMPLETED:
            return False
        return self.due_date < datetime.now()

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

class User(BaseModel):
    id: int | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    current_level: int = 1
    total_xp: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

class DailyProgress(BaseModel):
    id: int | None = None
    user_id: int
    date: date
    tasks_completed: int = 0
    tasks_total: int = 0
    completion_percentage: float = 0.0
    daily_xp_earned: int = 0

class Achievement(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    icon: str = Field(..., min_length=1, max_length=255)
    unlock_criteria: dict[str, Any] | None = None
    unlocked_at: datetime | None = None
    user_id: int | None = None
    created_at: datetime | None = None

class Prize(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    cost_xp: int = Field(default=0, ge=0)
    redeemed: bool = False
    redeemed_at: datetime | None = None
    user_id: int | None = None
