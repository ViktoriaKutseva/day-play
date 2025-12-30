from datetime import date, datetime, timedelta, timezone

from loguru import logger

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.interfaces import (
    DailyProgressRepository,
    TaskRepository,
    UserRepository,
)
from day_play.models.entities import DailyProgress


class ProgressTracker:
    """Service for calculating daily completion and level progress."""

    def __init__(
            self, gamification: GamificationEngine,
            task_repository: TaskRepository,
            user_repository: UserRepository,
            daily_progress_repository: DailyProgressRepository):
        """Initialize progress tracker with dependencies.

        Args:
            gamification: Engine for XP/level calculations
            task_repo: Repository for task data access
            user_repo: Repository for user data access
            progress_repo: Repository for progress data access
        """
        self._gamification = gamification
        self._task_repository = task_repository
        self._user_repository = user_repository
        self._daily_progress_repository = daily_progress_repository

    def _calculate_percent(self, completed: int, total: int) -> float:
        """Calculate completion percentage.

        Args:
            completed: Number of completed items
            total: Total number of items

        Returns:
            Percentage (0.0 to 100.0)

        Example:
            _calculate_percent(5, 10) → 50.0
            _calculate_percent(0, 0) → 0.0
            _calculate_percent(3, 3) → 100.0
        """
        if total == 0:
            return 0
        return (completed/total) * 100

    def calculate_daily_progression(self, user_id: int) -> float:
        """Calculate daily completion percentage for today.

        Calculates what percentage of today's scheduled tasks are completed.
        Returns 0.0 if no tasks are scheduled for today.

        Args:
            user_id: ID of the user

        Returns:
            Completion percentage (0.0 to 100.0)

        Example:
            If user has 10 tasks today and completed 7:
            Result: 70.0
        """
        today = datetime.now(timezone.utc).date()
        progress = self.get_daily_progress(user_id, today)
        return progress.completion_percentage

    def get_daily_progress(self, user_id: int, target_date: date) -> DailyProgress:
        """Calculate daily progress for a specific date.

        Args:
            user_id: ID of the user
            target_date: Date to calculate progress for

        Returns:
            DailyProgress entity with calculated values
        """
        logger.debug(f"Calculating daily progress for user {user_id} on {target_date}")

        # Fetch tasks for the specific date
        today_tasks = self._task_repository.get_tasks_for_today(user_id, target_date)
        
        tasks_completed = sum(1 for t in today_tasks if t.is_completed())
        tasks_total = len(today_tasks)
        completion_percentage = self._calculate_percent(tasks_completed, tasks_total)
        daily_xp_earned = sum(self._gamification.calculate_xp(t) for t in today_tasks if t.is_completed())

        progress = DailyProgress(
            user_id=user_id,
            date=target_date,
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            completion_percentage=completion_percentage,
            daily_xp_earned=daily_xp_earned,
        )

        logger.info(
            "Daily progress calculated",
            user_id=user_id,
            date=target_date,
            completed=tasks_completed,
            total=tasks_total,
            percentage=completion_percentage,
        )

        return progress

    def calculate_overall_progression(self, user_id: int) -> float:
        """Calculate level progression percentage for user.

        Shows how close the user is to reaching the next level based on
        accumulated XP within the current level.

        Args:
            user_id: ID of the user

        Returns:
            Level progress percentage (0.0 to 100.0)

        Example:
            If user is level 5 with 500 total XP:
            - Level 5 starts at 400 XP
            - Level 6 starts at 600 XP
            - Progress in level: 500 - 400 = 100 XP
            - XP needed for level: 600 - 400 = 200 XP
            - Result: (100 / 200) * 100 = 50.0%
        """

        logger.debug("Calculating overall progression", user_id=user_id)

        user = self._user_repository.get_by_id(user_id)
        if not user:
            logger.warning("User not found", user_id=user_id)
            return 0.0
        current_xp = user.total_xp
        current_level = user.current_level
        current_level_xp = self._gamification.xp_for_level(current_level)
        next_level_xp = self._gamification.xp_for_level(current_level + 1)

        xp_progress_in_level = current_xp - current_level_xp
        xp_needed_for_level = next_level_xp - current_level_xp
        percentage = self._calculate_percent(xp_progress_in_level, xp_needed_for_level)

        logger.info(
            "Overall progression calculated",
            user_id=user_id,
            level=current_level,
            total_xp=current_xp,
            xp_in_level=xp_progress_in_level,
            xp_needed=xp_needed_for_level,
            percentage=percentage,
        )
        return percentage

    def get_simple_history(self, user_id: int, limit: int = 30) -> list[DailyProgress]:
        """Get recent daily progress entries without complex aggregation.

        Args:
            user_id: ID of the user
            limit: Number of recent days to retrieve (default: 30)

        Returns:
            List of DailyProgress entries, most recent first
        """
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=limit)

        return self._daily_progress_repository.get_date_range(
            user_id, start_date, end_date
        )
    def calculate_daily_streak(self, user_id: int) -> int:
        """Calculate consecutive days user has completed tasks.

        A streak is broken if a day has 0% completion or no tasks.
        Counts backwards from today until finding a gap.

        Args:
            user_id: ID of the user

        Returns:
            Number of consecutive days with completed tasks

        Example:
            If user completed tasks on:
            - Today (Nov 27): 100% ✅
            - Yesterday (Nov 26): 80% ✅
            - Nov 25: 100% ✅
            - Nov 24: 0% ❌ (streak breaks here)
            - Nov 23: 100%

            Result: 3 (today + 2 previous days)
        """
        streak = 0
        current_date = datetime.now(timezone.utc).date()

        for _ in range(365):
            progress = self._daily_progress_repository.get_progress_by_date(
                user_id, current_date
            )
            if not progress or progress.tasks_completed == 0:
                break
            streak += 1
            current_date -= timedelta(days=1)
        logger.info("Daily streak calculated", user_id=user_id, streak=streak)
        return streak