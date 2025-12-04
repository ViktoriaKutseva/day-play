from datetime import date as date_type
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

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

class PrizeCreate(BaseModel):
    """Schema for creating a new prize."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Prize title",
        examples=["Gift Card"],
        )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Detailed prize description",
        )
    cost_xp: int = Field(
        default=0,
        ge=0,
        description="XP required to unlock this prize",
        examples=[500],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Movie night",
                    "description": "Watch a movie of your choice",
                    "cost_xp": 500,
                }
            ]
        }
    }

class PrizeUpdate(BaseModel):
    """Schema for updating an existing prize (partial updates)."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New prize title",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="New prize description",
    )
    cost_xp: int | None = Field(
        default=None,
        ge=0,
        description="New XP cost to unlock this prize",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Ensure name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip() if v else v

class PrizeResponse(BaseModel):
    """Schema for prize response."""
    id: int = Field(description="Unique prize identifier")
    name: str = Field(description="Prize name")
    description: str | None = Field(description="Prize description")
    cost_xp: int = Field(description="XP cost to unlock this prize")
    redeemed: bool = Field(description="Whether the prize has been redeemed")
    redeemed_at: datetime | None = Field(description="When prize was redeemed")
    is_available: bool = Field(description="Whether user has enough XP to redeem (computed)")
    user_id: int | None = Field(description="User who owns this prize")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Movie night",
                    "description": "Watch a movie of your choice",
                    "cost_xp": 500,
                    "redeemed": False,
                    "redeemed_at": None,
                    "is_available": True,
                    "user_id": 1,
                }
            ]
        }
    }
class AchievementCreate(BaseModel):
    """Schema for creating a new achievement."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Achievement name",
        examples=["First Steps"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Detailed achievement description",
    )
    icon: str | None = Field(
        default=None,
        max_length=255,
        description="URL or path to achievement icon",
        examples=["/images/achievements/first_steps.png"],
    )
    unlock_criteria: dict[str, Any] | None = Field(
        default=None,
        description="Criteria to unlock the achievement",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "First Steps",
                    "description": "Complete your first task",
                    "icon": "/images/achievements/first_steps.png",
                    "unlock_criteria": {"type": "task_count", "count": 1},
                }
            ]
        }
    }

class AchievementUpdate(BaseModel):
    """Schema for updating an existing achievement (partial updates)."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New achievement name",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="New achievement description",
    )
    icon: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New URL or path to achievement icon",
    )
    unlock_criteria: dict[str, Any] | None = Field(
        default=None,
        description="New criteria to unlock the achievement",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Ensure name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip() if v else v

class AchievementResponse(BaseModel):
    """Schema for achievement response."""
    id: int = Field(description="Unique achievement identifier")
    name: str = Field(description="Achievement name")
    description: str | None = Field(description="Achievement description")
    icon: str | None = Field(description="URL or path to achievement icon")
    unlock_criteria: dict[str, Any] | None = Field(description="Criteria to unlock the achievement")
    unlocked_at: datetime | None = Field(description="When achievement was unlocked")
    is_unlocked: bool = Field(description="Whether achievement is unlocked (computed from unlocked_at)")
    user_id: int | None = Field(description="User who owns this achievement")
    created_at: datetime = Field(description="When achievement was created")
    updated_at: datetime | None = Field(description="When achievement was last updated")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "First Steps",
                    "description": "Complete your first task",
                    "icon": "/images/achievements/first_steps.png",
                    "unlock_criteria": {"type": "task_count", "count": 1},
                    "unlocked_at": "2025-12-02T14:30:00",
                    "is_unlocked": True,
                    "user_id": 1,
                    "created_at": "2025-12-01T10:00:00",
                }
            ]
        }
    }

