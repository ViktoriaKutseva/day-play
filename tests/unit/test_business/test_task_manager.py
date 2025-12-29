from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.recurrence_engine import RecurrenceEngine
from day_play.business.task_manager import TaskManager
from day_play.business.achievement_manager import AchievementManager
from day_play.models.entities import Task, User
from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency
from day_play.models.exceptions import (
    TaskAlreadyCompletedError,
    TaskNotCompletedError,
    TaskNotFoundError,
)


@pytest.fixture
def mock_task_repository() -> Mock:
    return Mock()


@pytest.fixture
def mock_user_repository() -> Mock:
    return Mock()


@pytest.fixture
def mock_achievement_repository() -> Mock:
    return Mock()


@pytest.fixture
def mock_daily_progress_repository() -> Mock:
    return Mock()


@pytest.fixture
def gamification_engine() -> GamificationEngine:
    return GamificationEngine()


@pytest.fixture
def recurrence_engine() -> RecurrenceEngine:
    return RecurrenceEngine()


@pytest.fixture
def mock_progress_tracker() -> Mock:
    return Mock()


@pytest.fixture
def achievement_manager(
    gamification_engine: GamificationEngine,
    mock_task_repository: Mock,
    mock_user_repository: Mock,
    mock_daily_progress_repository: Mock,
    mock_achievement_repository: Mock,
    mock_progress_tracker: Mock,
) -> AchievementManager:
    return AchievementManager(
        gamification=gamification_engine,
        task_repository=mock_task_repository,
        user_repository=mock_user_repository,
        daily_progress_repository=mock_daily_progress_repository,
        achievement_repository=mock_achievement_repository,
        progress_tracker=mock_progress_tracker,
    )


@pytest.fixture
def task_manager(
    mock_task_repository: Mock,
    mock_user_repository: Mock,
    gamification_engine: GamificationEngine,
    recurrence_engine: RecurrenceEngine,
    achievement_manager: AchievementManager,
    mock_daily_progress_repository: Mock,
) -> TaskManager:
    return TaskManager(
        task_repository=mock_task_repository,
        user_repository=mock_user_repository,
        gamification=gamification_engine,
        recurrence=recurrence_engine,
        achievement_manager=achievement_manager,
        daily_progress_repository=mock_daily_progress_repository,
    )


