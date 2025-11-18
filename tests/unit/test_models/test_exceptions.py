
import pytest

from day_play.models.exceptions import (
    AchievementNotFoundError,
    DomainException,
    InsufficientXPAError,
    InvalidPriorityError,
    InvalidRecurrenceError,
    InvalidTaskStatusError,
    InvalidUrgencyError,
    PrizeNotFoundError,
    TaskNotFoundError,
)


class TestDomainExceptions:
    def test_domain_exception_base(self):
        """Test that DomainException can be raised and caught."""
        with pytest.raises(DomainException):
            raise DomainException("Base domain exception")
    def test_invalid_priority_error_raised(self):
        with pytest.raises(InvalidPriorityError):
            raise InvalidPriorityError("Invalid priority error")
    def test_invalid_urgency_error_raised(self):
        with pytest.raises(InvalidUrgencyError):
            raise InvalidUrgencyError("Invalid urgency error")
    def test_invalid_task_status_error_raised(self):
        with pytest.raises(InvalidTaskStatusError):
            raise InvalidTaskStatusError("Invalid task status error")
    def test_invalid_recurrence_error_raised(self):
        with pytest.raises(InvalidRecurrenceError):
            raise InvalidRecurrenceError("Invalid recurrence error")
    def test_task_not_found_error_raised(self):
        with pytest.raises(TaskNotFoundError):
            raise TaskNotFoundError("Task not found error")
    def test_achievement_not_found_error_raised(self):
        with pytest.raises(AchievementNotFoundError):
            raise AchievementNotFoundError("Achievement not found error")
    def test_prize_not_found_error_raised(self):
        with pytest.raises(PrizeNotFoundError):
            raise PrizeNotFoundError("Prize not found error")
    def test_insufficient_xp_error_raised(self):
        with pytest.raises(InsufficientXPAError):
            raise InsufficientXPAError("Insufficient XP error")
    def test_exceptions_have_messages(self):
        """Test that exceptions carry the correct messages."""
        message = "Test exception message"
        with pytest.raises(DomainException) as exc_info:
            raise DomainException(message)
        assert str(exc_info.value) == message