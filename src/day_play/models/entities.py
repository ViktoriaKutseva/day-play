from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency


class Task(BaseModel):
    id: int | None = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    tags: list[str] | None = None
    category: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    due_date: datetime | None = None
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    recurrence_rule_on_complete: bool = False
    next_occurrence: datetime | None = None
    custom_xp: int = 10
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

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title cannot be empty or just whitespace.")
        return value.strip()

    @field_validator("custom_xp")
    @classmethod
    def validate_xp(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("XP cannot be negative")
        return value
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: str) -> str | None:
        if not value.strip():
            raise ValueError("Tag cannot be empty")
        return value.strip()
class User(BaseModel):
    id: int | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    current_level: int = 1
    total_xp: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

class Achievement(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field (None, max_length=255)
    unlock_criteria: dict[str, Any] | None = None
    unlocked_at: datetime | None = None
    user_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class Prize(BaseModel):
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    cost_xp: int = Field(default=0, ge=0)
    redeemed: bool = False
    redeemed_at: datetime | None = None
    user_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty or just whitespace.")
        return value.strip()

class Tag(BaseModel):
    id:int | None = None
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#4B9441")
    user_id: int
