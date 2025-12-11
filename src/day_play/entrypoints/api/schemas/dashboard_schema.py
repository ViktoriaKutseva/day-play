"""Dashboard API schemas.

These schemas define the structure of dashboard-related API responses.
They are pure data containers with no business logic dependencies.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from day_play.business.dashboard_service import DashboardData, UserLevelData
from day_play.business.gamification_engine import GamificationEngine
from day_play.entrypoints.api.schemas.task_schema import TaskResponse


class DualProgressResponse(BaseModel):
    """Dual progress bars data."""

    daily_completion_percent: float = Field(description="Today's task completion %")
    level_progress_percent: float = Field(description="Progress to next level %")


class UserLevelResponse(BaseModel):
    """User level and XP information."""

    user_id: int = Field(description="User identifier")
    current_level: int = Field(description="Current user level")
    total_xp: int = Field(description="Total accumulated XP")
    xp_for_current_level: int = Field(description="XP needed to reach current level")
    xp_for_next_level: int = Field(description="XP needed to reach next level")
    xp_in_current_level: int = Field(description="XP earned within current level")
    progress_percent: float = Field(description="% progress to next level")

    @classmethod
    def from_data(cls, data: UserLevelData) -> "UserLevelResponse":
        """Create response from pre-computed UserLevelData."""
        return cls(
            user_id=data.user_id,
            current_level=data.current_level,
            total_xp=data.total_xp,
            xp_for_current_level=data.xp_for_current_level,
            xp_for_next_level=data.xp_for_next_level,
            xp_in_current_level=data.xp_in_current_level,
            progress_percent=data.progress_percent,
        )


class AchievementSummaryResponse(BaseModel):
    """Achievement summary for dashboard display."""

    id: int = Field(description="Achievement identifier")
    name: str = Field(description="Achievement name")
    description: str | None = Field(description="Achievement description")
    icon: str | None = Field(description="Achievement icon path")
    unlocked_at: datetime | None = Field(description="When the achievement was unlocked")


class DashboardResponse(BaseModel):
    """Complete dashboard data in single response."""

    progress: DualProgressResponse = Field(description="Daily and level progress")
    user_level: UserLevelResponse = Field(description="User level information")
    upcoming_tasks: list[TaskResponse] = Field(description="Upcoming tasks for today")
    recent_achievements: list[AchievementSummaryResponse] = Field(
        description="Recently unlocked achievements"
    )

    @classmethod
    def from_data(
        cls,
        data: DashboardData,
        gamification: GamificationEngine,
    ) -> "DashboardResponse":
        """Create response from pre-computed DashboardData.

        Args:
            data: Pre-aggregated dashboard data from DashboardService
            gamification: Engine for task XP calculation (needed for TaskResponse)
        """
        return cls(
            progress=DualProgressResponse(
                daily_completion_percent=data.daily_completion_percent,
                level_progress_percent=data.level_progress_percent,
            ),
            user_level=UserLevelResponse.from_data(data.user_level),
            upcoming_tasks=[
                TaskResponse.from_entity(t, gamification) for t in data.upcoming_tasks
            ],
            recent_achievements=[
                AchievementSummaryResponse(
                    id=a.id or 0,
                    name=a.name,
                    description=a.description,
                    icon=a.icon,
                    unlocked_at=a.unlocked_at,
                )
                for a in data.recent_achievements
            ],
        )

