from datetime import date, datetime, timedelta

import pytest
from pydantic import ValidationError

from day_play.models.entities import Achievement, DailyProgress, Prize, Task, User
from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency

class TestAchievement:
    def test_valid_achievement_creation(self):
        """Test creating a valid achievement."""
        achievement = Achievement(
            name="First Task",
            description="Complete your first task",
            icon="trophy",
            unlock_criteria={"tasks_completed": 1}
        )
        assert achievement.name == "First Task"
        assert achievement.icon == "trophy"
        assert achievement.unlock_criteria == {"tasks_completed": 1}

    def test_achievement_no_name(self):
        """Test achievement name minimum length validation."""
        with pytest.raises(ValidationError):
            Achievement(
                name="",
                description="Description",
                icon="icon",
                unlock_criteria={}
            )

    def test_achievement_name_min_length(self):
        """Test achievement name minimum length validation."""
        min_length_title = "A"  # Minimum length is 1
        achievement = Achievement(
            name=min_length_title,
            description=None,
            icon="icon",
            unlock_criteria={}
            )
        assert achievement.name == min_length_title

    def test_achievement_name_max_length(self):
        """Test achievement name maximum length validation."""
        long_name = "a" * 100 
        achievement = Achievement(
            name=long_name,
            description=None,
            icon="icon",
            unlock_criteria={}
            )
        assert achievement.name == long_name

    def test_achievement_name_exceeds_max_length(self):
        """Test achievement name maximum length validation."""
        long_name = "a" * 101  # Exceeds max_length=100
        with pytest.raises(ValidationError):
            Achievement(
                name=long_name,
                description="Description",
                icon="icon",
                unlock_criteria={}
            )
    def test_achievement_description_exceeds_max_length(self):
        """Test achievement description maximum length validation."""
        long_description = "a" * 501 
        with pytest.raises(ValidationError):
            Achievement(
                name="Valid Name",
                description=long_description,
                icon="icon",
                unlock_criteria={}
            )
    def test_achievement_icon_exceeds_max_length(self):
        """Test achievement icon maximum length validation."""
        long_icon = "a" * 256  
        with pytest.raises(ValidationError):
            Achievement(
                name="Valid Name",
                description="Valid Description",
                icon=long_icon,
                unlock_criteria={}
            )
    def test_achievement_unlock_criteria_not_dict(self):
        """Test achievement unlock_criteria type validation."""
        with pytest.raises(ValidationError):
            Achievement(
                name="Valid Name",
                description="Valid Description",
                icon="icon",
                unlock_criteria="not a dict"
            )
    def test_achievement_description_optional(self):
        """Test that description is optional."""
        achievement = Achievement(
            name="No Description",
            icon="icon",
            unlock_criteria={}
        )
        assert achievement.description is None

    def test_achievement_description_max_length(self):
        """Test achievement description maximum length validation."""
        max_length_description = "a" * 500 
        achievement = Achievement(
            name="Valid Name",
            description=max_length_description,
            icon="icon",
            unlock_criteria={}
            )
        assert achievement.description == max_length_description

    def test_achievement_unlock_criteria_optional(self):
        """Test that unlock_criteria is optional."""
        achievement = Achievement(
            name="No Criteria",
            icon="icon",
            description=None
        )
        assert achievement.unlock_criteria is None