from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from day_play.models.entities import Achievement


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
    unlock_criteria: dict[str, Any] | None = Field(
        description="Criteria to unlock the achievement"
    )
    unlocked_at: datetime | None = Field(description="When achievement was unlocked")
    is_unlocked: bool = Field(
        description="Whether achievement is unlocked (computed from unlocked_at)"
    )
    user_id: int | None = Field(description="User who owns this achievement")
    created_at: datetime = Field(description="When achievement was created")
    updated_at: datetime | None = Field(description="When achievement was last updated")

    @classmethod
    def from_entity(cls, achievement: "Achievement") -> "AchievementResponse":
        """Create AchievementResponse from Achievement entity.

        Args:
            achievement: Achievement entity from business layer

        Returns:
            AchievementResponse schema instance
        """
        return cls(
            id=achievement.id or 0,
            name=achievement.name,
            description=achievement.description,
            icon=achievement.icon,
            unlock_criteria=achievement.unlock_criteria,
            unlocked_at=achievement.unlocked_at,
            is_unlocked=achievement.unlocked_at is not None,
            user_id=achievement.user_id,
            created_at=achievement.created_at or datetime.now(),
            updated_at=achievement.updated_at,
        )

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
