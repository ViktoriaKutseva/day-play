import random
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from faker import Faker

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.progress_tracker import ProgressTracker
from day_play.models.entities import Task, User
from day_play.models.enums import TaskStatus


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
            status=random.choice(list(TaskStatus)),
            user_id=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),)
        tasks.append(task)
    return tasks


class TestProgressTracker:
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

    def test_calculate_overall_progression_user_not_found_returns_zero(self, progress_tracker, mock_user_repository):
        mock_user_repository.get_by_id.return_value = None
        result = progress_tracker.calculate_overall_progression(user_id=1)
        assert result == 0.0
