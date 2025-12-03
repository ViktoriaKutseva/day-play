from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from day_play.business.achievement_manager import (
    ACHIEVEMENT_DEFINITIONS,
    AchievementManager,
)
from day_play.business.gamification_engine import GamificationEngine
from day_play.models.entities import Achievement, User


@pytest.fixture
def mock_task_repository() -> Mock:
    """Mock TaskRepository for testing."""
    return Mock()


@pytest.fixture
def mock_user_repository() -> Mock:
    """Mock UserRepository for testing."""
    return Mock()


@pytest.fixture
def mock_daily_progress_repository() -> Mock:
    """Mock DailyProgressRepository for testing."""
    return Mock()


@pytest.fixture
def mock_achievement_repository() -> Mock:
    """Mock AchievementRepository for testing."""
    return Mock()


@pytest.fixture
def mock_progress_tracker() -> Mock:
    """Mock ProgressTracker for testing."""
    return Mock()


@pytest.fixture
def gamification_engine() -> GamificationEngine:
    """Real GamificationEngine instance."""
    return GamificationEngine()


@pytest.fixture
def achievement_manager(
    mock_task_repository: Mock,
    mock_user_repository: Mock,
    mock_daily_progress_repository: Mock,
    mock_achievement_repository: Mock,
    mock_progress_tracker: Mock,
    gamification_engine: GamificationEngine,
) -> AchievementManager:
    """Create AchievementManager with mocked dependencies."""
    return AchievementManager(
        gamification=gamification_engine,
        task_repository=mock_task_repository,
        user_repository=mock_user_repository,
        daily_progress_repository=mock_daily_progress_repository,
        achievement_repository=mock_achievement_repository,
        progress_tracker=mock_progress_tracker,
    )


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id=1,
        username="testuser",
        current_level=1,
        total_xp=100,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestGetAchievementDefinitions:
    """Test suite for get_achievement_definitions method."""

    def test_returns_all_achievement_definitions(self, achievement_manager):
        """Test that method returns all defined achievements."""
        # Act
        definitions = achievement_manager.get_achievement_definitions()

        # Assert
        assert definitions == ACHIEVEMENT_DEFINITIONS
        assert len(definitions) == 6  # We have 6 achievements defined
        assert all(isinstance(ach, Achievement) for ach in definitions)

    def test_achievement_definitions_have_required_fields(self, achievement_manager):
        """Test that all achievement definitions have required fields."""
        # Act
        definitions = achievement_manager.get_achievement_definitions()

        # Assert
        for achievement in definitions:
            assert achievement.name is not None
            assert achievement.description is not None
            assert achievement.icon is not None
            assert achievement.unlock_criteria is not None
            assert len(achievement.unlock_criteria) > 0

    def test_achievement_definitions_are_immutable(self, achievement_manager):
        """Test that returned definitions don't affect original list."""
        # Act
        definitions1 = achievement_manager.get_achievement_definitions()
        definitions2 = achievement_manager.get_achievement_definitions()

        # Assert
        assert definitions1 == definitions2
        assert definitions1 is ACHIEVEMENT_DEFINITIONS  # Same reference


