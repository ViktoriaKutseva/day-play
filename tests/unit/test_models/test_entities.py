"""Sample unit tests for Task entity."""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.day_play.models.entities import Task


class TestTask:
    """Test Task entity."""

    def test_task_creation(self):
        """Test creating a task with valid data."""
        task = Task(
            task_name="Test Task",
            completed=False,
            due_date=datetime(2025, 12, 31, tzinfo=timezone.utc)
        )
        
        assert task.task_name == "Test Task"
        assert task.completed is False
        assert task.due_date == datetime(2025, 12, 31, tzinfo=timezone.utc)
        assert task.task_id is None
        assert isinstance(task.created_at, datetime)

    def test_task_name_validation(self):
        """Test task name validation."""
        # Empty task name should be cleaned up
        task = Task(task_name="  Test Task  ")
        assert task.task_name == "Test Task"
        
        # Empty string should raise error
        with pytest.raises(ValidationError):
            Task(task_name="")

    def test_is_completed(self):
        """Test is_completed method."""
        task = Task(task_name="Test", completed=True)
        assert task.is_completed() is True
        
        task.completed = False
        assert task.is_completed() is False

    def test_is_overdue(self):
        """Test is_overdue method."""
        # Task with future due date should not be overdue
        future_date = datetime(2026, 12, 31, tzinfo=timezone.utc)
        task = Task(task_name="Test", due_date=future_date)
        assert task.is_overdue() is False
        
        # Task with past due date should be overdue
        past_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        task = Task(task_name="Test", due_date=past_date)
        assert task.is_overdue() is True
        
        # Completed task should not be overdue
        task.completed = True
        assert task.is_overdue() is False
        
        # Task without due date should not be overdue
        task = Task(task_name="Test")
        assert task.is_overdue() is False

    def test_mark_completed(self):
        """Test mark_completed method."""
        task = Task(task_name="Test")
        assert task.completed is False
        
        task.mark_completed()
        assert task.completed is True