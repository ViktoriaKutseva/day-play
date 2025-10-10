"""Domain exceptions for the task management system."""


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class TaskValidationError(Exception):
    """Raised when task validation fails."""
    pass


class TaskOperationError(Exception):
    """Raised when a task operation fails."""
    pass