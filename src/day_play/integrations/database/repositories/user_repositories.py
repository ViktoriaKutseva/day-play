from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from day_play.integrations.database.models import User as UserORM
from day_play.models.entities import User as DomainUser
from day_play.models.exceptions import UserNotFoundError


class SQLAlchemyUserRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory



    @staticmethod
    def _to_domain(orm_user: UserORM) -> DomainUser:
        return DomainUser(
            id=orm_user.id,
            username=orm_user.username,
            current_level=orm_user.current_level,
            total_xp=orm_user.total_xp,
            created_at=orm_user.created_at,
            updated_at=orm_user.updated_at,
        )

    @staticmethod
    def _to_orm(domain_user: DomainUser) -> UserORM:
        now = datetime.now(timezone.utc)
        return UserORM(
            id=domain_user.id,
            username=domain_user.username,
            current_level=domain_user.current_level,
            total_xp=domain_user.total_xp,
            created_at=domain_user.created_at or now,
            updated_at=domain_user.updated_at or now,
        )

    def create(self, user: DomainUser) -> DomainUser:
        """Create a new user."""
        with self._session_factory() as session:
            orm_user = self._to_orm(user)
            session.add(orm_user)
            session.commit()
            session.refresh(orm_user)
            return self._to_domain(orm_user)

    def get_by_id(self, user_id: int) -> DomainUser | None:
        """Get user by ID."""
        with self._session_factory() as session:
            orm_user = session.get(UserORM, user_id)
            if orm_user is None:
                return None
            return self._to_domain(orm_user)

    def update(self, user: DomainUser) -> DomainUser:
        """Update existing user."""
        if user.id is None:
            raise ValueError("User ID must be provided for update.")

        with self._session_factory() as session:
            orm_user = session.get(UserORM, user.id)
            if orm_user is None:
                raise UserNotFoundError(f"User with ID {user.id} not found.")
            orm_user.username = user.username
            orm_user.current_level = user.current_level
            orm_user.total_xp = user.total_xp
            orm_user.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(orm_user)
            return self._to_domain(orm_user)

    def update_xp(self, user_id: int, xp_delta: int) -> DomainUser:
        """
        Update user's total XP.

        Args:
            user_id: User's unique identifier
            xp_delta: XP amount to add (can be negative for deductions)

        Returns:
            Updated user
        """
        with self._session_factory() as session:
            orm_user = session.get(UserORM, user_id)
            if orm_user is None:
                raise UserNotFoundError(f"User with ID {user_id} not found.")
            orm_user.total_xp += xp_delta
            orm_user.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(orm_user)
            return self._to_domain(orm_user)

    def update_level(self, user_id: int, new_level: int) -> DomainUser:
        """
        Update user's level.

        Args:
            user_id: User's unique identifier
            new_level: New level value

        Returns:
            Updated user
        """
        with self._session_factory() as session:
            orm_user = session.get(UserORM, user_id)
            if orm_user is None:
                raise UserNotFoundError(f"User with ID {user_id} not found.")
            orm_user.current_level = new_level
            orm_user.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(orm_user)
            return self._to_domain(orm_user)
