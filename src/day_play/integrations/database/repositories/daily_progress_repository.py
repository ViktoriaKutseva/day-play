from collections.abc import Callable
from datetime import date

from sqlalchemy.orm import Session
from sqlmodel import select

from day_play.integrations.database.models import DailyProgress as DailyProgressORM
from day_play.models.entities import DailyProgress as DomainDailyProgress


class SQLAlchemyDailyProgressRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(orm_daily_progress: DailyProgressORM) -> DomainDailyProgress:
        return DomainDailyProgress(
            id=orm_daily_progress.id,
            date=orm_daily_progress.date,
            tasks_completed=orm_daily_progress.tasks_completed,
            tasks_total=orm_daily_progress.tasks_total,
            completion_percentage=orm_daily_progress.completion_percentage,
            daily_xp_earned=orm_daily_progress.daily_xp_earned,
            user_id=orm_daily_progress.user_id,
        )
    @staticmethod
    def _to_orm(domain_daily_progress: DomainDailyProgress) -> DailyProgressORM:
        return DailyProgressORM(
            id=domain_daily_progress.id,
            date=domain_daily_progress.date,
            tasks_completed=domain_daily_progress.tasks_completed,
            tasks_total=domain_daily_progress.tasks_total,
            completion_percentage=domain_daily_progress.completion_percentage,
            daily_xp_earned=domain_daily_progress.daily_xp_earned,
            user_id=domain_daily_progress.user_id,
        )

    def create_or_update_progress(self, progress: DomainDailyProgress) -> DomainDailyProgress:
        """Create or update daily progress for a user.
        Args:
            progress: DailyProgress entity to create or update
        Returns:
            Created or updated DailyProgress
        """
        with self._session_factory() as session:
            stmt = select(DailyProgressORM).where(
                DailyProgressORM.user_id == progress.user_id,
                DailyProgressORM.date == progress.date,
            )
            orm_progress = session.execute(stmt).scalar_one_or_none()
            if orm_progress:
                # Update existing record
                orm_progress.tasks_completed = progress.tasks_completed
                orm_progress.tasks_total = progress.tasks_total
                orm_progress.completion_percentage = progress.completion_percentage
                orm_progress.daily_xp_earned = progress.daily_xp_earned
            else:
                # Create new record
                orm_progress = self._to_orm(progress)
                session.add(orm_progress)
            session.commit()
            session.refresh(orm_progress)
            return self._to_domain(orm_progress)
    def get_progress_by_date(self, user_id: int, date_progress: date) -> DomainDailyProgress | None:
        """Retrieve daily progress for a user by date.
        Args:
            user_id: ID of the user
            date_progress: Date of the progress to retrieve
        Returns:
            DailyProgress for the given user and date, or None if not found
        """
        with self._session_factory() as session:
            stmt = select(DailyProgressORM).where(
                DailyProgressORM.user_id == user_id,
                DailyProgressORM.date == date_progress,
            )
            orm_progress = session.execute(stmt).scalar_one_or_none()
            if orm_progress is None:
                return None
            return self._to_domain(orm_progress)
    def get_date_range(self, user_id: int, start_date: date, end_date: date) -> list[DomainDailyProgress]:
        """Retrieve daily progress for a user within a date range.
        Args:
            user_id: ID of the user
            start_date: Start date of the range
            end_date: End date of the range
        Returns:
            List of DailyProgress entries for the given user within the date range
        """
        with self._session_factory() as session:
            stmt = select(DailyProgressORM).where(
                DailyProgressORM.user_id == user_id,
                DailyProgressORM.date >= start_date,
                DailyProgressORM.date <= end_date,
            )
            orm_progress_list = session.execute(stmt).scalars().all()
            return [self._to_domain(orm_progress) for orm_progress in orm_progress_list]
