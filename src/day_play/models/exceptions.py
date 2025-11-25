"""Domain-specific exceptions for the Day-Play application."""

class DomainException(Exception):
    """Base class for domain exceptions."""
    pass

class InvalidPriorityError(DomainException):
    """Raised when task priority is invalid."""
    pass

class InvalidUrgencyError(DomainException):
    """Raised when task urgency is invalid."""
    pass

class InvalidTaskStatusError(DomainException):
    """Raised when task status is invalid."""
    pass

class InvalidRecurrenceError(DomainException):
    """Raised when recurrence pattern is invalid."""
    pass

class TaskNotFoundError(DomainException):
    """Raised when a task is not found."""
    pass

class AchievementNotFoundError(DomainException):
    """Raised when an achievement is not found."""
    pass

class PrizeNotFoundError(DomainException):
    """Raised when a prize is not found."""
    pass

class InsufficientXPAError(DomainException):
    """Raised when user doesn't have enough XP for an action."""
    pass

class TaskAlreadyCompletedError(DomainException):
    """Raised when trying to complete already completed task"""

class TaskNotCompletedError(DomainException):
    """Raised when trying to undo a task that is not completed."""
    pass