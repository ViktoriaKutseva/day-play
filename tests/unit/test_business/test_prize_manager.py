from datetime import datetime
from unittest.mock import Mock

import pytest

from day_play.business.prize_manager import PrizeManager
from day_play.models.entities import Prize, User
from day_play.models.exceptions import (
    InsufficientXPError,
    PrizeAlreadyRedeemedError,
    PrizeNotFoundError,
    UserNotFoundError,
)


@pytest.fixture
def mock_prize_repository() -> Mock:
    """Mock repository for prize data access."""
    return Mock()


@pytest.fixture
def mock_user_repository() -> Mock:
    """Mock repository for user data access."""
    return Mock()


@pytest.fixture
def prize_manager(
    mock_prize_repository: Mock,
    mock_user_repository: Mock,
) -> PrizeManager:
    """Create PrizeManager instance with mocked repositories."""
    return PrizeManager(
        prize_repository=mock_prize_repository,
        user_repository=mock_user_repository,
    )


@pytest.fixture
def sample_prize() -> Prize:
    """Sample prize entity for testing."""
    return Prize(
        id=1,
        name="New Headphones",
        description="Reward for reaching 1000 XP",
        cost_xp=1000,
        redeemed=False,
        user_id=1,
    )


@pytest.fixture
def sample_user() -> User:
    """Sample user entity for testing."""
    return User(
        id=1,
        username="testuser",
        current_level=5,
        total_xp=1500,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestCreatePrize:
    """Tests for create_prize method."""

    def test_create_prize_success(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test successful prize creation with valid parameters."""
        # Arrange
        expected_prize = Prize(
            id=1,
            name="Gaming Mouse",
            description="High-quality gaming mouse",
            cost_xp=500,
            redeemed=False,
            user_id=1,
        )
        mock_prize_repository.create.return_value = expected_prize

        # Act
        prize_to_create = Prize(
            name="Gaming Mouse",
            description="High-quality gaming mouse",
            cost_xp=500,
            user_id=1,
        )
        result = prize_manager.create_prize(prize_to_create)

        # Assert
        assert result == expected_prize
        mock_prize_repository.create.assert_called_once()
        created_prize = mock_prize_repository.create.call_args[0][0]
        assert created_prize.name == "Gaming Mouse"
        assert created_prize.description == "High-quality gaming mouse"
        assert created_prize.cost_xp == 500
        assert created_prize.redeemed is False
        assert created_prize.user_id == 1

    def test_create_prize_with_zero_xp_raises_error(
        self,
        prize_manager: PrizeManager,
    ):
        """Test that creating a prize with zero XP threshold raises ValueError."""
        # Act & Assert
        prize_to_create = Prize(
            name="Invalid Prize",
            description="This should fail",
            cost_xp=0,
            user_id=1,
        )
        with pytest.raises(ValueError, match="Prize XP threshold must be greater than 0"):
            prize_manager.create_prize(prize_to_create)

    def test_create_prize_with_negative_xp_raises_error(
        self,
        prize_manager: PrizeManager,
    ):
        """Test that creating a prize with negative XP threshold raises ValidationError.
        
        Note: Pydantic validation at the entity level rejects negative cost_xp
        before the business logic can even be called.
        """
        # Act & Assert - Pydantic validation catches this at entity creation
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            Prize(
                name="Invalid Prize",
                description="This should fail",
                cost_xp=-100,
                user_id=1,
            )

    def test_create_prize_with_excessive_xp_raises_error(
        self,
        prize_manager: PrizeManager,
    ):
        """Test that creating a prize exceeding 100,000 XP raises ValueError."""
        # Act & Assert
        prize_to_create = Prize(
            name="Overpowered Prize",
            description="This should fail",
            cost_xp=150000,
            user_id=1,
        )
        with pytest.raises(ValueError, match="Prize XP threshold cannot exceed 100,000"):
            prize_manager.create_prize(prize_to_create)

    def test_create_prize_at_max_xp_threshold(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test creating a prize at the maximum allowed XP threshold (100,000)."""
        # Arrange
        expected_prize = Prize(
            id=1,
            name="Ultimate Prize",
            description="Maximum threshold prize",
            cost_xp=100000,
            redeemed=False,
            user_id=1,
        )
        mock_prize_repository.create.return_value = expected_prize

        # Act
        prize_to_create = Prize(
            name="Ultimate Prize",
            description="Maximum threshold prize",
            cost_xp=100000,
            user_id=1,
        )
        result = prize_manager.create_prize(prize_to_create)

        # Assert
        assert result.cost_xp == 100000
        mock_prize_repository.create.assert_called_once()


class TestRedeemPrize:
    """Tests for redeem_prize method."""

    def test_redeem_prize_success(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test successful prize redemption when user has sufficient XP."""
        # Arrange
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user
        redeemed_prize = Prize(
            id=sample_prize.id,
            name=sample_prize.name,
            description=sample_prize.description,
            cost_xp=sample_prize.cost_xp,
            redeemed=True,
            redeemed_at=datetime.now(),
            user_id=sample_prize.user_id,
        )
        mock_prize_repository.update.return_value = redeemed_prize

        # Act
        result = prize_manager.redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result.redeemed is True
        assert result.redeemed_at is not None
        mock_prize_repository.get_by_id.assert_called_once_with(1)
        mock_user_repository.get_by_id.assert_called_once_with(1)
        mock_prize_repository.update.assert_called_once()

    def test_redeem_prize_xp_not_deducted(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test that user's XP is not deducted when redeeming (milestone unlock, not purchase)."""
        # Arrange
        original_xp = sample_user.total_xp
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user
        redeemed_prize = Prize(
            id=sample_prize.id,
            name=sample_prize.name,
            description=sample_prize.description,
            cost_xp=sample_prize.cost_xp,
            redeemed=True,
            redeemed_at=datetime.now(),
            user_id=sample_prize.user_id,
        )
        mock_prize_repository.update.return_value = redeemed_prize

        # Act
        prize_manager.redeem_prize(prize_id=1, user_id=1)

        # Assert - user XP should remain unchanged
        assert sample_user.total_xp == original_xp
        # update_xp should never be called on user repository
        mock_user_repository.update_xp.assert_not_called()

    def test_redeem_prize_not_found_raises_error(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test that redeeming non-existent prize raises PrizeNotFoundError."""
        # Arrange
        mock_prize_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(PrizeNotFoundError, match="Prize with ID 999 not found"):
            prize_manager.redeem_prize(prize_id=999, user_id=1)

    def test_redeem_prize_wrong_user_raises_error(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        sample_prize: Prize,
    ):
        """Test that redeeming prize for wrong user raises PrizeNotFoundError."""
        # Arrange
        sample_prize.user_id = 1
        mock_prize_repository.get_by_id.return_value = sample_prize

        # Act & Assert
        with pytest.raises(PrizeNotFoundError, match="Prize with ID 1 not found for user 2"):
            prize_manager.redeem_prize(prize_id=1, user_id=2)

    def test_redeem_prize_user_not_found_raises_error(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
    ):
        """Test that redeeming prize when user doesn't exist raises UserNotFoundError."""
        # Arrange
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User with ID 1 not found"):
            prize_manager.redeem_prize(prize_id=1, user_id=1)

    def test_redeem_prize_already_redeemed_raises_error(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test that redeeming already redeemed prize raises PrizeAlreadyRedeemedError."""
        # Arrange
        sample_prize.redeemed = True
        sample_prize.redeemed_at = datetime.now()
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user

        # Act & Assert
        with pytest.raises(PrizeAlreadyRedeemedError, match="has already been redeemed"):
            prize_manager.redeem_prize(prize_id=1, user_id=1)

    def test_redeem_prize_insufficient_xp_raises_error(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test that redeeming prize without sufficient XP raises InsufficientXPError."""
        # Arrange
        sample_user.total_xp = 500  # Less than prize cost_xp of 1000
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user

        # Act & Assert
        with pytest.raises(InsufficientXPError, match="Need 1000 XP to unlock"):
            prize_manager.redeem_prize(prize_id=1, user_id=1)

    def test_redeem_prize_exact_xp_threshold(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test successful redemption when user has exactly the XP threshold."""
        # Arrange
        sample_user.total_xp = 1000  # Exactly equal to prize cost_xp
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user
        redeemed_prize = Prize(
            id=sample_prize.id,
            name=sample_prize.name,
            description=sample_prize.description,
            cost_xp=sample_prize.cost_xp,
            redeemed=True,
            redeemed_at=datetime.now(),
            user_id=sample_prize.user_id,
        )
        mock_prize_repository.update.return_value = redeemed_prize

        # Act
        result = prize_manager.redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result.redeemed is True
        mock_prize_repository.update.assert_called_once()


class TestListAvailablePrizes:
    """Tests for list_available_prizes method."""

    def test_list_available_prizes_success(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test listing available prizes returns correct data."""
        # Arrange
        available_prizes = [
            Prize(
                id=1,
                name="Prize 1",
                description="First prize",
                cost_xp=500,
                redeemed=False,
                user_id=1,
            ),
            Prize(
                id=2,
                name="Prize 2",
                description="Second prize",
                cost_xp=1000,
                redeemed=False,
                user_id=1,
            ),
        ]
        mock_prize_repository.get_available.return_value = available_prizes

        # Act
        result = prize_manager.list_available_prizes(user_id=1)

        # Assert
        assert len(result) == 2
        assert all(not prize.redeemed for prize in result)
        mock_prize_repository.get_available.assert_called_once_with(1)

    def test_list_available_prizes_empty(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test listing available prizes returns empty list when none exist."""
        # Arrange
        mock_prize_repository.get_available.return_value = []

        # Act
        result = prize_manager.list_available_prizes(user_id=1)

        # Assert
        assert result == []
        mock_prize_repository.get_available.assert_called_once_with(1)


class TestListRedeemedPrizes:
    """Tests for list_redeemed_prizes method."""

    def test_list_redeemed_prizes_success(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test listing redeemed prizes returns correct data."""
        # Arrange
        redeemed_prizes = [
            Prize(
                id=3,
                name="Prize 3",
                description="Third prize",
                cost_xp=1500,
                redeemed=True,
                redeemed_at=datetime.now(),
                user_id=1,
            ),
        ]
        mock_prize_repository.get_redeemed.return_value = redeemed_prizes

        # Act
        result = prize_manager.list_redeemed_prizes(user_id=1)

        # Assert
        assert len(result) == 1
        assert all(prize.redeemed for prize in result)
        mock_prize_repository.get_redeemed.assert_called_once_with(1)

    def test_list_redeemed_prizes_empty(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test listing redeemed prizes returns empty list when none exist."""
        # Arrange
        mock_prize_repository.get_redeemed.return_value = []

        # Act
        result = prize_manager.list_redeemed_prizes(user_id=1)

        # Assert
        assert result == []
        mock_prize_repository.get_redeemed.assert_called_once_with(1)


class TestCanRedeemPrize:
    """Tests for can_redeem_prize method."""

    def test_can_redeem_prize_returns_true(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test can_redeem_prize returns True when all conditions are met."""
        # Arrange
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user

        # Act
        result = prize_manager.can_redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result is True

    def test_can_redeem_prize_returns_false_prize_not_found(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test can_redeem_prize returns False when prize doesn't exist."""
        # Arrange
        mock_prize_repository.get_by_id.return_value = None

        # Act
        result = prize_manager.can_redeem_prize(prize_id=999, user_id=1)

        # Assert
        assert result is False

    def test_can_redeem_prize_returns_false_wrong_user(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        sample_prize: Prize,
    ):
        """Test can_redeem_prize returns False when prize belongs to different user."""
        # Arrange
        sample_prize.user_id = 2
        mock_prize_repository.get_by_id.return_value = sample_prize

        # Act
        result = prize_manager.can_redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result is False

    def test_can_redeem_prize_returns_false_already_redeemed(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        sample_prize: Prize,
    ):
        """Test can_redeem_prize returns False when prize is already redeemed."""
        # Arrange
        sample_prize.redeemed = True
        mock_prize_repository.get_by_id.return_value = sample_prize

        # Act
        result = prize_manager.can_redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result is False

    def test_can_redeem_prize_returns_false_user_not_found(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
    ):
        """Test can_redeem_prize returns False when user doesn't exist."""
        # Arrange
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = None

        # Act
        result = prize_manager.can_redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result is False

    def test_can_redeem_prize_returns_false_insufficient_xp(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
        mock_user_repository: Mock,
        sample_prize: Prize,
        sample_user: User,
    ):
        """Test can_redeem_prize returns False when user has insufficient XP."""
        # Arrange
        sample_user.total_xp = 500  # Less than prize cost_xp of 1000
        mock_prize_repository.get_by_id.return_value = sample_prize
        mock_user_repository.get_by_id.return_value = sample_user

        # Act
        result = prize_manager.can_redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result is False

    def test_can_redeem_prize_handles_exceptions(
        self,
        prize_manager: PrizeManager,
        mock_prize_repository: Mock,
    ):
        """Test can_redeem_prize returns False on unexpected exceptions."""
        # Arrange
        mock_prize_repository.get_by_id.side_effect = Exception("Database error")

        # Act
        result = prize_manager.can_redeem_prize(prize_id=1, user_id=1)

        # Assert
        assert result is False
