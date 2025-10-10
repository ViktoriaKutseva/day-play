"""Database integrations for task management."""
from typing import Optional
from sqlmodel import Session, select, create_engine
from sqlalchemy.orm import sessionmaker

from ...business.interfaces import TaskRepository
from ...models.entities import Task, TaskUpdate


class SQLiteTaskRepository(TaskRepository):
    """SQLite implementation of TaskRepository."""

    def __init__(self, database_url: str) -> None:
        """Initialize the repository with database connection."""
        self._engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self._session_factory = sessionmaker(bind=self._engine, class_=Session)

    def _get_session(self) -> Session:
        """Get a database session."""
        return self._session_factory()

    async def save(self, task: Task) -> None:
        """Save a task to the database."""
        with self._get_session() as session:
            session.add(task)
            session.commit()
            session.refresh(task)

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        with self._get_session() as session:
            return session.get(Task, task_id)

    async def get_all(self) -> list[Task]:
        """Get all tasks."""
        with self._get_session() as session:
            return list(session.exec(select(Task)).all())

    async def update(self, task_id: int, updates: TaskUpdate) -> Optional[Task]:
        """Update a task with the given updates."""
        with self._get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None

            # Apply updates
            update_data = updates.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    async def delete(self, task_id: int) -> bool:
        """Delete a task by its ID. Returns True if deleted, False if not found."""
        with self._get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return False

            session.delete(task)
            session.commit()
            return True

    def create_tables(self) -> None:
        """Create database tables."""
        Task.metadata.create_all(self._engine)

    def seed_initial_data(self) -> None:
        """Seed initial data for development."""
        from datetime import datetime, timezone

        with self._get_session() as session:
            if not session.exec(select(Task)).first():
                session.add_all([
                    Task(task_name="Sample Task 1", due_date=datetime(2025, 10, 1, tzinfo=timezone.utc)),
                    Task(task_name="Sample Task 2", due_date=datetime(2025, 10, 1, tzinfo=timezone.utc)),
                    Task(task_name="Sample Task 3", due_date=datetime(2025, 10, 1, tzinfo=timezone.utc))
                ])
                session.commit()