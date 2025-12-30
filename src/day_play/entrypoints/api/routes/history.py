# - GET /api/history - Get progress for date range (default: last 30 days)
# - GET /api/history/{date} - Get specific day detail with completed tasks
# - Pagination support for large date ranges
# - Efficient date-based queries
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query

from day_play.business.progress_tracker import ProgressTracker
from day_play.entrypoints.api.dependencies import (
    get_daily_progress_repository,
    get_progress_tracker,
)
from day_play.entrypoints.api.schemas.history_schema import (
    DailyProgressResponse,
    HistoryResponse,
)
from day_play.integrations.database.repositories.daily_progress_repository import (
    SQLAlchemyDailyProgressRepository,
)

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/", response_model=HistoryResponse)
def get_history(
    user_id: int = Query(description="User ID"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to retrieve"),
    progress_tracker: ProgressTracker = Depends(get_progress_tracker),
) -> HistoryResponse:
    """Get progress history for a date range.

    Args:
        user_id: The user's ID
        days: Number of days to retrieve (default: 30, max: 365)
        progress_tracker: Injected progress tracker service

    Returns:
        History response with daily progress entries and aggregated stats
    """
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days - 1)

    progress_entries = progress_tracker.get_simple_history(user_id, limit=days)

    return HistoryResponse.from_entries(start_date, end_date, progress_entries)


@router.get("/{history_date}", response_model=DailyProgressResponse)
def get_history_by_date(
    history_date: date,
    user_id: int = Query(description="User ID"),
    daily_progress_repository: SQLAlchemyDailyProgressRepository = Depends(
        get_daily_progress_repository
    ),
) -> DailyProgressResponse:
    """Get progress for a specific date.

    Args:
        history_date: The date to get progress for
        user_id: The user's ID
        daily_progress_repository: Injected daily progress repository

    Returns:
        Daily progress for the specified date
    """
    progress = daily_progress_repository.get_progress_by_date(user_id, history_date)

    if not progress:
        return DailyProgressResponse.empty(history_date)

    return DailyProgressResponse.from_entity(progress)
