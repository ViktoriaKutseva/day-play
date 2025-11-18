from datetime import date, datetime, timedelta

import pytest
from pydantic import ValidationError

from day_play.models.entities import Achievement, DailyProgress, Prize, Task, User
from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency


class TestTaskGeneral:
    @pytest.mark.asyncio
    async def test_valid_task_creation(self):
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

class TestTaskTitleAndDescription:
    @pytest.mark.asyncio
    async def test_task_max_length_title(self):
        """Test title maximum length validation."""
        max_length_title = "a" * 255
        task = Task(
            title=max_length_title,
            description=None
        )
        assert task.title == max_length_title

    @pytest.mark.asyncio
    async def test_task_min_length_title(self):
        """Test title minimum length validation."""
        min_length_title = "A"  # Minimum length is 1
        task = Task(
            title=min_length_title,
            description=None
        )
        assert task.title == min_length_title

    @pytest.mark.asyncio
    async def test_task_validation_title_required(self):
        """Test that title is required and cannot be empty."""
        with pytest.raises(ValidationError):
            Task(title="", description=None)

    @pytest.mark.asyncio
    async def test_task_validation_title_whitespace(self):
        """Test that title cannot be just whitespace."""
        with pytest.raises(ValidationError):
            Task(title="   ", description=None)

    @pytest.mark.asyncio
    async def test_task_validation_title_exceed_max_length(self):
        """Test title maximum length validation."""
        long_title = "a" * 256  # Exceeds max_length=255
        with pytest.raises(ValidationError):
            Task(title=long_title, description=None)

    @pytest.mark.asyncio
    async def test_task_nullable_description(self):
        """Test that description can be None."""
        task = Task(
            title="Task without description",
            description=None
        )
        assert task.description is None

    @pytest.mark.asyncio
    async def test_task_description_max_length(self):
        """Test description maximum length validation."""
        longest_possible_description = "a" * 1000
        task = Task(
            title="Task with max length description",
            description=longest_possible_description
        )
        assert task.description == longest_possible_description

    @pytest.mark.asyncio
    async def test_task_description_min_length(self):
        """Test description minimum length validation."""
        shortest_possible_description = "" 
        task = Task(
            title="Task with min length description",
            description=shortest_possible_description
        )
        assert task.description == shortest_possible_description

    @pytest.mark.asyncio
    async def test_task_description_exceeds_max_length(self):
        """Test description exceeding maximum length validation."""
        too_long_description = "a" * 1001
        with pytest.raises(ValidationError):
            Task(
                title="Task with too long description",
                description=too_long_description
            )

class TestTaskPriorityAndUrgency:
    @pytest.mark.asyncio
    async def test_task_accepts_low_priority(self):
        """Test that task accepts LOW priority."""
        task = Task(
            title="Low Priority Task",
            priority=Priority.LOW,
            description=None
        )
        assert task.priority == Priority.LOW

    @pytest.mark.asyncio
    async def test_task_accepts_medium_priority(self):
        """Test that task accepts MEDIUM priority."""
        task = Task(
            title="Medium Priority Task",
            priority=Priority.MEDIUM,
            description=None
        )
        assert task.priority == Priority.MEDIUM

    @pytest.mark.asyncio
    async def test_task_accepts_high_priority(self):
        """Test that task accepts HIGH priority."""
        task = Task(
            title="High Priority Task",
            priority=Priority.HIGH,
            description=None
        )
        assert task.priority == Priority.HIGH

    @pytest.mark.asyncio
    async def test_task_rejects_invalid_priority(self):
        """Test that task rejects invalid priority values."""
        with pytest.raises(ValidationError):
            Task(
                title="Invalid Priority Task",
                priority="URGENT",
                description=None
            )
    @pytest.mark.asyncio
    async def test_task_accepts_low_urgency(self):
        """Test that task accepts LOW urgency."""
        task = Task(
            title="Low Urgency Task",
            urgency=Urgency.LOW,
            description=None
        )
        assert task.urgency == Urgency.LOW
    @pytest.mark.asyncio
    async def test_task_accepts_medium_urgency(self):
        """Test that task accepts MEDIUM urgency."""
        task = Task(
            title="Medium Urgency Task",
            urgency=Urgency.MEDIUM,
            description=None
        )
        assert task.urgency == Urgency.MEDIUM
    @pytest.mark.asyncio
    async def test_task_accepts_high_urgency(self):
        """Test that task accepts HIGH urgency."""
        task = Task(
            title="High Urgency Task",
            urgency=Urgency.HIGH,
            description=None
        )
        assert task.urgency == Urgency.HIGH
    @pytest.mark.asyncio
    async def test_task_rejects_invalid_urgency(self):
        """Test that task rejects invalid urgency values."""
        with pytest.raises(ValidationError):
            Task(
                title="Invalid Urgency Task",
                urgency="CRITICAL",
                description=None
            )

