"""Unit tests for models."""
import pytest
from datetime import datetime, timezone

from src.day_play.models.entities import Task, TaskCreate, TaskUpdate


class TestTask:
    """Test Task entity."""

    def test_task_creation(self):
        """Test creating a valid task."""
        task_data = {
            "task_name": "Test Task",
            "completed": False,
            "due_date": datetime(2025, 10, 1, tzinfo=timezone.utc)
        }
        task = Task(**task_data)

        assert task.task_name == "Test Task"
        assert task.completed is False
        assert task.due_date == datetime(2025, 10, 1, tzinfo=timezone.utc)
        assert task.created_at is not None

    def test_task_name_validation(self):
        """Test task name validation."""
        # Valid task name
        task = Task(task_name="Valid Task")
        assert task.task_name == "Valid Task"

        # Empty task name should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            Task.model_validate({"task_name": ""})

        with pytest.raises(Exception):
            Task.model_validate({"task_name": "   "})


class TestTaskCreate:
    """Test TaskCreate DTO."""

    def test_task_create_validation(self):
        """Test TaskCreate validation."""
        # Valid creation
        task_create = TaskCreate(task_name="New Task", completed=True)
        assert task_create.task_name == "New Task"
        assert task_create.completed is True

        # Invalid task name
        with pytest.raises(Exception):
            TaskCreate(task_name="")


class TestTaskUpdate:
    """Test TaskUpdate DTO."""

    def test_task_update_partial(self):
        """Test partial task updates."""
        # Update only task name
        update = TaskUpdate.model_validate({"task_name": "Updated Task"})
        assert update.task_name == "Updated Task"
        assert update.completed is None
        assert update.due_date is None

        # Update only completion status
        update = TaskUpdate.model_validate({"completed": True})
        assert update.task_name is None
        assert update.completed is True
        assert update.due_date is None