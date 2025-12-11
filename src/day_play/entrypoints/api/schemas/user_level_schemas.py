from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from day_play.entrypoints.api.schemas.achievement_schema import AchievementResponse
from day_play.entrypoints.api.schemas.task_schema import TaskResponse


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
