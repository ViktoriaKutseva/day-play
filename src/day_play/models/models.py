from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class RecurrenceType(str, Enum):
    """Enumeration for task recurrence types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NONE = "none"


class User(SQLModel, table=True):
    """User model for storing user information."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(unique=True, index=True)  # Telegram user ID
    name: str = Field(max_length=255)
    lvl: int = Field(default=1, ge=1)  # Level, minimum 1
    score: int = Field(default=0, ge=0)  # Total score, non-negative

    # Relationship to tasks created by this user
    tasks: list["Task"] = Relationship(back_populates="creator")
    # Relationship to task completions by this user
    completions: list["TaskCompletion"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Task model for storing task definitions."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    recurrence: RecurrenceType = Field(default=RecurrenceType.NONE)
    due_date: Optional[date] = Field(default=None)
    score: int = Field(default=10, ge=0)  # Points awarded for completion

    # Foreign key to creator
    creator_id: int = Field(foreign_key="user.id", index=True)

    # Relationships
    creator: User = Relationship(back_populates="tasks")
    completions: list["TaskCompletion"] = Relationship(back_populates="task")


class TaskCompletion(SQLModel, table=True):
    """Task completion tracking model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    completed_date: datetime = Field(default_factory=datetime.utcnow)
    times_completed: int = Field(default=1, ge=1)  # How many times this task was completed

    # Foreign keys
    task_id: int = Field(foreign_key="task.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    # Relationships
    task: Task = Relationship(back_populates="completions")
    user: User = Relationship(back_populates="completions")