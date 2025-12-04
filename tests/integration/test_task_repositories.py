import random
from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from day_play.integrations.database.repositories.task_repository import (
    SQLAlchemyTaskRepository,
)
from day_play.models.entities import Task
from day_play.models.enums import Priority, TaskStatus, Urgency
from day_play.models.exceptions import TaskNotFoundError


@pytest.fixture
def task_repository(in_memory_db):
    return SQLAlchemyTaskRepository(in_memory_db)

def sample_tasks(number: int = 1):
    fake = Faker()
    tasks = []
    for _ in range(number):
        task = Task(
            title=fake.name_female(),
            description=fake.name_male(),
            priority=random.choice(list(Priority)),
            urgency=random.choice(list(Urgency)),
            status=random.choice(list(TaskStatus)),
            user_id=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),)
        tasks.append(task)
    return tasks

class TestTaskRepository:
    def test_create_task(self, task_repository):
        task = sample_tasks(1)[0]
        task.status = TaskStatus.PENDING
        task.title = "Test Task"
        created_task = task_repository.create_task(task)

        assert created_task.title == "Test Task"
        assert created_task.id is not None
        assert created_task.status == TaskStatus.PENDING

    def test_get_task_by_id(self, task_repository):
        tasks = sample_tasks(2)
        created_task_1 = task_repository.create_task(tasks[0])
        created_task_2 = task_repository.create_task(tasks[1])
        get_by_id = task_repository.get_task_by_id(created_task_1.id)
        assert get_by_id is not None
        assert get_by_id.id == created_task_1.id
        assert get_by_id.id  != created_task_2.id

    def test_get_by_id_not_found(self, task_repository):
        result = task_repository.get_task_by_id(999999)
        assert result is None

    def test_update_task(self, task_repository):
        task = sample_tasks(1)[0]
        created_task = task_repository.create_task(task)
        created_task.title = "Updated Title"
        created_task.status = TaskStatus.COMPLETED
        updated_task = task_repository.update_task(created_task)
        assert updated_task.title == "Updated Title"
        assert updated_task.status == TaskStatus.COMPLETED
        retrieved = task_repository.get_task_by_id(updated_task.id)
        assert retrieved.title == "Updated Title"

    def test_delete_task(self, task_repository):
        task = sample_tasks(1)[0]
        created_task = task_repository.create_task(task)
        task_repository.delete_task(created_task.id)
        retrieved = task_repository.get_task_by_id(created_task.id)
        assert retrieved is None

    def test_list_tasks(self, task_repository):
        tasks = sample_tasks(3)
        for task in tasks[:2]:
            task.user_id = 1
            task_repository.create_task(task)
        result = task_repository.list_tasks(1)

        assert len(result) == 2

    def test_get_tasks_for_today(self, task_repository):
        tasks = sample_tasks(5)

        for task in tasks:
            task.status = TaskStatus.PENDING

        tasks[0].due_date = datetime.now(UTC)
        tasks[1].due_date = datetime.now(UTC)
        tasks[2].due_date = datetime.now(UTC) + timedelta(days=2)
        tasks[3].due_date = None
        tasks[4].due_date = datetime.now(UTC) - timedelta(days=1)

        for task in tasks:
            task_repository.create_task(task)

        results = task_repository.get_tasks_for_today(1)
        assert len(results) == 3 

    def test_get_overdue_tasks(self, task_repository):
        past_date = datetime.now(UTC) - timedelta(days=1)
        future_date = datetime.now(UTC) + timedelta(days=1)

        tasks = sample_tasks(3)

        overdue_task = tasks[0]
        overdue_task.due_date = past_date
        overdue_task.status = TaskStatus.PENDING

        future_task = tasks[1]
        future_task.due_date = future_date
        future_task.status = TaskStatus.PENDING

        completed_overdue = tasks[2]
        completed_overdue.due_date = past_date
        completed_overdue.status = TaskStatus.COMPLETED

        task_repository.create_task(overdue_task)
        task_repository.create_task(future_task)
        task_repository.create_task(completed_overdue)

        overdue_tasks = task_repository.get_overdue_tasks(1)

        assert len(overdue_tasks) == 1

    def test_count_completed_tasks(self, task_repository):
        tasks = sample_tasks(4)
        for i, task in enumerate(tasks):
            task.user_id = 2
            task.status = TaskStatus.COMPLETED if i < 2 else TaskStatus.PENDING
        for task in tasks:
            task_repository.create_task(task)
        result = task_repository.count_completed_tasks(2)
        assert result == 2

    def test_find_by_status(self, task_repository):
        tasks = sample_tasks(3)
        tasks[0].status = TaskStatus.IN_PROGRESS
        tasks[1].status = TaskStatus.COMPLETED
        tasks[2].status = TaskStatus.PENDING
        for task in tasks:
            task_repository.create_task(task)
        result_in_progress = task_repository.find_by_status(1, TaskStatus.IN_PROGRESS)
        result_completed = task_repository.find_by_status(1, TaskStatus.COMPLETED)
        result_pending = task_repository.find_by_status(1, TaskStatus.PENDING)
        assert len(result_in_progress) == len(result_completed) == len(result_pending) == 1

    def test_update_task_not_found(self, task_repository):
        task = sample_tasks(1)[0]
        task.id = 9999
        with pytest.raises(TaskNotFoundError):
            task_repository.update_task(task)

    def test_delete_task_not_found(self, task_repository):
        with pytest.raises(TaskNotFoundError):
            task_repository.delete_task(9999)

    