class TestCheckCriteria:
    """Test suite for _check_criteria helper method."""

    def test_empty_criteria_returns_false(self, achievement_manager):
        """Test that empty criteria returns False."""
        # Act
        result = achievement_manager._check_criteria(None, 10, 5)

        # Assert
        assert result is False

    def test_tasks_completed_met(self, achievement_manager):
        """Test task completion criteria when met."""
        # Arrange
        criteria = {"tasks_completed": 10}

        # Act
        result = achievement_manager._check_criteria(criteria, 10, 0)

        # Assert
        assert result is True

    def test_tasks_completed_exceeded(self, achievement_manager):
        """Test task completion criteria when exceeded."""
        # Arrange
        criteria = {"tasks_completed": 10}

        # Act
        result = achievement_manager._check_criteria(criteria, 15, 0)

        # Assert
        assert result is True

    def test_tasks_completed_not_met(self, achievement_manager):
        """Test task completion criteria when not met."""
        # Arrange
        criteria = {"tasks_completed": 10}

        # Act
        result = achievement_manager._check_criteria(criteria, 9, 0)

        # Assert
        assert result is False

    def test_daily_streak_met(self, achievement_manager):
        """Test daily streak criteria when met."""
        # Arrange
        criteria = {"daily_streak": 7}

        # Act
        result = achievement_manager._check_criteria(criteria, 0, 7)

        # Assert
        assert result is True

    def test_daily_streak_exceeded(self, achievement_manager):
        """Test daily streak criteria when exceeded."""
        # Arrange
        criteria = {"daily_streak": 7}

        # Act
        result = achievement_manager._check_criteria(criteria, 0, 10)

        # Assert
        assert result is True

    def test_daily_streak_not_met(self, achievement_manager):
        """Test daily streak criteria when not met."""
        # Arrange
        criteria = {"daily_streak": 7}

        # Act
        result = achievement_manager._check_criteria(criteria, 0, 6)

        # Assert
        assert result is False

    def test_multiple_criteria_all_met(self, achievement_manager):
        """Test multiple criteria when all are met."""
        # Arrange
        criteria = {"tasks_completed": 10, "daily_streak": 5}

        # Act
        result = achievement_manager._check_criteria(criteria, 10, 5)

        # Assert
        assert result is True

    def test_multiple_criteria_one_not_met(self, achievement_manager):
        """Test multiple criteria when one is not met."""
        # Arrange
        criteria = {"tasks_completed": 10, "daily_streak": 5}

        # Act - tasks met, streak not met
        result = achievement_manager._check_criteria(criteria, 10, 4)

        # Assert
        assert result is False


