import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import UTC, datetime, timedelta
from day_play.integrations.database.repositories import SQLAlchemyTaskRepository
from day_play.integrations.database.models import SQLModel
from day_play.models.entities import Task
from day_play.models.enums import TaskStatus, Priority, Urgency

@pytest.fixture
def in_memory_db():
    """Create in-memory database for testing."""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session factory
    SessionLocal = sessionmaker(bind=engine)

    yield SessionLocal

    # Cleanup
    engine.dispose()


@pytest.fixture
def task_repository(in_memory_db):
    """Create repository instance with in-memory database."""
    return SQLAlchemyTaskRepository(in_memory_db)

class TestTaskRepository:
    def test_create_task(self, task_repository):
        task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=1
        )

        created_task = task_repository.create_task(task)

        assert created_task.id is not None  # ID was assigned
        assert created_task.title == "Test Task"
        assert created_task.status == TaskStatus.PENDING

    def test_get_task_by_id(self, task_repository):
        tasks = (
            Task(
            title="Test Task 1",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=1
        ), Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=1)

        )
        created_task_1 = task_repository.create_task(tasks[0])
        created_task_2 = task_repository.create_task(tasks[1])
        get_by_id = task_repository.get_task_by_id(created_task_1.id)
        assert get_by_id is not None
        assert get_by_id.title == 'Test Task 1'
        assert get_by_id.status == TaskStatus.PENDING
        assert get_by_id.id == created_task_1.id
        assert get_by_id.id  != created_task_2.id

    def test_get_by_id_not_found(self, task_repository):
        result = task_repository.get_task_by_id(999999)
        assert result is None

    def test_update_task(self, task_repository):
        task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=1
        )
        created_task = task_repository.create_task(task)
        created_task.title = "Updated Title"
        created_task.status = TaskStatus.COMPLETED
        updated_task = task_repository.update_task(created_task)
        assert updated_task.title == "Updated Title"
        assert updated_task.status == TaskStatus.COMPLETED
        retrieved = task_repository.get_task_by_id(updated_task.id)
        assert retrieved.title == "Updated Title"

    def test_delete_task(self, task_repository):
        task = Task(title = "Test task", description='test task', user_id= 1)
        created_task = task_repository.create_task(task)
        task_repository.delete_task(created_task.id)
        retrieved = task_repository.get_task_by_id(created_task.id)
        assert retrieved is None

    def test_list_tasks(self, task_repository):
        tasks = (
            Task(
            title="Test Task 1",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=2
        ), Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=2),
            Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=2
            )
        )
        task_repository.create_task(tasks[0])
        task_repository.create_task(tasks[1])
        task_repository.create_task(tasks[2])
        result = task_repository.list_tasks(2)

        assert len(result) == 3

    def test_get_tasks_for_today(self, task_repository):
        tasks = (
                Task(
                title="Test Task 1",
                description="Test description",
                priority=Priority.HIGH,
                urgency=Urgency.MEDIUM,
                status=TaskStatus.PENDING,
                user_id=2,
                due_date=datetime.now(UTC)
            ), Task(
                title="Test Task 2",
                description="Test description",
                priority=Priority.HIGH,
                urgency=Urgency.MEDIUM,
                status=TaskStatus.COMPLETED,
                due_date=datetime.now(UTC),
                user_id=2),
                Task(
                title="Test Task 2",
                description="Test description",
                priority=Priority.HIGH,
                urgency=Urgency.MEDIUM,
                status=TaskStatus.PENDING,
                due_date = None,
                user_id=2
                ),
                Task(
                title="Test Task 2",
                description="Test description",
                priority=Priority.HIGH,
                urgency=Urgency.MEDIUM,
                status=TaskStatus.PENDING,
                due_date = datetime(2024, 12, 12),
                user_id=2
                )
        )
        task_repository.create_task(tasks[0])
        task_repository.create_task(tasks[1])
        task_repository.create_task(tasks[2])
        task_repository.create_task(tasks[3])
        results = task_repository.get_tasks_for_today(2)
        assert len(results) == 2

    def test_get_overdue_tasks(self, task_repository):
        past_date = datetime.now(UTC) - timedelta(days=1)
        future_date = datetime.now(UTC) + timedelta(days=1)

        overdue_task = Task(
            title="Overdue Task",
            description= 'task',
            due_date=past_date,
            status=TaskStatus.PENDING,
            user_id=1
        )
        future_task = Task(
            title="Future Task",
            description= 'task',
            due_date=future_date,
            status=TaskStatus.PENDING,
            user_id=1
        )
        completed_overdue = Task(
            title="Completed Overdue",
            description='task',
            due_date=past_date,
            status=TaskStatus.COMPLETED,
            user_id=1
        )

        task_repository.create_task(overdue_task)
        task_repository.create_task(future_task)
        task_repository.create_task(completed_overdue)

        # Act
        overdue_tasks = task_repository.get_overdue_tasks(1)

        # Assert
        assert len(overdue_tasks) == 1  # Only overdue AND not completed
        assert overdue_tasks[0].title == "Overdue Task"

    def test_count_completed_tasks(self, task_repository):
        tasks = (
            Task(
            title="Test Task 1",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=2
        ), Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.COMPLETED,
            user_id=2),
            Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.COMPLETED,
            user_id=2
            )
        )
        for task in tasks:
            task_repository.create_task(task)
        result = task_repository.count_completed_tasks(2)
        assert result == 2

    def test_find_by_status(self, task_repository):
        tasks = (
            Task(
            title="Test Task 1",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=2
        ), Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.COMPLETED,
            user_id=2),
            Task(
            title="Test Task 2",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.IN_PROGRESS,
            user_id=2
            )
        )
        for task in tasks:
            task_repository.create_task(task)
        result_in_progress = task_repository.find_by_status(2, TaskStatus.IN_PROGRESS)
        result_completed = task_repository.find_by_status(2, TaskStatus.COMPLETED)
        result_pending = task_repository.find_by_status(2, TaskStatus.PENDING)
        assert len(result_in_progress) == len(result_completed) == len(result_pending) == 1