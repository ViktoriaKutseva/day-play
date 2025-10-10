"""Domain exceptions for the Day Play application."""


class DayPlayException(Exception):
    """Base exception for Day Play application."""
    pass


class TaskNotFoundError(DayPlayException):
    """Exception raised when a task is not found."""
    pass


class InvalidTaskDataError(DayPlayException):
    """Exception raised when task data is invalid."""
    pass