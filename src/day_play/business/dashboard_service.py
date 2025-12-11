"""Dashboard data aggregation service.

This service handles the aggregation of data for the dashboard endpoint.
It coordinates between multiple services to build a complete dashboard view.
"""

from dataclasses import dataclass
from datetime import datetime

from day_play.business.achievement_manager import AchievementManager
from day_play.business.gamification_engine import GamificationEngine
from day_play.business.interfaces import UserRepository
from day_play.business.progress_tracker import ProgressTracker
from day_play.business.task_manager import TaskManager
from day_play.models.entities import Achievement, Task, User


@dataclass
class UserLevelData:
    """Pre-computed user level data."""

    user_id: int
    current_level: int
    total_xp: int
    xp_for_current_level: int
    xp_for_next_level: int
    xp_in_current_level: int
    progress_percent: float


@dataclass
class DashboardData:
    """Pre-computed dashboard data.

    This is a plain data container with all the information
    needed to build a DashboardResponse.
    """

    daily_completion_percent: float
    level_progress_percent: float
    user_level: UserLevelData
    upcoming_tasks: list[Task]
    recent_achievements: list[Achievement]


class DashboardService:
    """Service for aggregating dashboard data.

    This service coordinates between TaskManager, ProgressTracker,
    AchievementManager, and GamificationEngine to build complete
    dashboard data in a single call.
    """

    def __init__(
        self,
        task_manager: TaskManager,
        progress_tracker: ProgressTracker,
        achievement_manager: AchievementManager,
        gamification: GamificationEngine,
        user_repository: UserRepository,
    ) -> None:
        self._task_manager = task_manager
        self._progress_tracker = progress_tracker
        self._achievement_manager = achievement_manager
        self._gamification = gamification
        self._user_repository = user_repository

    def get_user_level_data(self, user: User) -> UserLevelData:
        """Get pre-computed user level data.

        Args:
            user: User entity

        Returns:
            UserLevelData with all level-related calculations
        """
        user_id = user.id or 0
        current_level_xp = self._gamification.xp_for_level(user.current_level)
        next_level_xp = self._gamification.xp_for_level(user.current_level + 1)

        return UserLevelData(
            user_id=user_id,
            current_level=user.current_level,
            total_xp=user.total_xp,
            xp_for_current_level=current_level_xp,
            xp_for_next_level=next_level_xp,
            xp_in_current_level=user.total_xp - current_level_xp,
            progress_percent=self._progress_tracker.calculate_overall_progression(user_id),
        )

    def get_dashboard_data(self, user_id: int) -> DashboardData | None:
        """Get all dashboard data for a user.

        Args:
            user_id: User's ID

        Returns:
            DashboardData with all aggregated information, or None if user not found
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            return None

        # Progress calculations
        daily_percent = self._progress_tracker.calculate_daily_progression(user_id)
        level_percent = self._progress_tracker.calculate_overall_progression(user_id)

        # Get upcoming tasks (today's incomplete tasks)
        today_tasks = self._task_manager.get_tasks_for_today(user_id)
        upcoming = [t for t in today_tasks if not t.is_completed()]

        # Get recent achievements (last 5 unlocked)
        achievements = self._achievement_manager.get_unlocked_achievements(user_id)
        recent = sorted(
            achievements,
            key=lambda a: a.unlocked_at or datetime.min,
            reverse=True,
        )[:5]

        return DashboardData(
            daily_completion_percent=daily_percent,
            level_progress_percent=level_percent,
            user_level=self.get_user_level_data(user),
            upcoming_tasks=upcoming,
            recent_achievements=recent,
        )
