from day_play.models.entities import Task
from day_play.models.enums import Priority, Urgency
from day_play.models.exceptions import (
    InvalidPriorityError,
    InvalidUrgencyError,
)


class GamificationEngine:
    """Engine for calculating XP and levels based on tasks."""

    def __init__(self) -> None:
        pass

    def calculate_xp(self, task: Task) -> int:
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


    def calculate_level(self, total_xp: int) -> int:
        """Calculate user level based on total accumulated XP."""
        if total_xp < 0:
            raise ValueError("Total XP cannot be negative")

        level = 1
        while level < 1000:
            xp_needed_for_next = self.xp_for_level(level + 1)
            if total_xp < xp_needed_for_next:
                return level
            level += 1
        return level

    def xp_for_level(self, level: int) -> int:
        """Calculate total XP required to reach a specific level.

        Uses exponential formula with diminishing returns:
        - Levels 1-20: Moderate growth (exponent 1.5)
        - Levels 21-50: Slower growth (exponent 1.3)
        - Levels 51+: Very slow growth (exponent 1.1)

        Args:
            level: Target level (must be >= 1)

        Returns:
            Total cumulative XP required to reach the specified level
        """

        if level < 1:
            raise ValueError('Level must be a positive integer')
        base_xp = 100
        if level <= 20:
            return int(base_xp * ((level - 1) ** 1.5))
        elif level <= 50:
            level_20_xp = int(base_xp * ((20 - 1) ** 1.5))
            additional = int(base_xp * ((level - 20) ** 1.3) * 1.8)
            return level_20_xp + additional
        else:
            level_20_xp = int(base_xp * ((20 - 1) ** 1.5))
            level_21_to_50_xp = int(base_xp * ((50 - 20) ** 1.3) * 1.8)
            level_50_xp = level_20_xp + level_21_to_50_xp
            additional = int(base_xp * ((level - 50) ** 1.1) * 3.5)
            return level_50_xp + additional

    def xp_for_next_level(self, current_xp: int) -> int:
        """Calculate XP remaining to reach the next level from current XP.

        Args:
            current_xp: User's current total accumulated XP

        Returns:
            Number of XP points needed to reach the next level

        Example:
            If current_xp=100 and level 2 requires 282 total XP,
            this returns 282 - 100 = 182 XP remaining.
        """
        current_level = self.calculate_level(current_xp)
        next_level_xp = self.xp_for_level(current_level + 1)
        return next_level_xp - current_xp


game = GamificationEngine()
print(game.xp_for_level(3))