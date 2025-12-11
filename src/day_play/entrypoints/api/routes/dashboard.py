from fastapi import APIRouter, Depends, HTTPException, Query

from day_play.business.dashboard_service import DashboardService
from day_play.business.gamification_engine import GamificationEngine
from day_play.entrypoints.api.dependencies import (
    get_dashboard_service,
    get_gamification_engine,
    get_user_repository,
)
from day_play.entrypoints.api.schemas.dashboard_schema import (
    DashboardResponse,
    UserLevelResponse,
)
from day_play.integrations.database.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

router = APIRouter(prefix="/api", tags=["dashboard"])

# - GET /api/dashboard - Returns dual progress bars, upcoming tasks, recent achievements
# - GET /api/user/level - Returns current level, XP, progress to next level
# - Efficient queries (minimize database calls)
# - Proper data aggregation


@router.get("/user/level", response_model=UserLevelResponse)
def get_user_level(
    user_id: int = Query(default=1, description="User ID"),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> UserLevelResponse:
    """Get current level, XP, and progress to next level."""
    user = user_repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    level_data = dashboard_service.get_user_level_data(user)
    return UserLevelResponse.from_data(level_data)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    user_id: int = Query(default=1, description="User ID"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    gamification: GamificationEngine = Depends(get_gamification_engine),
) -> DashboardResponse:
    """Get all dashboard data in single request."""
    data = dashboard_service.get_dashboard_data(user_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")

    return DashboardResponse.from_data(data, gamification)

