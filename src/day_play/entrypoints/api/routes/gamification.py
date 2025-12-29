
from fastapi import APIRouter, Depends, HTTPException, Query

from day_play.business.achievement_manager import AchievementManager
from day_play.business.prize_manager import PrizeManager
from day_play.entrypoints.api.dependencies import (
    get_achievement_manager,
    get_prize_manager,
    get_user_repository,
)
from day_play.entrypoints.api.schemas.achievement_schema import AchievementResponse
from day_play.entrypoints.api.schemas.prize_schema import PrizeCreate, PrizeResponse
from day_play.integrations.database.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from day_play.models.exceptions import (
    InsufficientXPError,
    PrizeAlreadyRedeemedError,
    PrizeNotFoundError,
)

router = APIRouter(prefix="/api/gamification", tags=["gamification"])

@router.post("/prizes", response_model=PrizeResponse, status_code=201)
def create_prize(
    prize_data: PrizeCreate,
    user_id: int = Query(default=1, description="User ID"),
    prize_manager: PrizeManager = Depends(get_prize_manager),
) -> PrizeResponse:
    """Create a new prize."""
    prize = prize_data.to_entity(user_id=user_id)
    created_prize = prize_manager.create_prize(prize)
    return PrizeResponse.from_entity(created_prize)

@router.post("/prizes/{prize_id}/redeem", response_model=PrizeResponse, status_code=200)
def redeem_prize(
    prize_id: int,
    user_id: int = Query(default=1, description="User ID"),
    prize_manager: PrizeManager = Depends(get_prize_manager),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> PrizeResponse:
    """Redeem a prize (milestone unlock)."""
    user = user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    try:
        redeemed_prize = prize_manager.redeem_prize(prize_id, user_id)
        return PrizeResponse.from_entity(redeemed_prize, user.total_xp)
    except PrizeNotFoundError:
        raise HTTPException(status_code=404, detail="Prize not found")
    except PrizeAlreadyRedeemedError:
        raise HTTPException(status_code=400, detail="Prize already redeemed")
    except InsufficientXPError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/achievements", response_model=list[AchievementResponse])
def get_achievements(
    user_id: int = Query(default=1, description="User ID"),
    is_unlocked: bool | None = Query(default=None, description="Filter by unlock status"),
    achievement_manager: AchievementManager = Depends(get_achievement_manager),
) -> list[AchievementResponse]:
    """List achievements for a user.

    Args:
        user_id: The user's ID
        is_unlocked: Optional filter - True for unlocked, False for available, None for all
        achievement_manager: Injected achievement manager service

    Returns:
        List of achievements matching the filter criteria
    """
    if is_unlocked is True:
        achievements = achievement_manager.get_unlocked_achievements(user_id)
    elif is_unlocked is False:
        achievements = achievement_manager.get_available_achievements(user_id)
    else:
        # Return all: unlocked + available definitions
        unlocked = achievement_manager.get_unlocked_achievements(user_id)
        available = achievement_manager.get_available_achievements(user_id)
        achievements = unlocked + available

    return [AchievementResponse.from_entity(ach) for ach in achievements]

@router.get("/prizes", response_model=list[PrizeResponse])
def get_prizes(
    user_id: int = Query(default=1, description="User ID"),
    is_redeemed: bool = Query(default=False, description="Filter by redeemed status"),
    prize_manager: PrizeManager = Depends(get_prize_manager),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> list[PrizeResponse]:
    """List prizes for a user.

    Args:
        user_id: The user's ID
        is_redeemed: Filter by redeemed status
        prize_manager: Injected prize manager service
        user_repository: Injected user repository

    Returns:
        List of prizes matching the filter criteria
    """
    user = user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if is_redeemed is True:
        prizes = prize_manager.list_redeemed_prizes(user_id)
    elif is_redeemed is False:
        prizes = prize_manager.list_available_prizes(user_id)
    else:
        prizes = prize_manager.list_available_prizes(user_id) + prize_manager.list_redeemed_prizes(user_id)

    return [PrizeResponse.from_entity(prize, user.total_xp) for prize in prizes]
