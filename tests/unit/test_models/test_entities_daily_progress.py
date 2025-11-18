from datetime import date

import pytest
from pydantic import ValidationError

from day_play.models.entities import DailyProgress


class TestDailyProgress:
    def test_valid_daily_progress_creation(self):
        """Test creating valid daily progress."""
        progress = DailyProgress(
            user_id=1,
            date=date.today(),
            tasks_completed=5,
            tasks_total=10,
            completion_percentage=50.0,
            daily_xp_earned=100
        )
        assert progress.user_id == 1
        assert progress.tasks_completed == 5
        assert progress.completion_percentage == 50.0

    def test_daily_progress_defaults(self):
        """Test default values for daily progress."""
        progress = DailyProgress(
            user_id=2,
            date=date.today()
        )
        assert progress.tasks_completed == 0
        assert progress.tasks_total == 0
        assert progress.completion_percentage == 0.0
        assert progress.daily_xp_earned == 0

    def test_daily_progress_completion_percentage(self):
        """Test that completion percentage is correctly set."""
        progress = DailyProgress(
            user_id=1,
            date=date.today(),
            tasks_completed=3,
            tasks_total=6,
            completion_percentage=50.0,
            daily_xp_earned=120
        )
        assert progress.completion_percentage == 50.0

    def test_daily_progress_date_field(self):
        """Test that the date field is correctly assigned."""
        test_date = date(2024, 1, 15)
        progress = DailyProgress(
            user_id=3,
            date=test_date
        )
        assert progress.date == test_date

    def test_daily_progress_negative_values_rejected(self):
        """Test that negative values for tasks_completed and tasks_total are rejected."""
        with pytest.raises(ValidationError):
            DailyProgress(
                user_id=4,
                date=date.today(),
                tasks_completed=-1,
                tasks_total=5
            )
        with pytest.raises(ValidationError):
            DailyProgress(
                user_id=4,
                date=date.today(),
                tasks_completed=3,
                tasks_total=-5
            )

    def test_daily_progress_xp_earned_non_negative(self):
        """Test that daily_xp_earned cannot be negative."""
        with pytest.raises(ValidationError):
            DailyProgress(
                user_id=5,
                date=date.today(),
                daily_xp_earned=-50
            )
    def test_daily_progress_completion_percentage_range(self):
        """Test that completion_percentage is within valid range (0-100)."""
        with pytest.raises(ValidationError):
            DailyProgress(
                user_id=6,
                date=date.today(),
                completion_percentage=-10.0
            )
        with pytest.raises(ValidationError):
            DailyProgress(
                user_id=6,
                date=date.today(),
                completion_percentage=150.0
            )