class UserLevelResponse(BaseModel):
    """Schema for user level and XP information."""

    current_level: int = Field(ge=1, description="User's current level")
    total_xp: int = Field(ge=0, description="User's total XP earned")
    xp_for_current_level: int = Field(
        ge=0,
        description="XP required to reach current level",
    )
    xp_for_next_level: int = Field(
        ge=0,
        description="XP required to reach next level",
    )
    xp_in_current_level: int = Field(
        ge=0,
        description="XP earned within current level",
    )
    xp_needed_for_next: int = Field(
        ge=0,
        description="XP still needed to reach next level",
    )
    level_progress_percentage: float = Field(
        ge=0,
        le=100,
        description="Progress percentage toward next level",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_level": 5,
                    "total_xp": 750,
                    "xp_for_current_level": 568,
                    "xp_for_next_level": 869,
                    "xp_in_current_level": 182,
                    "xp_needed_for_next": 119,
                    "level_progress_percentage": 60.5,
                }
            ]
        }
    }




class DashboardResponse(BaseModel):
    """Schema for dashboard overview data."""

    # Daily progress
    daily_completion_percentage: float = Field(
        ge=0,
        le=100,
        description="Percentage of today's tasks completed",
    )
    tasks_completed_today: int = Field(
        ge=0,
        description="Number of tasks completed today",
    )
    tasks_total_today: int = Field(
        ge=0,
        description="Total number of tasks for today",
    )
    daily_xp_earned: int = Field(
        ge=0,
        description="XP earned today",
    )

    # User level
    user_level: UserLevelResponse = Field(description="User level information")

    # Quick lists
    upcoming_tasks: list[TaskResponse] = Field(
        default=[],
        description="Upcoming and overdue tasks",
    )
    recent_achievements: list[AchievementResponse] = Field(
        default=[],
        description="Recently unlocked achievements",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "daily_completion_percentage": 60.0,
                    "tasks_completed_today": 3,
                    "tasks_total_today": 5,
                    "daily_xp_earned": 75,
                    "user_level": {
                        "current_level": 5,
                        "total_xp": 750,
                        "xp_for_current_level": 568,
                        "xp_for_next_level": 869,
                        "xp_in_current_level": 182,
                        "xp_needed_for_next": 119,
                        "level_progress_percentage": 60.5,
                    },
                    "upcoming_tasks": [],
                    "recent_achievements": [],
                }
            ]
        }
    }


# ============================================================================
# History Schemas
# ============================================================================

class DailyProgressResponse(BaseModel):
    """Schema for daily progress summary."""

    date: date_type = Field(description="Date of the progress record")
    tasks_completed: int = Field(ge=0, description="Tasks completed that day")
    tasks_total: int = Field(ge=0, description="Total tasks that day")
    completion_percentage: float = Field(
        ge=0,
        le=100,
        description="Completion percentage",
    )
    daily_xp_earned: int = Field(ge=0, description="XP earned that day")


class HistoryResponse(BaseModel):
    """Schema for history page data."""

    start_date: date_type = Field(description="Start of date range")
    end_date: date_type = Field(description="End of date range")
    progress_entries: list[DailyProgressResponse] = Field(
        description="Daily progress for each day in range",
    )
    total_tasks_completed: int = Field(
        ge=0,
        description="Total tasks completed in range",
    )
    total_xp_earned: int = Field(
        ge=0,
        description="Total XP earned in range",
    )
    average_completion: float = Field(
        ge=0,
        le=100,
        description="Average daily completion percentage",
    )

class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(description="Error detail message")


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username for the new user",
        examples=["john_doe"],
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username is not just whitespace."""
        if not v.strip():
            raise ValueError("Username cannot be empty or just whitespace")
        return v.strip()

class UserResponse(BaseModel):
    """Schema for user response."""

    id: int = Field(description="Unique user identifier")
    username: str = Field(description="Username of the user")
    current_level: int = Field(description="Current level of the user")
    total_xp: int = Field(description="Total XP of the user")
    created_at: datetime = Field(description="When the user was created")
    updated_at: datetime | None = Field(description="When the user was last updated")

class TaskListResponse(BaseModel):
    """Paginated task list response."""
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    has_next: bool