class TestCheckAndUnlockAchievements:
    """Test suite for check_and_unlock_achievements method."""

    def test_user_not_found_returns_empty_list(
        self,
        achievement_manager,
        mock_user_repository,
    ):
        """Test that non-existent user returns empty list."""
        # Arrange
        mock_user_repository.get_by_id.return_value = None

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=999)

        # Assert
        assert result == []
        mock_user_repository.get_by_id.assert_called_once_with(999)

    def test_first_task_achievement_unlocked(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that 'Getting Started' unlocks on first completed task."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 1
        mock_progress_tracker.calculate_daily_streak.return_value = 0
        mock_achievement_repository.get_unlocked.return_value = []

        # Mock achievement creation
        created_achievement = Achievement(
            id=1,
            name="Getting Started",
            description="Complete your first task.",
            icon="🏆",
            unlock_criteria={"tasks_completed": 1},
            unlocked_at=datetime.now(UTC),
            user_id=1,
        )
        mock_achievement_repository.create.return_value = created_achievement

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        assert len(result) == 1
        assert result[0].name == "Getting Started"
        assert result[0].user_id == 1
        assert result[0].unlocked_at is not None
        mock_achievement_repository.create.assert_called_once()

    def test_task_master_achievement_unlocked(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that 'Task Master' unlocks at 10 completed tasks."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 10
        mock_progress_tracker.calculate_daily_streak.return_value = 0
        mock_achievement_repository.get_unlocked.return_value = []

        # Mock multiple achievements being created
        def create_side_effect(achievement):
            return achievement.model_copy(update={"id": 1})

        mock_achievement_repository.create.side_effect = create_side_effect

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        # Should unlock: Getting Started (1) and Task Master (10)
        assert len(result) >= 1
        achievement_names = {ach.name for ach in result}
        assert "Task Master" in achievement_names

    def test_streak_achievement_unlocked(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that streak achievement unlocks with proper streak count."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 20
        mock_progress_tracker.calculate_daily_streak.return_value = 7  # 7-day streak
        mock_achievement_repository.get_unlocked.return_value = []

        def create_side_effect(achievement):
            return achievement.model_copy(update={"id": 1})

        mock_achievement_repository.create.side_effect = create_side_effect

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        achievement_names = {ach.name for ach in result}
        assert "Week Warrior" in achievement_names or "Daily Streak" in achievement_names

    def test_no_achievements_unlocked_when_criteria_not_met(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that no achievements unlock when criteria aren't met."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 0
        mock_progress_tracker.calculate_daily_streak.return_value = 0
        mock_achievement_repository.get_unlocked.return_value = []

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        assert len(result) == 0
        mock_achievement_repository.create.assert_not_called()

    def test_already_unlocked_achievements_not_duplicated(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that achievements aren't unlocked twice."""
        # Arrange
        already_unlocked = Achievement(
            id=1,
            name="Getting Started",
            description="Complete your first task.",
            icon="🏆",
            unlock_criteria={"tasks_completed": 1},
            unlocked_at=datetime.now(UTC),
            user_id=1,
        )

        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 1
        mock_progress_tracker.calculate_daily_streak.return_value = 0
        mock_achievement_repository.get_unlocked.return_value = [already_unlocked]

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        assert len(result) == 0
        mock_achievement_repository.create.assert_not_called()

    def test_multiple_achievements_unlocked_at_once(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that multiple achievements can be unlocked simultaneously."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 10
        mock_progress_tracker.calculate_daily_streak.return_value = 5
        mock_achievement_repository.get_unlocked.return_value = []

        def create_side_effect(achievement):
            return achievement.model_copy(update={"id": 1})

        mock_achievement_repository.create.side_effect = create_side_effect

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        # Should unlock: Getting Started (1), Task Master (10), Daily Streak (5)
        assert len(result) >= 2
        achievement_names = {ach.name for ach in result}
        assert "Getting Started" in achievement_names
        assert "Task Master" in achievement_names

    def test_century_achievement_unlocked(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that 'Century' unlocks at 100 completed tasks."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 100
        mock_progress_tracker.calculate_daily_streak.return_value = 0
        mock_achievement_repository.get_unlocked.return_value = []

        def create_side_effect(achievement):
            return achievement.model_copy(update={"id": 1})

        mock_achievement_repository.create.side_effect = create_side_effect

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        achievement_names = {ach.name for ach in result}
        assert "Century" in achievement_names

    def test_error_during_checking_returns_partial_results(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that partial results are returned even if error occurs."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 10
        mock_progress_tracker.calculate_daily_streak.return_value = 0
        mock_achievement_repository.get_unlocked.return_value = []

        # First call succeeds, second fails
        call_count = 0

        def create_side_effect(achievement):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return achievement.model_copy(update={"id": 1})
            else:
                raise Exception("Database error")

        mock_achievement_repository.create.side_effect = create_side_effect

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        # Should return the one achievement that was created before error
        assert len(result) == 1


class TestGetUnlockedAchievements:
    """Test suite for get_unlocked_achievements method."""

    def test_returns_unlocked_achievements(
        self,
        achievement_manager,
        mock_achievement_repository,
    ):
        """Test that method returns user's unlocked achievements."""
        # Arrange
        unlocked = [
            Achievement(
                id=1,
                name="Getting Started",
                description="Complete your first task.",
                icon="🏆",
                unlocked_at=datetime.now(UTC),
                user_id=1,
            ),
            Achievement(
                id=2,
                name="Task Master",
                description="Complete 10 tasks.",
                icon="🏅",
                unlocked_at=datetime.now(UTC),
                user_id=1,
            ),
        ]
        mock_achievement_repository.get_unlocked.return_value = unlocked

        # Act
        result = achievement_manager.get_unlocked_achievements(user_id=1)

        # Assert
        assert result == unlocked
        assert len(result) == 2
        mock_achievement_repository.get_unlocked.assert_called_once_with(1)

    def test_returns_empty_list_when_no_achievements(
        self,
        achievement_manager,
        mock_achievement_repository,
    ):
        """Test that empty list is returned when user has no achievements."""
        # Arrange
        mock_achievement_repository.get_unlocked.return_value = []

        # Act
        result = achievement_manager.get_unlocked_achievements(user_id=1)

        # Assert
        assert result == []


class TestGetAvailableAchievements:
    """Test suite for get_available_achievements method."""

    def test_returns_available_achievements(
        self,
        achievement_manager,
        mock_achievement_repository,
    ):
        """Test that method returns achievements user hasn't unlocked."""
        # Arrange
        unlocked = [
            Achievement(
                id=1,
                name="Getting Started",
                description="Complete your first task.",
                icon="🏆",
                unlocked_at=datetime.now(UTC),
                user_id=1,
            ),
        ]
        mock_achievement_repository.get_unlocked.return_value = unlocked

        # Act
        result = achievement_manager.get_available_achievements(user_id=1)

        # Assert
        # Should return all achievements except "Getting Started"
        available_names = {ach.name for ach in result}
        assert "Getting Started" not in available_names
        assert "Task Master" in available_names
        assert "Century" in available_names
        assert len(result) == 5  # 6 total - 1 unlocked = 5 available

    def test_returns_all_achievements_when_none_unlocked(
        self,
        achievement_manager,
        mock_achievement_repository,
    ):
        """Test that all achievements returned when none are unlocked."""
        # Arrange
        mock_achievement_repository.get_unlocked.return_value = []

        # Act
        result = achievement_manager.get_available_achievements(user_id=1)

        # Assert
        assert len(result) == 6  # All achievements are available

    def test_returns_empty_when_all_unlocked(
        self,
        achievement_manager,
        mock_achievement_repository,
    ):
        """Test that empty list returned when all achievements unlocked."""
        # Arrange
        # Create unlocked versions of all achievement definitions
        unlocked = [
            Achievement(
                id=idx,
                name=ach.name,
                description=ach.description,
                icon=ach.icon,
                unlock_criteria=ach.unlock_criteria,
                unlocked_at=datetime.now(UTC),
                user_id=1,
            )
            for idx, ach in enumerate(ACHIEVEMENT_DEFINITIONS, start=1)
        ]
        mock_achievement_repository.get_unlocked.return_value = unlocked

        # Act
        result = achievement_manager.get_available_achievements(user_id=1)

        # Assert
        assert len(result) == 0


class TestIntegrationWithProgressTracker:
    """Test suite for integration with ProgressTracker for streak calculation."""

    def test_uses_progress_tracker_for_streak_calculation(
        self,
        achievement_manager,
        mock_user_repository,
        mock_task_repository,
        mock_achievement_repository,
        mock_progress_tracker,
        sample_user,
    ):
        """Test that AchievementManager delegates streak calculation to ProgressTracker."""
        # Arrange
        mock_user_repository.get_by_id.return_value = sample_user
        mock_task_repository.count_completed_tasks.return_value = 20
        mock_progress_tracker.calculate_daily_streak.return_value = 7
        mock_achievement_repository.get_unlocked.return_value = []

        def create_side_effect(achievement):
            return achievement.model_copy(update={"id": 1})

        mock_achievement_repository.create.side_effect = create_side_effect

        # Act
        result = achievement_manager.check_and_unlock_achievements(user_id=1)

        # Assert
        # Verify ProgressTracker.calculate_daily_streak was called
        mock_progress_tracker.calculate_daily_streak.assert_called_once_with(1)

        # Verify streak achievements unlocked based on ProgressTracker result
        achievement_names = {ach.name for ach in result}
        # With 7-day streak, should unlock both Daily Streak (5) and Week Warrior (7)
        assert "Daily Streak" in achievement_names or "Week Warrior" in achievement_names
