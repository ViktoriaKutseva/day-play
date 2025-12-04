from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from day_play.integrations.database.models import Task as TaskORM
from day_play.models.entities import Task as DomainTask
from day_play.models.enums import TaskStatus
from day_play.models.exceptions import TaskNotFoundError

# Note: Pylance reports false positives for SQLAlchemy column comparisons
# (e.g., TaskORM.user_id == user_id). These are valid SQLAlchemy expressions
# that return ColumnElement[bool], not Python bool. Type ignore comments are used.


class SQLAlchemyTaskRepository:
    """SQLAlchemy implementation of TaskRepository protocol."""
    def __init__(self, session: Session):
        self._session = session

    @staticmethod
    def _to_domain(orm_task: TaskORM) -> DomainTask:
        return DomainTask(
            id=orm_task.id,
            title=orm_task.title,
            description=orm_task.description,
            priority=orm_task.priority,
            urgency=orm_task.urgency,
            status=orm_task.status,
            due_date=orm_task.due_date,
            recurrence_pattern=orm_task.recurrence_pattern,
            recurrence_rule_on_complete=orm_task.recurrence_rule_on_complete,
            next_occurrence=orm_task.next_occurrence,
            custom_xp=orm_task.custom_xp,
            created_at=orm_task.created_at,
            updated_at=orm_task.updated_at,
            completed_at=orm_task.completed_at,
            user_id=orm_task.user_id,
        )

    @staticmethod
    def _to_orm(domain_task: DomainTask) -> TaskORM:
        now = datetime.now(timezone.utc)
        return TaskORM(
            id=domain_task.id,
            title=domain_task.title,
            description=domain_task.description,
            priority=domain_task.priority,
            urgency=domain_task.urgency,
            status=domain_task.status,
            due_date=domain_task.due_date,
            recurrence_pattern=domain_task.recurrence_pattern,
            recurrence_rule_on_complete=domain_task.recurrence_rule_on_complete,
            next_occurrence=domain_task.next_occurrence,
            custom_xp=domain_task.custom_xp,
            created_at=domain_task.created_at or now,
            updated_at=domain_task.updated_at or now,
            completed_at=domain_task.completed_at,
            user_id=domain_task.user_id,
        )

    def create_task(self, task: DomainTask) -> DomainTask:
        orm_task = self._to_orm(task)
        self._session.add(orm_task)
        self._session.commit()
        self._session.refresh(orm_task)
        return self._to_domain(orm_task)

    def get_task_by_id(self, task_id: int) -> DomainTask | None:
        orm_task = self._session.get(TaskORM, task_id)
        if orm_task is None:
            return None
        return self._to_domain(orm_task)

    def update_task(self, task: DomainTask) -> DomainTask:
        """
        Update an existing task.

        Steps:
        1. Get existing ORM task from database
        2. Update all fields from domain entity
        3. Update the updated_at timestamp
        4. Commit changes
        5. Convert back to domain entity and return

        Args:
            task: Domain entity with updated data (must have ID)

        Returns:
            Updated task

        Raises:
            ValueError: If task ID is None or task not found
        """
        if task.id is None:
            raise ValueError("Cannot update task without ID")

        orm_task = self._session.get(TaskORM, task.id)

        if orm_task is None:
            raise TaskNotFoundError(f"Task with ID {task.id} not found")

        orm_task.title = task.title
        orm_task.description = task.description
        orm_task.priority = task.priority
        orm_task.urgency = task.urgency
        orm_task.status = task.status
        orm_task.due_date = task.due_date
        orm_task.recurrence_pattern = task.recurrence_pattern
        orm_task.next_occurrence = task.next_occurrence
        orm_task.recurrence_rule_on_complete = task.recurrence_rule_on_complete
        orm_task.custom_xp = task.custom_xp
        orm_task.completed_at = task.completed_at
        orm_task.updated_at = datetime.now(timezone.utc)  # Always update timestamp

        self._session.commit()

        self._session.refresh(orm_task)
        return self._to_domain(orm_task)

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by its ID.

        Steps:
        1. Get task from database
        2. Delete it
        3. Commit changes

        Args:
            task_id: Unique identifier of the task to delete

        Raises:
            ValueError: If task not found
        """
        orm_task = self._session.get(TaskORM, task_id)

        if orm_task is None:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        self._session.delete(orm_task)
        self._session.commit()

    def list_tasks(self, user_id: int) -> list[DomainTask]:
        """
        Get all tasks for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of all tasks for the user
        """
        stmt = select(TaskORM).where(TaskORM.user_id == user_id)  # type: ignore[arg-type]
        orm_tasks = self._session.execute(stmt).scalars().all()

        return [self._to_domain(orm_task) for orm_task in orm_tasks]
    def get_tasks_for_today(self, user_id: int) -> list[DomainTask]:
        """
        Get tasks due today or with no due date for a user.

        This includes:
        - Tasks with due_date = today
        - Tasks with no due_date (None)
        - Only non-completed tasks

        Args:
            user_id: User's unique identifier

        Returns:
            List of today's tasks
        """
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        stmt = select(TaskORM).where(
            TaskORM.user_id == user_id,  # type: ignore[arg-type]
            TaskORM.status != TaskStatus.COMPLETED,  # type: ignore[arg-type]
            (
                (TaskORM.due_date.is_(None))  # type: ignore[union-attr]
                | (
                    (TaskORM.due_date >= today_start)  # type: ignore[operator]
                    & (TaskORM.due_date <= today_end)  # type: ignore[operator]
                )
            ),
        )
        orm_tasks = self._session.execute(stmt).scalars().all()

        return [self._to_domain(orm_task) for orm_task in orm_tasks]

    def get_overdue_tasks(self, user_id: int) -> list[DomainTask]:
        """
        Get overdue tasks (past due date and not completed).

        Args:
            user_id: User's unique identifier

        Returns:
            List of overdue tasks
        """
        now = datetime.now(timezone.utc)

        # Query overdue tasks
        stmt = select(TaskORM).where(
            TaskORM.user_id == user_id,  # type: ignore[arg-type]
            TaskORM.status != TaskStatus.COMPLETED,  # type: ignore[arg-type]
            TaskORM.due_date < now,  # Past due date  # type: ignore[operator]
        )
        orm_tasks = self._session.execute(stmt).scalars().all()

        return [self._to_domain(orm_task) for orm_task in orm_tasks]

    def count_completed_tasks(self, user_id: int) -> int:
        """
        Count the number of completed tasks for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            Number of completed tasks
        """
        stmt = (
            select(func.count())
            .select_from(TaskORM)
            .where(
                TaskORM.user_id == user_id,  # type: ignore[arg-type]
                TaskORM.status == TaskStatus.COMPLETED,  # type: ignore[arg-type]
            )
        )
        count = self._session.execute(stmt).scalar()
        return count or 0

    def find_by_status(self, user_id: int, status: TaskStatus) -> list[DomainTask]:
        stmt = select(TaskORM).where(
            TaskORM.user_id == user_id,  # type: ignore[arg-type]
            TaskORM.status == status,  # type: ignore[arg-type]
        )
        orm_tasks = self._session.execute(stmt).scalars().all()
        return [self._to_domain(orm_task) for orm_task in orm_tasks]

