import pytest
from datetime import datetime, date, timedelta
from pydantic import ValidationError

from day_play.models.entities import Task, User, DailyProgress, Achievement, Prize
from day_play.models.enums import Priority, Urgency, TaskStatus, RecurrencePattern


class TestTask:
    def test_valid_task_creation(self):
        """Test creating a valid task with all required fields."""
        task = Task(
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            urgency=Urgency.HIGH,
            status=TaskStatus.PENDING,
            recurrence_pattern=RecurrencePattern.NONE
        )
        assert task.title == "Test Task"
        assert task.priority == Priority.HIGH
        assert task.status == TaskStatus.PENDING

    def test_task_validation_title_required(self):
        """Test that title is required and cannot be empty."""
        with pytest.raises(ValidationError):
            Task(title="")

    def test_task_validation_title_max_length(self):
        """Test title maximum length validation."""
        long_title = "a" * 256  # Exceeds max_length=255
        with pytest.raises(ValidationError):
            Task(title=long_title)

    def test_task_business_logic_is_completed(self):
        """Test is_completed business logic method."""
        completed_task = Task(
            title="Completed Task",
            status=TaskStatus.COMPLETED
        )
        pending_task = Task(
            title="Pending Task",
            status=TaskStatus.PENDING
        )
        
        assert completed_task.is_completed() is True
        assert pending_task.is_completed() is False

    def test_task_business_logic_is_overdue(self):
        """Test is_overdue business logic method."""
        past_due_pending = Task(
            title="Overdue Task",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.PENDING
        )
        past_due_completed = Task(
            title="Completed Overdue Task",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.COMPLETED
        )
        future_due = Task(
            title="Future Task",
            due_date=datetime.now() + timedelta(days=1),
            status=TaskStatus.PENDING
        )
        
        assert past_due_pending.is_overdue() is True
        assert past_due_completed.is_overdue() is False
        assert future_due.is_overdue() is False


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
            User(username="ab")  # Less than min_length=3


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