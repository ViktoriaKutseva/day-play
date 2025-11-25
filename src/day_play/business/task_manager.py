from datetime import UTC, datetime

from loguru import logger

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.interfaces import (
    TaskRepository,
    UserRepository,
)
from day_play.business.recurrence_engine import RecurrenceEngine
from day_play.models.entities import Task
from day_play.models.enums import RecurrencePattern, TaskStatus
from day_play.models.exceptions import (
    TaskAlreadyCompletedError,
    TaskNotCompletedError,
    TaskNotFoundError,
)


class TaskManager:
    """Manages tasks, including creation, updating, and recurrence handling.

    Attributes:
        task_repository (TaskRepository): Repository for task data operations.
        user_repository (UserRepository): Repository for user data operations.
        gamification (GamificationEngine): Engine for handling gamification logic.
        recurrence (RecurrenceEngine): Engine for handling task recurrence logic.
    """

    def __init__(
        self,
        task_repository: TaskRepository,
        user_repository: UserRepository,
        gamification: GamificationEngine,
        recurrence: RecurrenceEngine,
    ) -> None:
        self._task_repository = task_repository
        self._user_repository = user_repository
        self._gamification = gamification
        self._recurrence = recurrence

    def create_task(self, task: Task) -> Task:
        """Creates a new task and handles any initial gamification logic."""
        logger.info(
            "Creating task",
            title=task.title,
            user_id=task.user_id,
            recurrence=task.recurrence_pattern.value,
            priority=task.priority.value,
            urgency=task.urgency.value,
        )

        try:
            task.created_at = datetime.now(UTC)
            task.updated_at = datetime.now(UTC)
            if task.recurrence_pattern != RecurrencePattern.NONE:
                task = self._recurrence.calculate_next_occurrence(task)

            created_task = self._task_repository.create_task(task)
            logger.info(
                "Task created successfully",
                task_id=created_task.id,
                title=created_task.title,
            )
            return created_task
        except Exception as e:
            logger.error(
                "Failed to create task",
                title=task.title,
                user_id=task.user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def get_task(self, task_id: int) -> Task | None:
        """Retrieves a task by its ID."""
        logger.debug("Retrieving task", task_id=task_id)

        try:
            task = self._task_repository.get_task_by_id(task_id)
            if task is None:
                logger.warning("Task not found", task_id=task_id)
                raise TaskNotFoundError(f"Task with ID {task_id} not found")

            logger.debug("Task retrieved", task_id=task.id, title=task.title)
            return task
        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to retrieve task",
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def update_task(self, task: Task) -> Task:
        """Updates an existing task and handles recurrence if applicable."""
        if task.id is None:
            raise ValueError("Task ID is required for update operation")

        logger.info("Updating task", task_id=task.id, title=task.title)

        try:
            existing = self._task_repository.get_task_by_id(task.id)
            if existing is None:
                logger.warning("Cannot update: task not found", task_id=task.id)
                raise TaskNotFoundError(f"Task with ID {task.id} not found")

            if task.recurrence_pattern != existing.recurrence_pattern:
                logger.debug(
                    "Recurrence pattern changed, recalculating",
                    task_id=task.id,
                    old_pattern=existing.recurrence_pattern.value,
                    new_pattern=task.recurrence_pattern.value,
                )
                task = self._recurrence.calculate_next_occurrence(task)

            updated_task = self._task_repository.update_task(task)
            logger.info("Task updated successfully", task_id=updated_task.id)
            return updated_task
        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update task",
                task_id=task.id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def delete_task(self, task_id: int) -> None:
        """Deletes a task by its ID."""
        logger.info("Deleting task", task_id=task_id)

        try:
            existing = self._task_repository.get_task_by_id(task_id)
            if existing is None:
                logger.warning("Cannot delete: task not found", task_id=task_id)
                raise TaskNotFoundError(f"Task with ID {task_id} not found")

            self._task_repository.delete_task(task_id)
            logger.info(
                "Task deleted successfully", task_id=task_id, title=existing.title
            )
        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to delete task",
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def complete_task(self, task_id: int, user_id: int) -> Task:
        """
        Mark a pending task as completed and award XP.

        Business rules:
        - Can only complete a pending/in-progress task
        - Completion timestamp is set to current UTC time
        - XP is calculated and awarded to user
        - User level is recalculated (may increase)
        - Next occurrence is calculated for recurring tasks

        Args:
            task_id: ID of task to complete
            user_id: ID of user completing the task

        Returns:
            Task with completed status

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskAlreadyCompletedError: If task is already completed
        """
        logger.info("Completing task", task_id=task_id, user_id=user_id)

        try:
            task = self._task_repository.get_task_by_id(task_id)
            if task is None:
                logger.warning("Cannot complete: task not found", task_id=task_id)
                raise TaskNotFoundError(f"Task with ID {task_id} not found")

            if task.is_completed():
                logger.warning(
                    "Cannot complete: task already completed",
                    task_id=task_id,
                    completed_at=task.completed_at,
                )
                raise TaskAlreadyCompletedError(f"Task {task_id} is already completed")

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(UTC)
            task.updated_at = datetime.now(UTC)

            xp = self._gamification.calculate_xp(task)
            logger.debug("XP calculated", task_id=task_id, xp_earned=xp)

            user = self._user_repository.update_xp(user_id, xp)
            new_level = self._gamification.calculate_level(user.total_xp)

            if new_level > user.current_level:
                logger.info(
                    "Level up!",
                    user_id=user_id,
                    old_level=user.current_level,
                    new_level=new_level,
                )
                self._user_repository.update_level(user_id, new_level)

            task = self._recurrence.calculate_next_occurrence(task)

            updated_task = self._task_repository.update_task(task)
            logger.info(
                "Task completed successfully",
                task_id=task_id,
                xp_earned=xp,
                user_level=new_level,
                title=updated_task.title,
            )
            return updated_task
        except (TaskNotFoundError, TaskAlreadyCompletedError):
            raise
        except Exception as e:
            logger.error(
                "Failed to complete task",
                task_id=task_id,
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def undo_task(self, task_id: int, user_id: int) -> Task:
        """
        Mark a completed task as pending (undo completion).

        Business rules:
        - Can only undo a completed task
        - Completion timestamp is cleared
        - XP is deducted from user
        - User level is recalculated (may decrease)
        - Next occurrence is cleared

        Args:
            task_id: ID of task to undo
            user_id: ID of user who completed the task

        Returns:
            Task with pending status

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValueError: If task is not completed
        """
        logger.info("Undoing task completion", task_id=task_id, user_id=user_id)

        try:
            task = self._task_repository.get_task_by_id(task_id)
            if task is None:
                logger.warning("Cannot undo: task not found", task_id=task_id)
                raise TaskNotFoundError(f"Task with ID {task_id} not found")

            if not task.is_completed():
                logger.warning(
                    "Cannot undo: task is not completed",
                    task_id=task_id,
                    current_status=task.status.value,
                )
                raise TaskNotCompletedError(
                    f"Task {task_id} is not completed, cannot undo"
                )

            # Calculate XP to deduct
            xp = self._gamification.calculate_xp(task)
            logger.debug("XP to deduct", task_id=task_id, xp_deducted=xp)

            # Revert task status
            task.status = TaskStatus.PENDING
            task.completed_at = None
            task.updated_at = datetime.now(UTC)

            user = self._user_repository.update_xp(user_id, -xp)  # Negative XP

            new_level = self._gamification.calculate_level(user.total_xp)
            if new_level != user.current_level:
                logger.info(
                    "Level changed after undo",
                    user_id=user_id,
                    old_level=user.current_level,
                    new_level=new_level,
                )
                self._user_repository.update_level(user_id, new_level)

            task.next_occurrence = None

            updated_task = self._task_repository.update_task(task)
            logger.info(
                "Task completion undone successfully",
                task_id=task_id,
                xp_deducted=xp,
                user_level=new_level,
                title=updated_task.title,
            )
            return updated_task
        except (TaskNotFoundError, TaskNotCompletedError):
            raise
        except Exception as e:
            logger.error(
                "Failed to undo task completion",
                task_id=task_id,
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def get_tasks(
        self,
        user_id: int,
        status: TaskStatus | None = None,
        overdue_only: bool = False,
    ) -> list[Task]:
        """
        Get tasks for a user with optional filtering.

        Args:
            user_id: ID of user whose tasks to retrieve
            status: Optional status filter (pending/completed)
            overdue_only: If True, only return overdue tasks

        Returns:
            List of tasks matching criteria
        """
        logger.debug(
            "Retrieving tasks",
            user_id=user_id,
            status=status.value if status else None,
            overdue_only=overdue_only,
        )

        try:
            if overdue_only:
                tasks = self._task_repository.get_overdue_tasks(user_id)
                logger.debug(
                    "Retrieved overdue tasks", user_id=user_id, count=len(tasks)
                )
                return tasks

            tasks = self._task_repository.get_by_user_id(user_id)
            if status is not None:
                tasks = [t for t in tasks if t.status == status]

            logger.debug(
                "Retrieved tasks",
                user_id=user_id,
                count=len(tasks),
                filtered_by_status=status.value if status else None,
            )
            return tasks
        except Exception as e:
            logger.error(
                "Failed to retrieve tasks",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def get_tasks_for_today(self, user_id: int) -> list[Task]:
        """
        Get tasks due today or with no due date.

        Args:
            user_id: ID of user whose tasks to retrieve

        Returns:
            List of today's tasks
        """
        logger.debug("Retrieving today's tasks", user_id=user_id)

        try:
            tasks = self._task_repository.get_tasks_for_today(user_id)
            logger.debug("Retrieved today's tasks", user_id=user_id, count=len(tasks))
            return tasks
        except Exception as e:
            logger.error(
                "Failed to retrieve today's tasks",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
