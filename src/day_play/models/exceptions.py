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

class TaskAlreadyCompletedError(DomainException):
    """Raised when trying to complete already completed task"""

class TaskNotCompletedError(DomainException):
    """Raised when trying to undo a task that is not completed."""
    pass

class InsufficientXPError(DomainException):
    """Raised when user doesn't have enough XP to unlock a prize milestone."""
    pass

# Backwards-compatible alias (older tests expect InsufficientXPAError)
class InsufficientXPAError(InsufficientXPError):
    """Alias for InsufficientXPError for compatibility."""
    pass

class PrizeAlreadyRedeemedError(DomainException):
    """Raised when attempting to redeem a prize that has already been redeemed."""
    pass

class UserNotFoundError(DomainException):
    """Raised when a user is not found."""
    pass
