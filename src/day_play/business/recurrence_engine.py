"""
Recurrence Engine for Day-Play Task Management

Calculates next occurrence dates for recurring tasks with proper edge case handling:
- Daily, weekly, and monthly recurrence patterns
- Month-end date normalization (e.g., Jan 31 → Feb 28/29)
- Leap year handling via dateutil.relativedelta
- Timezone-aware calculations using UTC
- Support for on_complete pattern (task recurs only after completion)

All functions follow immutability pattern - returning new Task objects
without mutating inputs.
"""

from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

from day_play.models.entities import Task
from day_play.models.enums import RecurrencePattern

class RecurrenceEngine:
    """Engine for calculating next occurrence dates for recurring tasks."""

    def __init__(self) -> None:
        pass

    def _calculate_next_date(self, date: datetime, recurrence: RecurrencePattern) -> datetime | None:
        """Calculate next occurrence date from base date using recurrence pattern.

        Uses dateutil.relativedelta for proper date arithmetic that handles:
        - Month-end dates (Jan 31 + 1 month = Feb 28/29)
        - Leap years (Feb 29 + 1 month = Mar 29)
        - Year boundaries (Dec 31 + 1 month = Jan 31 next year)

        Args:
            base_date: Starting datetime (timezone-aware UTC)
            pattern: Recurrence pattern enum

        Returns:
            Next occurrence datetime, or None for NONE pattern

        Raises:
            ValueError: If pattern is not a valid RecurrencePattern enum
        """
        if recurrence == RecurrencePattern.NONE:
            return None
        elif recurrence == RecurrencePattern.DAILY:
            return date + relativedelta(days=1)
        elif recurrence == RecurrencePattern.WEEKLY:
            return date + relativedelta(weeks=1)
        elif recurrence == RecurrencePattern.MONTHLY:
            return date + relativedelta(months=1)
        else:
            raise ValueError(f"Invalid recurrence pattern: {recurrence}")

    def calculate_next_occurrence(self,task: Task) -> Task:
        """
            Calculate the next occurrence date for a recurring task.

            Returns a new Task object with updated next_occurrence field.
            Does not mutate the input task (follows immutability pattern).

            Behavior by recurrence pattern:
            - NONE: Returns task with next_occurrence = None
            - DAILY: Adds 1 day to base date
            - WEEKLY: Adds 7 days to base date
            - MONTHLY: Adds 1 month to base date (handles month-end dates properly)

            Base date selection:
            - If recurrence_rule_on_complete is False: Uses current UTC time
            - If recurrence_rule_on_complete is True and task not completed: Returns task unchanged
            - If recurrence_rule_on_complete is True and task completed: Uses completed_at timestamp

            Edge cases handled:
            - Month-end dates: Jan 31 + 1 month = Feb 28/29 (last day of shorter month)
            - Leap years: Feb 29 + 1 month = Mar 29
            - Year boundaries: Dec 31 + 1 month = Jan 31 (next year)

            Args:
                task: Task entity with recurrence settings

            Returns:
                New Task object with calculated next_occurrence field

            Raises:
                ValueError: If recurrence_pattern is not a valid RecurrencePattern enum (via _calculate_next_date)
        """

        if task.recurrence_pattern == RecurrencePattern.NONE:
            return task.model_copy(update={"next_occurrence": None})
        if task.recurrence_rule_on_complete:
            if not task.is_completed() or task.completed_at is None:
                return task
            base_date = task.completed_at
        else:
            base_date = datetime.now(timezone.utc)

        next_date = self._calculate_next_date(base_date, task.recurrence_pattern)
        return task.model_copy(update={"next_occurrence": next_date})
