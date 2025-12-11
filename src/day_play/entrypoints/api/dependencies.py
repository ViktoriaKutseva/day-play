from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from day_play.business.achievement_manager import AchievementManager
from day_play.business.dashboard_service import DashboardService
from day_play.business.gamification_engine import GamificationEngine
from day_play.business.prize_manager import PrizeManager
from day_play.business.progress_tracker import ProgressTracker
from day_play.business.recurrence_engine import RecurrenceEngine
from day_play.business.task_manager import TaskManager
from day_play.integrations.database.database import SessionLocal
from day_play.integrations.database.repositories.achievement_repository import (
    SQLAlchemyAchievementRepository,
)
from day_play.integrations.database.repositories.daily_progress_repository import (
    SQLAlchemyDailyProgressRepository,
)
from day_play.integrations.database.repositories.prize_repository import (
    SQLAlchemyPrizeRepository,
)
from day_play.integrations.database.repositories.task_repository import (
    SQLAlchemyTaskRepository,
)
from day_play.integrations.database.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


def get_db() -> Generator[Session, None, None]:
    """Get a new database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_gamification_engine() -> GamificationEngine:
    """Get GamificationEngine instance."""
    return GamificationEngine()

def get_recurrence_engine() -> RecurrenceEngine:
    """Get RecurrenceEngine instance."""
    return RecurrenceEngine()

def get_task_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyTaskRepository:
    """Get TaskRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        SQLAlchemyTaskRepository: Repository for task operations
    """
    return SQLAlchemyTaskRepository(db)



def get_user_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyUserRepository:
    """Get UserRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        SQLAlchemyUserRepository: Repository for user operations
    """
    return SQLAlchemyUserRepository(db)


def get_daily_progress_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyDailyProgressRepository:
    """Get DailyProgressRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        SQLAlchemyDailyProgressRepository: Repository for daily progress operations
    """
    return SQLAlchemyDailyProgressRepository(db)


def get_achievement_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyAchievementRepository:
    """Get AchievementRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        SQLAlchemyAchievementRepository: Repository for achievement operations
    """
    return SQLAlchemyAchievementRepository(db)


def get_prize_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyPrizeRepository:
    """Get PrizeRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        SQLAlchemyPrizeRepository: Repository for prize operations
    """
    return SQLAlchemyPrizeRepository(db)


def get_progress_tracker(
    gamification: GamificationEngine = Depends(get_gamification_engine),
    task_repository: SQLAlchemyTaskRepository = Depends(get_task_repository),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    daily_progress_repository: SQLAlchemyDailyProgressRepository = Depends(
        get_daily_progress_repository
    ),
) -> ProgressTracker:
    """Get ProgressTracker instance.

    ProgressTracker calculates daily completion and level progression.

    Args:
        gamification: Engine for XP/level calculations
        task_repository: Repository for task data access
        user_repository: Repository for user data access
        daily_progress_repository: Repository for daily progress data access

    Returns:
        ProgressTracker: Configured progress tracking service
    """
    return ProgressTracker(
        gamification=gamification,
        task_repository=task_repository,
        user_repository=user_repository,
        daily_progress_repository=daily_progress_repository,
    )


def get_prize_manager(
    prize_repository: SQLAlchemyPrizeRepository = Depends(get_prize_repository),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> PrizeManager:
    """Get PrizeManager instance.

    PrizeManager handles prize creation, redemption, and availability checks.

    Args:
        prize_repository: Repository for prize data access
        user_repository: Repository for user data access

    Returns:
        PrizeManager: Configured prize management service
    """
    return PrizeManager(
        prize_repository=prize_repository,
        user_repository=user_repository,
    )



def get_achievement_manager(
    gamification: GamificationEngine = Depends(get_gamification_engine),
    task_repository: SQLAlchemyTaskRepository = Depends(get_task_repository),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    daily_progress_repository: SQLAlchemyDailyProgressRepository = Depends(
        get_daily_progress_repository
    ),
    achievement_repository: SQLAlchemyAchievementRepository = Depends(
        get_achievement_repository
    ),
    progress_tracker: ProgressTracker = Depends(get_progress_tracker),
) -> AchievementManager:
    """Get AchievementManager instance.

    AchievementManager handles achievement definitions, checking, and unlocking.
    
    IMPORTANT: AchievementManager depends on ProgressTracker for streak
    calculations. This is why ProgressTracker must be initialized first!

    Args:
        gamification: Engine for XP/level calculations
        task_repository: Repository for task data access
        user_repository: Repository for user data access
        daily_progress_repository: Repository for daily progress data access
        achievement_repository: Repository for achievement data access
        progress_tracker: Service for progress calculations

    Returns:
        AchievementManager: Configured achievement management service
    """
    return AchievementManager(
        gamification=gamification,
        task_repository=task_repository,
        user_repository=user_repository,
        daily_progress_repository=daily_progress_repository,
        achievement_repository=achievement_repository,
        progress_tracker=progress_tracker,
    )


# =============================================================================
# Level 4: TaskManager (Depends on AchievementManager)
# =============================================================================

def get_task_manager(
    task_repository: SQLAlchemyTaskRepository = Depends(get_task_repository),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    gamification: GamificationEngine = Depends(get_gamification_engine),
    recurrence: RecurrenceEngine = Depends(get_recurrence_engine),
    achievement_manager: AchievementManager = Depends(get_achievement_manager),
) -> TaskManager:
    """Get TaskManager instance.

    TaskManager is the main service for task operations including
    creation, completion, and recurrence handling.

    IMPORTANT: TaskManager depends on AchievementManager to check and
    unlock achievements when tasks are completed. This is why
    AchievementManager must be initialized first!

    Args:
        task_repository: Repository for task data access
        user_repository: Repository for user data access
        gamification: Engine for XP calculations
        recurrence: Engine for recurrence date calculations
        achievement_manager: Service for achievement checking

    Returns:
        TaskManager: Configured task management service
    """
    return TaskManager(
        task_repository=task_repository,
        user_repository=user_repository,
        gamification=gamification,
        recurrence=recurrence,
        achievement_manager=achievement_manager,
    )


# =============================================================================
# Level 5: DashboardService (Depends on TaskManager)
# =============================================================================

def get_dashboard_service(
    task_manager: TaskManager = Depends(get_task_manager),
    progress_tracker: ProgressTracker = Depends(get_progress_tracker),
    achievement_manager: AchievementManager = Depends(get_achievement_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> DashboardService:
    """Get DashboardService instance.

    DashboardService aggregates data from multiple services for the
    dashboard endpoint, keeping routes thin and schemas pure.

    Args:
        task_manager: Service for task operations
        progress_tracker: Service for progress calculations
        achievement_manager: Service for achievement operations
        gamification: Engine for XP/level calculations
        user_repository: Repository for user data access

    Returns:
        DashboardService: Configured dashboard aggregation service
    """
    return DashboardService(
        task_manager=task_manager,
        progress_tracker=progress_tracker,
        achievement_manager=achievement_manager,
        gamification=gamification,
        user_repository=user_repository,
    )
