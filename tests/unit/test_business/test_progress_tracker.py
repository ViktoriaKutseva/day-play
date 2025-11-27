import random
from datetime import UTC, datetime, timezone, date, timedelta
from unittest.mock import Mock

import pytest
from faker import Faker

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.progress_tracker import ProgressTracker
from day_play.models.entities import Task, User, DailyProgress
from day_play.models.enums import Priority, TaskStatus, Urgency


@pytest.fixture
def mock_task_repository() -> Mock:
    return Mock()

@pytest.fixture
def mock_user_repository() -> Mock:
    return Mock()

@pytest.fixture
def mock_daily_progress_repository() -> Mock:
    return Mock()

@pytest.fixture
def get_tasks_for_today() -> Mock:
    return Mock()

@pytest.fixture
def get_by_id() -> Mock:
    return Mock()

@pytest.fixture
def gamification_engine() -> GamificationEngine:
    return GamificationEngine()


@pytest.fixture
def progress_tracker(
    mock_task_repository: Mock,
    mock_user_repository: Mock,
    mock_daily_progress_repository: Mock,
    gamification_engine: GamificationEngine,
) -> ProgressTracker:
    return ProgressTracker(
        task_repository=mock_task_repository,
        user_repository=mock_user_repository,
        daily_progress_repository=mock_daily_progress_repository,
        gamification=gamification_engine
    )

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
@pytest.fixture
def sample_progress():

    today = date.today()
    sample_progress = [
        DailyProgress(
            user_id=1,
            date=today,
            tasks_completed=5,
            tasks_total=10,
            daily_xp_earned=50,
            completion_percentage=50.0
        ),
        DailyProgress(
            user_id=1,
            date=today - timedelta(days=1),
            tasks_completed=8,
            tasks_total=10,
            daily_xp_earned=80,
            completion_percentage=80.0
        ),
    ]
    return sample_progress

class TestProgressTracker:
    def test_daily_progression_with_no_tasks(
        self, progress_tracker, mock_task_repository):

        mock_task_repository.get_tasks_for_today.return_value = []

        result = progress_tracker.calculate_daily_progression(user_id=1)

        assert result == 0.0

        mock_task_repository.get_tasks_for_today.assert_called_once_with(1)

    def test_daily_progression_with_partial_completion(self, progress_tracker,mock_task_repository):

        tasks = sample_tasks(4)
        for task in tasks[:2]:
            task.status = TaskStatus.COMPLETED
        for task in tasks[2:]:
            task.status = TaskStatus.PENDING
        print(tasks)
        mock_task_repository.get_tasks_for_today.return_value = tasks
        result = progress_tracker.calculate_daily_progression(user_id=1)
        assert result == 50.0

    def test_daily_progression_with_full_completion(self, progress_tracker,mock_task_repository):

        tasks = sample_tasks(5)
        for task in tasks:
            task.status = TaskStatus.COMPLETED
        mock_task_repository.get_tasks_for_today.return_value = tasks
        result = progress_tracker.calculate_daily_progression(user_id=1)
        assert result == 100.0
    def test_calculate_overall_progression_first_level_zero_xp(
        self, progress_tracker, mock_user_repository, sample_user
    ):
        sample_user.current_level = 1
        sample_user.total_xp = 0
        mock_user_repository.get_by_id.return_value = sample_user

        result = progress_tracker.calculate_overall_progression(user_id=1)

        assert result == 0.0

    def test_calculate_overall_progression_first_level_fifty_xp(
        self, progress_tracker, mock_user_repository, sample_user
    ):
        sample_user.current_level = 1
        sample_user.total_xp = 50
        mock_user_repository.get_by_id.return_value = sample_user

        result = progress_tracker.calculate_overall_progression(user_id=1)

        assert result == 50.0

    def test_calculate_overall_progression_second_level_zero_xp(
        self, progress_tracker, mock_user_repository, sample_user
    ):
        sample_user.current_level = 2
        sample_user.total_xp = 100
        mock_user_repository.get_by_id.return_value = sample_user

        result = progress_tracker.calculate_overall_progression(user_id=1)

        assert result == 0.0


    def test_calculate_overall_progression_second_level_twenty_xp(
        self, progress_tracker, mock_user_repository, sample_user
    ):
        sample_user.current_level = 2
        sample_user.total_xp = 191
        mock_user_repository.get_by_id.return_value = sample_user

        result = progress_tracker.calculate_overall_progression(user_id=1)

        assert result == 50.0

    def test_get_simple_history_returns_progress_entries(
        self, progress_tracker, mock_daily_progress_repository, sample_progress
    ):
        mock_daily_progress_repository.get_date_range.return_value = sample_progress
        result = progress_tracker.get_simple_history(user_id=1, limit=30)

        assert result == sample_progress
        assert len(result) == 2
        expected_end_date = date.today()
        expected_start_date = expected_end_date - timedelta(days=30)
        mock_daily_progress_repository.get_date_range.assert_called_once_with(
            1, expected_start_date, expected_end_date
        )

    def test_get_simple_history_with_custom_limit(
        self, progress_tracker, mock_daily_progress_repository
    ):
        """Test that get_simple_history respects custom limit parameter."""
        mock_daily_progress_repository.get_date_range.return_value = []

        progress_tracker.get_simple_history(user_id=1, limit=7)

        expected_end_date = date.today()
        expected_start_date = expected_end_date - timedelta(days=7)
        mock_daily_progress_repository.get_date_range.assert_called_once_with(
            1, expected_start_date, expected_end_date
        )

    def test_get_simple_history_with_empty_result(
        self, progress_tracker, mock_daily_progress_repository
    ):
        """Test that get_simple_history handles empty result correctly."""

        mock_daily_progress_repository.get_date_range.return_value = []

        result = progress_tracker.get_simple_history(user_id=1)
        assert result == []
        assert len(result) == 0