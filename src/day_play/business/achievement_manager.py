from datetime import datetime
from typing import Any

from loguru import logger

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.interfaces import (
    AchievementRepository,
    TaskRepository,
    UserRepository,
)
from day_play.business.progress_tracker import ProgressTracker
from day_play.models.entities import Achievement

ACHIEVEMENT_DEFINITIONS = [
    Achievement(
        id=None,
        name="Getting Started",
        description="Complete your first task.",
        icon="🏆",
        unlock_criteria={"tasks_completed": 1},
    ),
    Achievement(
        id=None,
        name="Task Master",
        description="Complete 10 tasks.",
        icon="🏅",
        unlock_criteria={"tasks_completed": 10},
    ),
    Achievement(
        id=None,
        name="Century",
        description="Complete 100 tasks.",
        icon="💯",
        unlock_criteria={"tasks_completed": 100},
    ),
    Achievement(
        id=None,
        name="Daily Streak",
        description="Complete tasks 5 days in a row.",
        icon="🔥",
        unlock_criteria={"daily_streak": 5},
    ),
    Achievement(
        id=None,
        name="Week Warrior",
        description="Complete tasks 7 days in a row.",
        icon="⚔️",
        unlock_criteria={"daily_streak": 7},
    ),
    Achievement(
        id=None,
        name="Unstoppable",
        description="Complete tasks 30 days in a row.",
        icon="🚀",
        unlock_criteria={"daily_streak": 30},
    ),
]
class AchievementManager:
    def __init__(
            self, gamification: GamificationEngine,
            task_repository: TaskRepository,
            user_repository: UserRepository,
            achievement_repository: AchievementRepository,
            progress_tracker: ProgressTracker,

            ):
        """Initialize achievement manager with dependencies.

        Args:
            gamification: Engine for XP/level calculations
            task_repository: Repository for task data access
            user_repository: Repository for user data access
            achievement_repository: Repository for achievement data access
        """
        self._gamification = gamification
        self._task_repository = task_repository
        self._user_repository = user_repository
        self._achievement_repository = achievement_repository
        self._progress_tracker = progress_tracker

    def get_achievement_definitions(self) -> list[Achievement]:
        """Get all possible achievements (the catalog).

        Returns achievement templates that can be earned.
        Uses hardcoded definitions for MVP.

        Returns:
            List of all possible achievement definitions
        """
        return ACHIEVEMENT_DEFINITIONS

    def check_and_unlock_achievements(self, user_id: int) -> list[Achievement]:
        """Check and unlock achievements for a user.

        Compares user progress against achievement criteria.
        Creates new achievement records for newly unlocked achievements.
        Only returns newly unlocked achievements (not previously earned ones).

        Args:
            user_id: ID of the user

        Returns:
            List of newly unlocked Achievement objects
            Empty list if user not found or no new achievements
        """
        logger.debug("Checking achievements for user", user_id=user_id)

        user = self._user_repository.get_by_id(user_id)
        if not user:
            logger.warning("User not found, cannot check achievements", user_id=user_id)
            return []

        unlocked_achievements = []

        try:
            all_achievements = self.get_achievement_definitions()

            user_unlocked = self._achievement_repository.get_unlocked(user_id)
            unlocked_names = {ach.name for ach in user_unlocked}
            total_tasks_completed = self._task_repository.count_completed_tasks(user_id)
            daily_streak = self._progress_tracker.calculate_daily_streak(user_id)
            logger.debug(
                "User stats calculated",
                user_id=user_id,
                tasks=total_tasks_completed,
                streak=daily_streak,
            )

            for achievement_def in all_achievements:
                if achievement_def.name in unlocked_names:  # ← Changed: use name instead of id
                    continue
                if self._check_criteria(
                    achievement_def.unlock_criteria,
                    total_tasks_completed,
                    daily_streak,
                ):
                    new_achievement = Achievement(
                        name=achievement_def.name,
                        description=achievement_def.description,
                        icon=achievement_def.icon,
                        unlock_criteria=achievement_def.unlock_criteria,
                        unlocked_at=datetime.now(),
                        user_id=user_id,
                    )

                    saved_achievement = self._achievement_repository.create(new_achievement)
                    unlocked_achievements.append(saved_achievement)

                    logger.info(
                        "Unlocked achievement",
                        user_id=user_id,
                        achievement=achievement_def.name,
                    )

        except Exception as e:
            logger.error(
                "Error checking achievements",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            # Return what we have so far (partial success)
            return unlocked_achievements

        return unlocked_achievements

    def _check_criteria(
        self,
        criteria: dict[str, Any] | None,
        tasks_completed: int,
        daily_streak: int,
    ) -> bool:
        """Check if achievement criteria are met.

        Args:
            criteria: Achievement unlock criteria
            tasks_completed: Total tasks user has completed
            daily_streak: User's current daily streak

        Returns:
            True if all criteria are met, False otherwise
        """
        if not criteria:
            return False

        if "tasks_completed" in criteria:
            if tasks_completed < criteria["tasks_completed"]:
                return False

        if "daily_streak" in criteria:
            if daily_streak < criteria["daily_streak"]:
                return False

        return True

    def get_unlocked_achievements(self, user_id: int) -> list[Achievement]:
        """Get all achievements user has unlocked.

        Args:
            user_id: ID of the user

        Returns:
            List of unlocked achievements for the user
        """
        return self._achievement_repository.get_unlocked(user_id)

    def get_available_achievements(self, user_id: int) -> list[Achievement]:
        """Get achievements user hasn't unlocked yet.

        Args:
            user_id: ID of the user

        Returns:
            List of achievement definitions not yet unlocked
        """
        all_achievements = self.get_achievement_definitions()
        unlocked = self.get_unlocked_achievements(user_id)
        unlocked_names = {ach.name for ach in unlocked}

        return [ach for ach in all_achievements if ach.name not in unlocked_names]
