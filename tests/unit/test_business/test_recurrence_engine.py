from datetime import datetime, timedelta, timezone
import pytest
from dateutil.relativedelta import relativedelta

from day_play.business.recurrence_engine import RecurrenceEngine
from day_play.models.entities import Task
from day_play.models.enums import RecurrencePattern, TaskStatus


@pytest.fixture
def test_time():
    """Fixed time for consistent testing."""
    return datetime(2025, 11, 20, 12, 0, 0, tzinfo=timezone.utc)

@pytest.fixture
def test_complete_time():
    """Fixed time for consistent testing."""
    return datetime(2025, 11, 22, 12, 0, 0, tzinfo=timezone.utc)


class TestRecurrenceEngine:
    def test_calculate_next_occurrence_daily(self, test_time):
        """Test next occurrence calculation for daily recurrence."""
        task = Task(
            id=1,
            title="Daily Task",
            description="Test daily task",
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_rule_on_complete=False
        )

        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        expected_date = test_time + timedelta(days=1)
        assert updated_task.next_occurrence.date() >= expected_date.date()

    def test_calculate_next_occurrence_daily_on_complete(self, test_time, test_complete_time):
        """Test next occurrence calculation for daily recurrence."""
        task = Task(
            id=1,
            title="Daily Task",
            description="Test daily task",
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_rule_on_complete=True
        )
        engine = RecurrenceEngine()
        updated_task = task.model_copy(update={"status": TaskStatus.COMPLETED, "completed_at": test_complete_time})
        updated_task = engine.calculate_next_occurrence(updated_task)
        expected_date = test_complete_time + timedelta(days=1)
        assert updated_task.next_occurrence.date() >= expected_date.date()

    def test_calculate_next_occurrence_weekly(self, test_time):
        task = Task(
            id=1,
            title="Weekly Task",
            description="Test weekly task",
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_rule_on_complete=False
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        expected_date = test_time + timedelta(weeks=1)
        assert updated_task.next_occurrence.date() >= expected_date.date()

    def test_calculate_next_occurrence_weekly_on_complete(self, test_time, test_complete_time):
        task = Task(
            id=1,
            title="Weekly Task",
            description="Test weekly task",
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_rule_on_complete=True
        )
        engine = RecurrenceEngine()
        updated_task = task.model_copy(update={"status": TaskStatus.COMPLETED, "completed_at": test_complete_time})
        updated_task = engine.calculate_next_occurrence(updated_task)
        expected_date = test_complete_time + timedelta(weeks=1)
        assert updated_task.next_occurrence.date() >= expected_date.date()

    def test_calculate_next_occurrence_monthly(self, test_time):
        task = Task(
            id=1,
            title="Monthly Task",
            description="Test monthly task",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_rule_on_complete=False
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        expected_date = test_time + relativedelta(months=1)
        assert updated_task.next_occurrence.date() >= expected_date.date()

    def test_calculate_next_occurrence_monthly_on_complete(self, test_time, test_complete_time):
        task = Task(
            id=1,
            title="Monthly Task",
            description="Test monthly task",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_rule_on_complete=True
        )
        updated_task = task.model_copy(update={"status": TaskStatus.COMPLETED, "completed_at": test_complete_time})
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(updated_task)
        expected_date = test_complete_time + relativedelta(months=1)
        assert updated_task.next_occurrence.date() >= expected_date.date()

    def test_calculate_next_occurrence_monthly_edge_case(self):
        """Test monthly recurrence with month-end dates (Jan 31 → Feb 28)."""
        # Create task with completed_at on Jan 31
        task = Task(
            id=1,
            title="Monthly Task",
            description="Test monthly edge case",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_rule_on_complete=True,
            status=TaskStatus.COMPLETED,
            completed_at=datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)

        # Should be Feb 28 (or Feb 29 in leap year)
        assert updated_task.next_occurrence.month == 2

    def test_calculate_next_occurrence_none_pattern(self):
        """Test that NONE pattern returns task with None next_occurrence."""
        task = Task(
            id=3,
            title="Non-recurring Task",
            description="Test none pattern",
            recurrence_pattern=RecurrencePattern.NONE,
            recurrence_rule_on_complete=False
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        assert updated_task.next_occurrence is None

    def test_on_complete_not_yet_completed(self):
        """Test that on_complete tasks don't calculate until completed."""
        task = Task(
            id=4,
            title="On Complete Task",
            description="Not completed yet",
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_rule_on_complete=True,
            status=TaskStatus.PENDING  # Not completed
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        # Should return same task unchanged
        assert updated_task == task

    def test_on_complete_completed_but_no_timestamp(self):
        """Test edge case where task is completed but completed_at is None."""
        task = Task(
            id=8,
            title="Edge Case Task",
            description="Completed but no timestamp",
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_rule_on_complete=True,
            status=TaskStatus.COMPLETED,
            completed_at=None  
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        assert updated_task == task

    def test_monthly_year_boundary(self):
        """Test monthly recurrence crossing year boundary."""
        task = Task(
            id=7,
            title="Year Boundary Task",
            description="Test year crossing",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_rule_on_complete=True,
            status=TaskStatus.COMPLETED,
            completed_at=datetime(2025, 12, 15, 12, 0, 0, tzinfo=timezone.utc)
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        # Should be Jan 15, 2026
        assert updated_task.next_occurrence is not None
        assert updated_task.next_occurrence.month == 1
        assert updated_task.next_occurrence.day == 15
        assert updated_task.next_occurrence.year == 2026

    def test_monthly_leap_year_edge_case(self):
        """Test monthly recurrence on Feb 29 (leap year)."""
        # Feb 29, 2024 (leap year)
        task = Task(
            id=6,
            title="Leap Year Task",
            description="Test leap year",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_rule_on_complete=True,
            status=TaskStatus.COMPLETED,
            completed_at=datetime(2024, 2, 29, 12, 0, 0, tzinfo=timezone.utc)
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        # Should be March 29, 2024
        assert updated_task.next_occurrence is not None
        assert updated_task.next_occurrence.month == 3
        assert updated_task.next_occurrence.day == 29
        assert updated_task.next_occurrence.year == 2024

    def test_monthly_dec_31_to_jan_31(self):
        """Test monthly recurrence from Dec 31 to Jan 31 (year boundary)."""
        task = Task(
            id=9,
            title="Dec 31 Task",
            description="Test Dec 31 edge case",
            recurrence_pattern=RecurrencePattern.MONTHLY,
            recurrence_rule_on_complete=True,
            status=TaskStatus.COMPLETED,
            completed_at=datetime(2025, 12, 31, 12, 0, 0, tzinfo=timezone.utc)
        )
        engine = RecurrenceEngine()
        updated_task = engine.calculate_next_occurrence(task)
        # Should be Jan 31, 2026
        assert updated_task.next_occurrence.month == 1
        assert updated_task.next_occurrence.day == 31
        assert updated_task.next_occurrence.year == 2026