# src/day_play/entrypoints/api/schemas.py
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from datetime import date
from src.day_play.models.models import RecurrenceType

# Generic response wrapper
T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    """Generic response wrapper."""
    data: T


# User schemas
class UserCreate(BaseModel):
    """Schema for creating a new user."""
    user_id: int  # Telegram user ID
    name: str


# Task schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    name: str
    description: Optional[str] = None
    recurrence: RecurrenceType = RecurrenceType.NONE
    due_date: Optional[date] = None
    score: int = 10
    creator_id: int  # User's database ID


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    name: Optional[str] = None
    description: Optional[str] = None
    recurrence: Optional[RecurrenceType] = None
    due_date: Optional[date] = None
    score: Optional[int] = None


# Task completion schemas
class TaskCompletionCreate(BaseModel):
    """Schema for recording task completion."""
    task_id: int
    user_id: int  # User's database ID