class TestTaskBusinessLogic:
    @pytest.mark.asyncio
    async def test_task_business_logic_is_completed(self):
        """Test is_completed business logic method."""
        completed_task = Task(
            title="Completed Task",
            status=TaskStatus.COMPLETED,
            description=None
        )
        pending_task = Task(
            title="Pending Task",
            status=TaskStatus.PENDING,
            description=None
        )
        assert completed_task.is_completed() is True
        assert pending_task.is_completed() is False

    @pytest.mark.asyncio
    async def test_task_business_logic_is_overdue(self):
        """Test is_overdue business logic method."""
        past_due_pending = Task(
            title="Overdue Task",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.PENDING,
            description=None
        )
        past_due_completed = Task(
            title="Completed Overdue Task",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.COMPLETED,
            description=None
        )
        future_due = Task(
            title="Future Task",
            due_date=datetime.now() + timedelta(days=1),
            status=TaskStatus.PENDING,
            description=None
        )
        assert past_due_pending.is_overdue() is True
        assert past_due_completed.is_overdue() is False
        assert future_due.is_overdue() is False

    @pytest.mark.asyncio
    async def test_task_is_overdue_with_no_due_date(self):
        """Test that task with no due date is not overdue."""
        task = Task(
            title="No Due Date Task",
            due_date=None,
            status=TaskStatus.PENDING,
            description=None
        )
        assert task.is_overdue() is False

    @pytest.mark.asyncio
    async def test_task_is_overdue_when_completed_and_past_due(self):
        """Test that completed task past due date is not overdue."""
        task = Task(
            title="Completed Past Due Task",
            due_date=datetime.now() - timedelta(days=2),
            status=TaskStatus.COMPLETED,
            description=None
        )
        assert task.is_overdue() is False

    @pytest.mark.asyncio
    async def test_task_not_overdue_when_due_date_is_today(self):
        """Test that task due today is not overdue."""
        task = Task(
            title="Due Today Task",
            due_date=datetime.now() + timedelta(hours=1),
            status=TaskStatus.PENDING,
            description=None
        )
        assert task.is_overdue() is False

    @pytest.mark.asyncio
    async def test_task_is_overdue_boundary_case(self):
        """Test boundary case for is_overdue method."""
        task = Task(
            title="Boundary Overdue Task",
            due_date=datetime.now() - timedelta(seconds=1),
            status=TaskStatus.PENDING,
            description=None
        )
        assert task.is_overdue() is True

class TestTaskOptionalFieldsAndXP:
    @pytest.mark.asyncio
    async def test_task_custom_xp_optional(self):
        """Test that custom_xp is optional."""
        task = Task(
            title="Task without custom XP",
            description=None
        )
        assert task.custom_xp is None

    @pytest.mark.asyncio
    async def test_task_custom_xp_positive_value(self):
        """Test that custom_xp accepts positive integer."""
        task = Task(
            title="Task with custom XP",
            custom_xp=150,
            description=None
        )
        assert task.custom_xp == 150

    @pytest.mark.asyncio
    async def test_task_custom_xp_zero_value(self):
        """Test that custom_xp accepts zero value."""
        task = Task(
            title="Task with zero custom XP",
            custom_xp=0,
            description=None
        )
        assert task.custom_xp == 0

    @pytest.mark.asyncio
    async def test_task_custom_xp_negative_fails(self):
        """Test that negative xp fails"""
        with pytest.raises(ValidationError):
            Task(title="test negative xp", description = None, custom_xp=-3)

    @pytest.mark.asyncio
    async def test_task_due_date_optional(self):
        """Test that due date can be optional"""
        task = Task(
            title="Task with no due date",
            description=None
        )
        assert task.due_date is None

class TestTaskRecurrencePattern:
    @pytest.mark.asyncio
    async def test_task_accepts_none_recurrence(self):
        """Test that task accepts NONE recurrence pattern."""
        task = Task(
            title="Non-recurring Task",
            recurrence_pattern=RecurrencePattern.NONE,
            description=None
        )
        assert task.recurrence_pattern == RecurrencePattern.NONE

    @pytest.mark.asyncio
    async def test_task_accepts_daily_recurrence(self):
        """Test that task accepts DAILY recurrence pattern."""
        task = Task(
            title="Daily Recurring Task",
            recurrence_pattern=RecurrencePattern.DAILY,
            description=None
        )
        assert task.recurrence_pattern == RecurrencePattern.DAILY

    @pytest.mark.asyncio
    async def test_task_accepts_weekly_recurrence(self):
        """Test that task accepts WEEKLY recurrence pattern."""
        task = Task(
            title="Weekly Recurring Task",
            recurrence_pattern=RecurrencePattern.WEEKLY,
            description=None
        )
        assert task.recurrence_pattern == RecurrencePattern.WEEKLY

    @pytest.mark.asyncio
    async def test_task_accepts_monthly_recurrence(self):
        """Test that task accepts MONTHLY recurrence pattern."""
        task = Task(
            title="Monthly Recurring Task",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            description=None
        )
        assert task.recurrence_pattern == RecurrencePattern.MONTHLY

    @pytest.mark.asyncio
    async def test_task_accepts_on_complete_recurrence(self):
        """Test that task accepts ON_COMPLETE recurrence pattern."""
        task = Task(
            title="On Complete Recurring Task",
            recurrence_pattern=RecurrencePattern.ON_COMPLETE,
            description=None
        )
        assert task.recurrence_pattern == RecurrencePattern.ON_COMPLETE

    @pytest.mark.asyncio
    async def test_task_rejects_invalid_recurrence_pattern(self):
        """Test that task rejects invalid recurrence pattern."""
        with pytest.raises(ValidationError):
            Task(
                title="Invalid Recurrence Task",
                recurrence_pattern="WEEKDAY",
                description=None
            )
