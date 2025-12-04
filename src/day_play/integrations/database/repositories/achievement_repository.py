from collections.abc import Callable

from sqlalchemy.orm import Session
from sqlmodel import select

from day_play.integrations.database.models import Achievement as AchievementORM
from day_play.models.entities import Achievement as DomainAchievement
from day_play.models.exceptions import AchievementNotFoundError


class SQLAlchemyAchievementRepository:
    def __init__(self, session: Session):
        self._session = session

    @staticmethod
    def _to_domain(orm_achievement: AchievementORM) -> DomainAchievement:
        return DomainAchievement(
            id=orm_achievement.id,
            name=orm_achievement.name,
            description=orm_achievement.description,
            icon=orm_achievement.icon,
            unlock_criteria = orm_achievement.unlock_criteria,
            unlocked_at=orm_achievement.unlocked_at,
            user_id=orm_achievement.user_id,
            created_at=orm_achievement.created_at,
        )

    @staticmethod
    def _to_orm(domain_achievement: DomainAchievement) -> AchievementORM:
        return AchievementORM(
            id=domain_achievement.id,
            name=domain_achievement.name,
            description=domain_achievement.description or "",
            icon=domain_achievement.icon,
            unlock_criteria=domain_achievement.unlock_criteria or {},
            unlocked_at=domain_achievement.unlocked_at,
            user_id=domain_achievement.user_id,
        )

    def create(self, achievement: DomainAchievement) -> DomainAchievement:
        """Create a new achievement."""
        orm_achievement = self._to_orm(achievement)
        self._session.add(orm_achievement)
        self._session.commit()
        self._session.refresh(orm_achievement)
        return self._to_domain(orm_achievement)

    def get_by_id(self, achievement_id: int) -> DomainAchievement | None:
        """Get achievement by ID."""
        orm_achievement = self._session.get(AchievementORM, achievement_id)
        if orm_achievement is None:
            return None
        return self._to_domain(orm_achievement)

    def get_by_user_id(self, user_id: int) -> list[DomainAchievement]:
        """Get all achievements for a user."""

        stmt = select(AchievementORM).where(AchievementORM.user_id == user_id)
        orm_achievements = self._session.execute(stmt).scalars().all()
        return [self._to_domain(orm_achievement) for orm_achievement in orm_achievements]
    def get_unlocked(self, user_id: int) -> list[DomainAchievement]:
        """
        Get unlocked achievements for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of unlocked achievements
        """
        stmt = select(AchievementORM).where(
            AchievementORM.user_id == user_id,
            AchievementORM.unlocked_at.isnot(None))  # type: ignore[union-attr]
        orm_achievements = self._session.execute(stmt).scalars().all()
        return [self._to_domain(orm_achievement) for orm_achievement in orm_achievements]

    def update(self, achievement: DomainAchievement) -> DomainAchievement:
        """Update existing achievement."""
        orm_achievement = self._session.get(AchievementORM, achievement.id)
        if orm_achievement is None:
            raise AchievementNotFoundError(f"Achievement with ID {achievement.id} not found.")
        orm_achievement.name = achievement.name
        orm_achievement.description = achievement.description or ''
        orm_achievement.icon = achievement.icon
        orm_achievement.unlock_criteria = achievement.unlock_criteria or {}
        orm_achievement.unlocked_at = achievement.unlocked_at
        self._session.commit()
        self._session.refresh(orm_achievement)
        return self._to_domain(orm_achievement)

    def delete(self, achievement_id: int) -> None:
        """Delete achievement by ID."""
        orm_achievement = self._session.get(AchievementORM, achievement_id)
        if orm_achievement is None:
            raise AchievementNotFoundError(f"Achievement with ID {achievement_id} not found.")
        self._session.delete(orm_achievement)
        self._session.commit()