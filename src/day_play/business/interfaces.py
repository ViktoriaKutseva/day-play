from datetime import date
from typing import Protocol

from day_play.models.entities import Achievement, DailyProgress, Prize, Task, User


class TaskRepository(Protocol):
    def create_task(self, task: Task) -> Task:
        """Create a new task.
        Args:
            task: Task entity to create (without ID)

        Returns:
            Created task with assigned ID
        """
        ...
    def get_task_by_id(self, task_id: int) -> Task | None:
        """Retrieve a task by its ID.
        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task with the given ID or None if not found
        """
        ...

    def update_task(self, task: Task) -> Task:
        """Update an existing task.
        Args:
            task: Task entity with updated data (must include ID)

        Returns:
            Updated task
        """
        ...

    def delete_task(self, task_id: int) -> None:
        """Delete a task by its ID.
        Args:
            task_id: ID of the task to delete
        """
        ...

    def list_tasks(self, user_id: int) -> list[Task]:
        """List all tasks for a given user.
        Args:
            user_id: ID of the user whose tasks to list

        Returns:
            List of tasks for the given user
        """
        ...
    def get_tasks_for_today(self, user_id: int) -> list[Task]:
        """Get tasks for the current day for a given user.
        Args:
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of tasks for the current day for the given user
        """
        ...
    def get_overdue_tasks(self, user_id: int) -> list[Task]:
        """Get overdue tasks for a given user.
        Args:
            user_id: ID of the user whose overdue tasks to retrieve
        Returns:
            List of overdue tasks for the given user
        """
        ...
    def get_by_user_id(self, user_id: int) -> list[Task]:
        """Get all tasks for a given user.
        Args:
            user_id: ID of the user whose tasks to retrieve
        Returns:
            List of tasks for the given user
        """
        ...
    def count_completed_tasks(self, user_id: int) -> int:
        """Count the number of completed tasks for a given user.
        Args:
            user_id: ID of the user whose completed tasks to count
        Returns:
            Number of completed tasks for the given user
        """
        ...
class DailyProgressRepository(Protocol):
    def create_or_update_progress(self, progress: DailyProgress) -> DailyProgress:
        """Create or update daily progress for a user.
        Args:
            progress: DailyProgress entity to create or update
        Returns:
            Created or updated DailyProgress
        """
        ...
    def get_progress_by_date(self, user_id: int, date_progress: date) -> DailyProgress | None:
        """Retrieve daily progress for a user by date.
        Args:
            user_id: ID of the user
            date_progress: Date of the progress to retrieve
        Returns:
            DailyProgress for the given user and date, or None if not found
        """
        ...
    def get_date_range(self, user_id: int, start_date: date, end_date: date) -> list[DailyProgress]:
        """Retrieve daily progress for a user within a date range.
        Args:
            user_id: ID of the user
            start_date: Start date of the range
            end_date: End date of the range
        Returns:
            List of DailyProgress entries for the given user within the date range
        """
        ...

class AllProgressRepository(Protocol):
    """Interface for progress data access operations."""

    def create(self, progress: DailyProgress) -> DailyProgress:
        """Create a new progress entry."""
        ...

    def get_by_id(self, progress_id: int) -> DailyProgress | None:
        """Get progress by ID."""
        ...

    def get_by_user_id_and_date(self, user_id: int, progress_date: date) -> DailyProgress | None:
        """
        Get progress for a user on a specific date.

        Args:
            user_id: User's unique identifier
            progress_date: Date of the progress entry

        Returns:
            DailyProgress entry or None if not found
        """
        ...

    def update(self, progress: DailyProgress) -> DailyProgress:
        """Update existing daily progress entry."""
        ...

class UserRepository(Protocol):
    """Interface for user data access operations."""

    def create(self, user: User) -> User:
        """Create a new user."""
        ...

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        ...

    def update(self, user: User) -> User:
        """Update existing user."""
        ...

    def update_xp(self, user_id: int, xp_delta: int) -> User:
        """
        Update user's total XP.

        Args:
            user_id: User's unique identifier
            xp_delta: XP amount to add (can be negative for deductions)

        Returns:
            Updated user
        """
        ...

    def update_level(self, user_id: int, new_level: int) -> User:
        """
        Update user's level.

        Args:
            user_id: User's unique identifier
            new_level: New level value

        Returns:
            Updated user
        """
        ...

class AchievementRepository(Protocol):
    """Interface for achievement data access operations."""

    def create(self, achievement: Achievement) -> Achievement:
        """Create a new achievement."""
        ...

    def get_by_id(self, achievement_id: int) -> Achievement | None:
        """Get achievement by ID."""
        ...

    def get_by_user_id(self, user_id: int) -> list[Achievement]:
        """Get all achievements for a user."""
        ...

    def get_unlocked(self, user_id: int) -> list[Achievement]:
        """
        Get unlocked achievements for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of unlocked achievements
        """
        ...

class PrizeRepository(Protocol):
    """Interface for prize data access operations."""

    def create(self, prize: Prize) -> Prize:
        """Create a new prize."""
        ...

    def get_by_id(self, prize_id: int) -> Prize | None:
        """Get prize by ID."""
        ...

    def get_by_user_id(self, user_id: int) -> list[Prize]:
        """Get all prizes for a user."""
        ...

    def get_available(self, user_id: int) -> list[Prize]:
        """
        Get available (not redeemed) prizes for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of available prizes
        """
        ...

    def get_redeemed(self, user_id: int) -> list[Prize]:
        """
        Get redeemed prizes for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of redeemed prizes
        """
        ...

    def update(self, prize: Prize) -> Prize:
        """Update existing prize."""
        ...
