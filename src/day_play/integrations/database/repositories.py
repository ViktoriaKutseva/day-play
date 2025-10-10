"""SQLModel repository implementation for tasks."""
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime, timezone

from ...models.entities import Task
from ...models.value_objects import TaskCreate, TaskUpdate
from .models import TaskDB


class SQLModelTaskRepository:
    """SQLModel implementation of TaskRepository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    async def get_all(self) -> List[Task]:
        """Get all tasks."""
        statement = select(TaskDB)
        results = self._session.exec(statement).all()
        return [self._db_to_entity(task_db) for task_db in results]
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        task_db = self._session.get(TaskDB, task_id)
        if not task_db:
            return None
        return self._db_to_entity(task_db)
    
    async def create(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        task_db = TaskDB(
            task_name=task_data.task_name,
            completed=task_data.completed,
            due_date=task_data.due_date,
            created_at=datetime.now(timezone.utc)
        )
        self._session.add(task_db)
        self._session.commit()
        self._session.refresh(task_db)
        return self._db_to_entity(task_db)
    
    async def update(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task."""
        task_db = self._session.get(TaskDB, task_id)
        if not task_db:
            return None
        
        # Update only provided fields
        if task_data.task_name is not None:
            task_db.task_name = task_data.task_name
        if task_data.completed is not None:
            task_db.completed = task_data.completed
        if task_data.due_date is not None:
            task_db.due_date = task_data.due_date
        
        self._session.add(task_db)
        self._session.commit()
        self._session.refresh(task_db)
        return self._db_to_entity(task_db)
    
    async def delete(self, task_id: int) -> bool:
        """Delete a task by ID."""
        task_db = self._session.get(TaskDB, task_id)
        if not task_db:
            return False
        
        self._session.delete(task_db)
        self._session.commit()
        return True
    
    @staticmethod
    def _db_to_entity(task_db: TaskDB) -> Task:
        """Convert database model to entity."""
        return Task(
            task_id=task_db.task_id,
            task_name=task_db.task_name,
            completed=task_db.completed,
            due_date=task_db.due_date,
            created_at=task_db.created_at
        )