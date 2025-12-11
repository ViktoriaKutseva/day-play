from datetime import date as date_type
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from day_play.models.entities import DailyProgress


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

    @classmethod
    def from_entity(cls, progress: "DailyProgress") -> "DailyProgressResponse":
        """Create DailyProgressResponse from DailyProgress entity.

        Args:
            progress: DailyProgress entity from business layer

        Returns:
            DailyProgressResponse schema instance
        """
        return cls(
            date=progress.date,
            tasks_completed=progress.tasks_completed,
            tasks_total=progress.tasks_total,
            completion_percentage=progress.completion_percentage,
            daily_xp_earned=progress.daily_xp_earned,
        )

    @classmethod
    def empty(cls, date: date_type) -> "DailyProgressResponse":
        """Create an empty DailyProgressResponse for a date with no data.

        Args:
            date: The date for the empty progress

        Returns:
            DailyProgressResponse with zero values
        """
        return cls(
            date=date,
            tasks_completed=0,
            tasks_total=0,
            completion_percentage=0.0,
            daily_xp_earned=0,
        )


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

    @classmethod
    def from_entries(
        cls,
        start_date: date_type,
        end_date: date_type,
        entries: list["DailyProgress"],
    ) -> "HistoryResponse":
        """Create HistoryResponse from a list of DailyProgress entities.

        Args:
            start_date: Start of the date range
            end_date: End of the date range
            entries: List of DailyProgress entities

        Returns:
            HistoryResponse with aggregated stats
        """
        daily_responses = [DailyProgressResponse.from_entity(entry) for entry in entries]

        total_tasks_completed = sum(entry.tasks_completed for entry in entries)
        total_xp_earned = sum(entry.daily_xp_earned for entry in entries)
        average_completion = (
            sum(entry.completion_percentage for entry in entries) / len(entries)
            if entries
            else 0.0
        )

        return cls(
            start_date=start_date,
            end_date=end_date,
            progress_entries=daily_responses,
            total_tasks_completed=total_tasks_completed,
            total_xp_earned=total_xp_earned,
            average_completion=round(average_completion, 2),
        )
