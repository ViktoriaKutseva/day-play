from datetime import date as date_type, datetime, timezone
from typing import Any

from pydantic import field_validator
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency


class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    due_date: datetime | None = Field(default=None)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    next_occurrence: datetime | None = Field(default=None)
    tags: list[str] | None = Field(default=None, sa_column=Column(JSON))
    custom_xp: int | None = Field(default=None)
    recurrence_rule_on_complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title cannot be empty or just whitespace.")
        return value.strip()

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)
    username: str | None = Field(default=None, max_length=150, unique=True, index=True)
    current_level: int = Field(default=1)
    total_xp: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Achievement(SQLModel, table=True):
    __tablename__ = "achievement"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field(None, max_length=255)
    unlock_criteria: dict[str, Any] = Field(sa_column=Column(JSON))
    unlocked_at: datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Prize(SQLModel, table=True):
    __tablename__ = "prize"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    cost_xp: int = Field(default=0, ge=0)
    redeemed: bool = Field(default=False)
    redeemed_at: datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#4B9441")
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)