@pytest.fixture
def sample_task():
    task = Task(
        id=1,
        title="Test Task",
        description="A test task",
        priority=Priority.MEDIUM,
        urgency=Urgency.MEDIUM,
        status=TaskStatus.PENDING,
        user_id=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return task


@pytest.fixture
def sample_user():
    user = User(
        id=1,
        username="testuser",
        current_level=1,
        total_xp=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return user


class TestTaskManagerCreateTask:
    """Test suite for TaskManager create_task method."""

    def test_create_task_success(self, task_manager, mock_task_repository):
        """Test successfully creating a new task."""
        # Arrange
        new_task = Task(
            id=None,
            title="New Task",
            description="A new task",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            user_id=1,
        )

        # Mock returns the task it receives with an ID added
        def create_task_side_effect(task):
            return task.model_copy(update={"id": 1})

        mock_task_repository.create_task.side_effect = create_task_side_effect

        # Act
        result = task_manager.create_task(new_task)

        # Assert
        assert result.id == 1
        assert result.title == "New Task"
        assert result.description == "A new task"
        assert result.priority == Priority.HIGH
        assert result.urgency == Urgency.HIGH
        assert result.created_at is not None
        assert result.updated_at is not None
        mock_task_repository.create_task.assert_called_once()

        called_task = mock_task_repository.create_task.call_args[0][0]
        assert called_task.created_at is not None
        assert called_task.updated_at is not None

    def test_create_task_sets_timestamps(
        self, task_manager, mock_task_repository, sample_task
    ):
        """Test that creating a task sets creation and update timestamps."""
        # Arrange
        sample_task.created_at = None
        sample_task.updated_at = None
        mock_task_repository.create_task.return_value = sample_task

        # Act
        result = task_manager.create_task(sample_task)

        # Assert
        assert result.created_at is not None
        assert result.updated_at is not None
        mock_task_repository.create_task.assert_called_once()

    def test_create_recurring_task_calculates_next_occurrence(
        self, task_manager, mock_task_repository
    ):
        """Test that creating a recurring task calculates initial next_occurrence."""
        # Arrange
        recurring_task = Task(
            title="Daily Task",
            description="A daily recurring task",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        mock_task_repository.create_task.return_value = recurring_task.model_copy(
            update={"id": 1}
        )

        # Act
        task_manager.create_task(recurring_task)

        # Assert
        called_task = mock_task_repository.create_task.call_args[0][0]
        assert called_task.next_occurrence is not None
        mock_task_repository.create_task.assert_called_once()


class TestTaskManagerGetTask:
    def test_get_task_success(self, task_manager, mock_task_repository):
        new_task = Task(
            id=1,
            title="Daily Task",
            description="A daily recurring task",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        mock_task_repository.get_task_by_id.return_value = new_task
        result = task_manager.get_task(1)
        assert result is not None
        assert result.title == "Daily Task"
        assert result.id == 1
        mock_task_repository.get_task_by_id.assert_called_once_with(1)

    def test_get_task_not_found_raises_error(self, task_manager, mock_task_repository):
        mock_task_repository.get_task_by_id.return_value = None
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task(999)
        mock_task_repository.get_task_by_id.assert_called_once_with(999)


class TestTaskManagerUpdateTask:
    def test_update_task_success(self, task_manager, mock_task_repository):
        existing_task = Task(
            id=1,
            title="Daily Task",
            description="A daily recurring task",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        updated_task = Task(
            id=1,
            title="Daily Task updated",
            description="A daily recurring task updated",
            priority=Priority.HIGH,
            urgency=Urgency.LOW,
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        mock_task_repository.get_task_by_id.return_value = existing_task
        mock_task_repository.update_task.return_value = updated_task
        result = task_manager.update_task(updated_task)

        assert result.title == "Daily Task updated"
        assert result.priority == Priority.HIGH
        assert result.urgency == Urgency.LOW
        assert result.id == 1
        mock_task_repository.get_task_by_id.assert_called_once_with(1)
        mock_task_repository.update_task.assert_called_once()

    def test_update_task_recurrence_changed_calculates_next_occurrence(
        self, task_manager, mock_task_repository
    ):
        existing_task = Task(
            id=1,
            title="Task",
            description="Task description",
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        updated_task = Task(
            id=1,
            title="Task",
            description="Task description",
            recurrence_pattern=RecurrencePattern.WEEKLY,
            user_id=1,
        )
        mock_task_repository.get_task_by_id.return_value = existing_task
        mock_task_repository.update_task.return_value = updated_task
        task_manager.update_task(updated_task)

        mock_task_repository.update_task.assert_called_once()

        called_task = mock_task_repository.update_task.call_args[0][0]
        assert called_task.next_occurrence is not None

    def test_update_task_not_found_raises_error(
        self, task_manager, mock_task_repository
    ):
        # ARRANGE
        # 1. Create a task to update (with non-existent ID)
        task_to_update = Task(
            id=999,  # This ID doesn't exist
            title="Updated Title",
            description="Update description",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            user_id=1,
        )

        mock_task_repository.get_task_by_id.return_value = None
        with pytest.raises(TaskNotFoundError):
            task_manager.update_task(task_to_update)
        mock_task_repository.get_task_by_id.assert_called_once_with(999)

        mock_task_repository.update_task.assert_not_called()


class TestTaskManagerDeleteTask:
    def test_delete_task_success(self, task_manager, mock_task_repository):
        task_to_delete = Task(
            id=1,
            title="Daily Task",
            description="A daily recurring task",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        mock_task_repository.get_task_by_id.return_value = task_to_delete
        result = task_manager.delete_task(1)
        assert result is None
        mock_task_repository.get_task_by_id.assert_called_once_with(1)
        mock_task_repository.delete_task.assert_called_once_with(1)

    def test_delete_task_not_found_raises_error(
        self, task_manager, mock_task_repository
    ):
        non_existent_task_id = 999
        mock_task_repository.get_task_by_id.return_value = None
        with pytest.raises(TaskNotFoundError):
            task_manager.delete_task(non_existent_task_id)
        mock_task_repository.get_task_by_id.assert_called_once_with(
            non_existent_task_id
        )

        mock_task_repository.delete_task.assert_not_called()


class TestTaskManagerCompleteTask:
    def test_complete_task_awards_xp(
        self, task_manager, mock_task_repository, mock_user_repository, mock_daily_progress_repository
    ):
        task = Task(
            id=1,
            title="Complete Me",
            description="Task to be completed",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            user_id=1,
        )
        user = User(id=1, username="testuser", current_level=1, total_xp=0)
        mock_user_repository.update_xp.return_value = user
        mock_task_repository.get_task_by_id.return_value = task
        mock_task_repository.update_task.return_value = task.model_copy(
            update={"status": TaskStatus.COMPLETED}
        )
        mock_task_repository.get_tasks_for_today.return_value = [task]
        mock_daily_progress_repository.create_or_update_progress.return_value = None
        completed_task, achievements = task_manager.complete_task(task.id, user.id)
        assert completed_task.status == TaskStatus.COMPLETED
        assert isinstance(achievements, list)
        mock_user_repository.update_xp.assert_called_once_with(user.id, 50)
        mock_task_repository.get_task_by_id.assert_called_once_with(task.id)
        # update_task is called twice: once to complete, once for recurrence
        assert mock_task_repository.update_task.call_count == 2
        # Level should not update since 50 XP is not enough for level 2 (requires 100 XP)
        mock_user_repository.update_level.assert_not_called()

    def test_complete_task_updates_level_when_threshold_crossed(
        self, task_manager, mock_task_repository, mock_user_repository, mock_daily_progress_repository
    ):
        task = Task(
            id=1,
            title="Complete Me",
            description="Task to be completed",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            user_id=1,
        )
        user = User(id=1, username="testuser", current_level=1, total_xp=90)
        user = User(id=1, username="testuser", current_level=1, total_xp=0)
        mock_user_repository.update_xp.return_value = user
        mock_task_repository.get_task_by_id.return_value = task
        mock_task_repository.update_task.return_value = task.model_copy(
            update={"status": TaskStatus.COMPLETED}
        )
        mock_task_repository.get_tasks_for_today.return_value = [task]
        mock_daily_progress_repository.create_or_update_progress.return_value = None
        completed_task, achievements = task_manager.complete_task(task.id, user.id)
        assert completed_task.status == TaskStatus.COMPLETED
        assert isinstance(achievements, list)
        mock_user_repository.update_xp.assert_called_once_with(user.id, 50)
        mock_task_repository.get_task_by_id.assert_called_once_with(task.id)
        # update_task is called twice: once to complete, once for recurrence
        assert mock_task_repository.update_task.call_count == 2
        # Level should not update since 50 XP is not enough for level 2 (requires 100 XP)
        mock_user_repository.update_level.assert_not_called()

    def test_complete_task_calculates_next_occurrence_for_recurring(
        self, task_manager, mock_task_repository, mock_user_repository, mock_daily_progress_repository
    ):
        task = Task(
            id=1,
            title="Recurring Task",
            description="A recurring task",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            recurrence_pattern=RecurrencePattern.DAILY,
            user_id=1,
        )
        user = User(id=1, username="testuser", current_level=1, total_xp=30)
        mock_task_repository.get_task_by_id.return_value = task
        mock_task_repository.update_task.return_value = task.model_copy(
            update={"status": TaskStatus.COMPLETED}
        )
        mock_user_repository.update_xp.return_value = user
        mock_task_repository.get_tasks_for_today.return_value = [task]
        mock_daily_progress_repository.create_or_update_progress.return_value = None
        completed_task, achievements = task_manager.complete_task(task.id, task.user_id)
        assert completed_task.status == TaskStatus.COMPLETED
        assert isinstance(achievements, list)
        mock_task_repository.get_task_by_id.assert_called_once_with(task.id)
        # update_task is called twice: once to complete, once for recurrence
        assert mock_task_repository.update_task.call_count == 2

        called_task = mock_task_repository.update_task.call_args[0][0]
        assert called_task.next_occurrence is not None

    def test_complete_task_already_completed_raises_error(
        self, task_manager, mock_task_repository
    ):
        task = Task(
            id=1,
            title="Already Completed Task",
            description="This task is already completed",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.COMPLETED,
            user_id=1,
        )
        mock_task_repository.get_task_by_id.return_value = task
        with pytest.raises(TaskAlreadyCompletedError):
            task_manager.complete_task(task.id, task.user_id)
        mock_task_repository.get_task_by_id.assert_called_once_with(task.id)


class TestTaskManagerUndoTask:
    """Test suite for TaskManager undo_task method."""

    def test_undo_task_success(
        self, task_manager, mock_task_repository, mock_user_repository, mock_daily_progress_repository
    ):
        """Test successfully undoing a completed task."""
        completed_task = Task(
            id=1,
            title="Completed Task",
            description="Task to undo",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(UTC),
            user_id=1,
        )
        user = User(id=1, username="testuser", current_level=2, total_xp=100)

        mock_task_repository.get_task_by_id.return_value = completed_task
        mock_task_repository.update_task.return_value = completed_task.model_copy(
            update={"status": TaskStatus.PENDING, "completed_at": None}
        )
        mock_user_repository.update_xp.return_value = user.model_copy(
            update={"total_xp": 50}
        )
        mock_task_repository.get_tasks_for_today.return_value = []
        mock_daily_progress_repository.create_or_update_progress.return_value = None

        result = task_manager.undo_task(completed_task.id, user.id)

        assert result.status == TaskStatus.PENDING
        assert result.completed_at is None
        mock_task_repository.get_task_by_id.assert_called_once_with(completed_task.id)
        mock_user_repository.update_xp.assert_called_once()
        mock_task_repository.update_task.assert_called_once()

    def test_undo_task_not_found_raises_error(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test undoing a non-existent task raises error."""
        mock_task_repository.get_task_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            task_manager.undo_task(999, 1)

        mock_task_repository.get_task_by_id.assert_called_once_with(999)
        mock_task_repository.update_task.assert_not_called()

    def test_undo_task_not_completed_raises_error(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test undoing a non-completed task raises error."""
        pending_task = Task(
            id=1,
            title="Pending Task",
            description="Not completed yet",
            priority=Priority.MEDIUM,
            urgency=Urgency.MEDIUM,
            status=TaskStatus.PENDING,
            user_id=1,
        )
        mock_task_repository.get_task_by_id.return_value = pending_task

        with pytest.raises(TaskNotCompletedError):
            task_manager.undo_task(pending_task.id, pending_task.user_id)

        mock_task_repository.get_task_by_id.assert_called_once_with(pending_task.id)
        mock_task_repository.update_task.assert_not_called()

    def test_undo_task_updates_level_when_xp_decreased(
        self, task_manager, mock_task_repository, mock_user_repository, mock_daily_progress_repository
    ):
        """Test that undoing a task recalculates user level."""
        completed_task = Task(
            id=1,
            title="High XP Task",
            description="Task worth lots of XP",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(UTC),
            user_id=1,
        )
        # User at level 2 with 100 XP, will drop to level 1 after losing 50 XP
        user = User(id=1, username="testuser", current_level=2, total_xp=100)
        updated_user = user.model_copy(update={"total_xp": 50})

        mock_task_repository.get_task_by_id.return_value = completed_task
        mock_task_repository.update_task.return_value = completed_task.model_copy(
            update={"status": TaskStatus.PENDING, "completed_at": None}
        )
        mock_user_repository.update_xp.return_value = updated_user
        mock_task_repository.get_tasks_for_today.return_value = []
        mock_daily_progress_repository.create_or_update_progress.return_value = None

        task_manager.undo_task(completed_task.id, user.id)

        mock_user_repository.update_level.assert_called_once()


class TestTaskManagerGetTasks:
    """Test suite for TaskManager get_tasks method."""

    def test_get_tasks_all_for_user(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test retrieving all tasks for a user."""
        tasks = [
            Task(
                id=1,
                title="Task 1",
                description="First task",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
            Task(
                id=2,
                title="Task 2",
                description="Second task",
                user_id=1,
                status=TaskStatus.COMPLETED,
            ),
            Task(
                id=3,
                title="Task 3",
                description="Third task",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
        ]
        mock_task_repository.list_tasks.return_value = tasks

        result = task_manager.get_tasks(user_id=1)

        assert len(result) == 3
        assert result == tasks
        mock_task_repository.list_tasks.assert_called_once_with(1)

    def test_get_tasks_filtered_by_status(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test retrieving tasks filtered by status."""
        all_tasks = [
            Task(
                id=1,
                title="Task 1",
                description="First task",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
            Task(
                id=2,
                title="Task 2",
                description="Second task",
                user_id=1,
                status=TaskStatus.COMPLETED,
            ),
            Task(
                id=3,
                title="Task 3",
                description="Third task",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
        ]
        mock_task_repository.list_tasks.return_value = all_tasks

        result = task_manager.get_tasks(user_id=1, status=TaskStatus.PENDING)

        assert len(result) == 2
        assert all(t.status == TaskStatus.PENDING for t in result)
        mock_task_repository.list_tasks.assert_called_once_with(1)

    def test_get_tasks_overdue_only(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test retrieving only overdue tasks."""
        overdue_tasks = [
            Task(
                id=1,
                title="Overdue 1",
                description="First overdue",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
            Task(
                id=2,
                title="Overdue 2",
                description="Second overdue",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
        ]
        mock_task_repository.get_overdue_tasks.return_value = overdue_tasks

        result = task_manager.get_tasks(user_id=1, overdue_only=True)

        assert len(result) == 2
        assert result == overdue_tasks
        mock_task_repository.get_overdue_tasks.assert_called_once_with(1)
        mock_task_repository.get_by_user_id.assert_not_called()


class TestTaskManagerGetTasksForToday:
    """Test suite for TaskManager get_tasks_for_today method."""

    def test_get_tasks_for_today_success(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test retrieving today's tasks."""
        today_tasks = [
            Task(
                id=1,
                title="Today 1",
                description="First today task",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
            Task(
                id=2,
                title="Today 2",
                description="Second today task",
                user_id=1,
                status=TaskStatus.PENDING,
            ),
            Task(
                id=3,
                title="Today 3",
                description="Third today task",
                user_id=1,
                status=TaskStatus.COMPLETED,
            ),
        ]
        mock_task_repository.get_tasks_for_today.return_value = today_tasks

        result = task_manager.get_tasks_for_today(user_id=1)

        assert len(result) == 3
        assert result == today_tasks
        mock_task_repository.get_tasks_for_today.assert_called_once_with(1)

    def test_get_tasks_for_today_empty(
        self, task_manager, mock_task_repository, mock_user_repository
    ):
        """Test retrieving today's tasks when there are none."""
        mock_task_repository.get_tasks_for_today.return_value = []

        result = task_manager.get_tasks_for_today(user_id=1)

        assert len(result) == 0
        assert result == []
        mock_task_repository.get_tasks_for_today.assert_called_once_with(1)


class TestTaskManagerRepositoryExceptions:
    """Repository exception propagation tests for TaskManager public methods."""

    def test_create_task_repository_exception_propagates(self, task_manager, mock_task_repository, sample_task):
        mock_task_repository.create_task.side_effect = Exception("Database error")
        sample_task.id = None
        with pytest.raises(Exception, match="Database error"):
            task_manager.create_task(sample_task)

    def test_get_task_repository_exception_propagates(self, task_manager, mock_task_repository):
        mock_task_repository.get_task_by_id.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.get_task(1)

    def test_update_task_repository_exception_propagates(self, task_manager, mock_task_repository):
        existing_task = Task(id=1, title="Task", description="desc", priority=Priority.HIGH, urgency=Urgency.HIGH, user_id=1)
        mock_task_repository.get_task_by_id.return_value = existing_task
        mock_task_repository.update_task.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.update_task(existing_task)

    def test_delete_task_repository_exception_propagates(self, task_manager, mock_task_repository):
        task_to_delete = Task(id=1, title="Task", description="desc", priority=Priority.HIGH, urgency=Urgency.HIGH, user_id=1)
        mock_task_repository.get_task_by_id.return_value = task_to_delete
        mock_task_repository.delete_task.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.delete_task(1)

    def test_complete_task_repository_exception_propagates(self, task_manager, mock_task_repository, mock_user_repository):
        task = Task(id=1, title="Task", description="desc", priority=Priority.HIGH, urgency=Urgency.HIGH, user_id=1)
        mock_task_repository.get_task_by_id.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.complete_task(task.id, task.user_id)

    def test_undo_task_repository_exception_propagates(self, task_manager, mock_task_repository, mock_user_repository):
        completed_task = Task(id=1, title="Task", description="desc", priority=Priority.HIGH, urgency=Urgency.HIGH, status=TaskStatus.COMPLETED, user_id=1)
        mock_task_repository.get_task_by_id.return_value = completed_task
        # The undo flow calls update_xp before update_task; raise on update_xp to simulate repo failure
        mock_user_repository.update_xp.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.undo_task(completed_task.id, completed_task.user_id)

    def test_get_tasks_repository_exception_propagates(self, task_manager, mock_task_repository):
        mock_task_repository.list_tasks.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.get_tasks(user_id=1)

    def test_get_tasks_for_today_repository_exception_propagates(self, task_manager, mock_task_repository):
        mock_task_repository.get_tasks_for_today.side_effect = Exception("Database error")
        with pytest.raises(Exception, match="Database error"):
            task_manager.get_tasks_for_today(user_id=1)
