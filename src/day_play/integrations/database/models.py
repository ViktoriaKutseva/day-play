"""Database models using SQLModel."""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class TaskDB(SQLModel, table=True):
    """Database model for Task."""
    
    task_id: Optional[int] = Field(default=None, primary_key=True)
    task_name: str = Field(index=True)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )