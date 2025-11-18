from datetime import datetime

import pytest
from pydantic import ValidationError

from day_play.models.entities import User


class TestUser:
    def test_valid_user_creation(self):
        """Test creating a valid user."""
        user = User(
            username="testuser",
            current_level=1,
            total_xp=0
        )
        assert user.username == "testuser"
        assert user.current_level == 1
        assert user.total_xp == 0

    def test_user_nullable_username(self):
        """Test that username can be None."""
        user = User(username=None)
        assert user.username is None

    def test_user_validation_username_min_length(self):
        """Test username minimum length validation."""
        with pytest.raises(ValidationError):
            User(username="ab")

    def test_user_default_level_is_one(self):
        """Test that user default lvl is one"""
        user = User(username=None)
        assert user.current_level == 1

    def test_user_default_xp_is_zero(self):
        """Test that user default xp is zero"""
        user = User(username=None)
        assert user.total_xp == 0

    def test_user_username_exceeds_max_length(self):
        """Test username maximum length validation."""
        long_username = "a" * 51  # Exceeds max_length=50
        with pytest.raises(ValidationError):
            User(username=long_username)

    def test_user_username_max_length(self):
        """Test username maximum length validation."""
        max_length_username = "a" * 50
        user = User(username=max_length_username)
        assert user.username == max_length_username

    def test_user_created_and_updated_timestamps(self):
        """Test that created_at and updated_at can be set."""
        now = datetime.now()
        user = User(
            username="timestampeduser",
            created_at=now,
            updated_at=now
        )
        assert user.created_at == now
        assert user.updated_at == now
