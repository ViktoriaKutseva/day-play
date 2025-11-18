from day_play.models.entities import Task
from day_play.models.enums import Priority, Urgency
from day_play.models.exceptions import InvalidPriorityError, InvalidUrgencyError


def calculate_xp(task: Task) -> int:
    """Calculate XP for the task based on its attributes."""
    if task.custom_xp is not None:
        return task.custom_xp

    # Validate enum values
    if task.urgency not in Urgency:
        raise InvalidUrgencyError(f"Invalid urgency value: {task.urgency}")
    if task.priority not in Priority:
        raise InvalidPriorityError(f"Invalid priority value: {task.priority}")

    xp_matrix = {
        (Urgency.LOW, Priority.LOW): 5,
        (Urgency.LOW, Priority.MEDIUM): 10,
        (Urgency.LOW, Priority.HIGH): 15,
        (Urgency.MEDIUM, Priority.LOW): 10,
        (Urgency.MEDIUM, Priority.MEDIUM): 20,
        (Urgency.MEDIUM, Priority.HIGH): 30,
        (Urgency.HIGH, Priority.LOW): 15,
        (Urgency.HIGH, Priority.MEDIUM): 30,
        (Urgency.HIGH, Priority.HIGH): 50,
    }
    total_xp = xp_matrix.get((task.urgency, task.priority))
    if total_xp is None:
        raise ValueError(
            f"Invalid urgency-priority combination: {task.urgency}, {task.priority}"
        )
    return total_xp
