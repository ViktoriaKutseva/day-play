from datetime import date as date_type, datetime
from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency


class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    priority: Priority = Field(default=Priority.MEDIUM)
    urgency: Urgency = Field(default=Urgency.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    due_date: datetime | None = Field(default=None)
    recurrence_pattern: RecurrencePattern = Field(default=RecurrencePattern.NONE)
    next_occurrence: datetime | None = Field(default=None)
    custom_xp: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)
    username: str | None = Field(default=None, max_length=150, unique=True, index=True)
    current_level: int = Field(default=1)
    total_xp: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DailyProgress(SQLModel, table=True):
    __tablename__ = "daily_progress"

    id: int | None = Field(default=None, primary_key=True)
    date: date_type = Field(default_factory=date_type.today, index=True)
    tasks_completed: int = Field(default=0)
    tasks_total: int = Field(default=0)
    completion_percentage: float = Field(default=0.0)
    daily_xp_earned: int = Field(default=0)
    user_id: int = Field(foreign_key="user.id", index=True)

class Achievement(SQLModel, table=True):
    __tablename__ = "achievement"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(max_length=1000)
    icon: str = Field(max_length=255)
    unlock_criteria: dict[str, Any] = Field(sa_column=Column(JSON))
    unlocked_at: datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Prize(SQLModel, table=True):
    __tablename__ = "prize"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(max_length=1000)
    cost_xp: int = Field(default=0, ge=0)
    redeemed: bool = Field(default=False)
    redeemed_at: datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
