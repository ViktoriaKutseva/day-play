
import pytest
from pydantic import ValidationError

from day_play.models.entities import Prize


class TestPrize:
    def test_valid_prize_creation(self):
        """Test creating a valid prize."""
        prize = Prize(
            name="Coffee Break",
            description="Take a coffee break",
            cost_xp=50
        )
        assert prize.name == "Coffee Break"
        assert prize.cost_xp == 50
        assert prize.redeemed is False

    def test_prize_no_name(self):
        """Test prize name minimum length validation."""
        with pytest.raises(ValidationError):
            Prize(
                name="",
                description="Description",
                cost_xp=10
            )
    def test_prize_name_exceeds_max_length(self):
        """Test prize name maximum length validation."""
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            Prize(
                name=long_name,
                description="Description",
                cost_xp=10
            )
    def test_prize_name_whitespace_only(self):
        """Test prize name cannot be just whitespace."""
        with pytest.raises(ValidationError):
            Prize(
                name="   ",
                description="Description",
                cost_xp=10
            )
    def test_prize_description_exceeds_max_length(self):
        """Test prize description maximum length validation."""
        long_description = "a" * 501
        with pytest.raises(ValidationError):
            Prize(
                name="Lunch",
                description=long_description,
                cost_xp=30
            )
    def test_prize_name_min_length(self):
        """Test prize name minimum length validation."""
        min_length_name = "A"
        prize = Prize(
            name=min_length_name,
            description=None,
            cost_xp=10
        )
        assert prize.name == min_length_name

    def test_prize_name_max_length(self):
        """Test prize name maximum length validation."""
        long_name = "a" * 100 
        prize = Prize(
            name=long_name,
            description=None,
            cost_xp=10
        )
        assert prize.name == long_name

    def test_prize_description_optional(self):
        """Test prize description can be None."""
        prize = Prize(
            name="Snack",
            description=None,
            cost_xp=20
        )
        assert prize.description is None

    def test_prize_description_max_length(self):
        """Test prize description maximum length validation."""
        long_description = "a" * 500 
        prize = Prize(
            name="Lunch",
            description=long_description,
            cost_xp=30
        )
        assert prize.description == long_description

    def test_prize_default_redeemed_false(self):
        """Test that redeemed defaults to False."""
        prize = Prize(
            name="Movie Ticket",
            description="Watch a movie",
            cost_xp=100
        )
        assert prize.redeemed is False

    def test_prize_cost_xp_non_negative(self):
        """Test prize cost_xp must be non-negative."""
        with pytest.raises(ValidationError):
            Prize(
                name="Expensive Item",
                description="This item costs negative XP",
                cost_xp=-10
            )

    def test_prize_cost_xp_zero_valid(self):
        """Test prize cost_xp can be zero."""
        prize = Prize(
            name="Free Item",
            description="This item costs no XP",
            cost_xp=0
        )
        assert prize.cost_xp == 0

    def test_prize_cost_xp_negative_fails(self):
        """Test prize cost_xp negative value raises ValidationError."""
        with pytest.raises(ValidationError):
            Prize(
                name="Invalid Item",
                description="This item has negative cost",
                cost_xp=-5
            )
