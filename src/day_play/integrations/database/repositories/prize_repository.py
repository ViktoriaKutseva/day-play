from collections.abc import Callable

from sqlalchemy.orm import Session
from sqlmodel import select

from day_play.integrations.database.models import Prize as PrizeORM
from day_play.models.entities import Prize as DomainPrize
from day_play.models.exceptions import PrizeNotFoundError

class SQLAlchemyPrizeRepository:
    def __init__(self, session: Session):
        self._session = session

    @staticmethod
    def _to_domain(orm_prize: PrizeORM) -> DomainPrize:
        return DomainPrize(
            id=orm_prize.id,
            name=orm_prize.name,
            description=orm_prize.description,
            cost_xp=orm_prize.cost_xp,
            redeemed=orm_prize.redeemed,
            redeemed_at=orm_prize.redeemed_at,
            user_id=orm_prize.user_id,
        )

    @staticmethod
    def _to_orm(domain_prize: DomainPrize) -> PrizeORM:
        return PrizeORM(
            id=domain_prize.id,
            name=domain_prize.name,
            description=domain_prize.description or "",
            cost_xp=domain_prize.cost_xp,
            redeemed=domain_prize.redeemed,
            redeemed_at=domain_prize.redeemed_at,
            user_id=domain_prize.user_id,
        )

    def create(self, prize: DomainPrize) -> DomainPrize:
        """Create a new prize."""
        orm_prize = self._to_orm(prize)
        self._session.add(orm_prize)
        self._session.commit()
        self._session.refresh(orm_prize)
        return self._to_domain(orm_prize)

    def get_by_id(self, prize_id: int) -> DomainPrize | None:
        """Get prize by ID."""
        orm_prize = self._session.get(PrizeORM, prize_id)
        if orm_prize is None:
            return None
        return self._to_domain(orm_prize)

    def get_by_user_id(self, user_id: int) -> list[DomainPrize]:
        """Get all prizes for a user."""
        stmt = select(PrizeORM).where(PrizeORM.user_id == user_id)
        orm_prizes = self._session.execute(stmt).scalars().all()
        return [self._to_domain(orm_prize) for orm_prize in orm_prizes]

    def get_available(self, user_id: int) -> list[DomainPrize]:
        """
        Get available (not redeemed) prizes for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of available prizes
        """
        stmt = select(PrizeORM).where(
            PrizeORM.user_id == user_id,
            PrizeORM.redeemed == False,  # noqa: E712
        )
        orm_prizes = self._session.execute(stmt).scalars().all()
        return [self._to_domain(orm_prize) for orm_prize in orm_prizes]

    def get_redeemed(self, user_id: int) -> list[DomainPrize]:
        """
        Get redeemed prizes for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of redeemed prizes
        """
        stmt = select(PrizeORM).where(
            PrizeORM.user_id == user_id,
            PrizeORM.redeemed == True,  # noqa: E712
        )
        orm_prizes = self._session.execute(stmt).scalars().all()
        return [self._to_domain(orm_prize) for orm_prize in orm_prizes]

    def update(self, prize: DomainPrize) -> DomainPrize:
        """Update existing prize."""
        if prize.id is None:
            raise ValueError("Prize ID must be provided for update.")

        orm_prize = self._session.get(PrizeORM, prize.id)
        if orm_prize is None:
            raise ValueError(f"Prize with ID {prize.id} not found.")
        orm_prize.name = prize.name
        orm_prize.description = prize.description or ""
        orm_prize.cost_xp = prize.cost_xp
        orm_prize.redeemed = prize.redeemed
        orm_prize.redeemed_at = prize.redeemed_at
        orm_prize.user_id = prize.user_id
        self._session.commit()
        self._session.refresh(orm_prize)
        return self._to_domain(orm_prize)

    def delete(self, prize_id: int) -> None:
        """Delete prize by ID."""
        orm_prize = self._session.get(PrizeORM, prize_id)
        if orm_prize is None:
            raise PrizeNotFoundError(f"Prize with ID {prize_id} not found.")
        self._session.delete(orm_prize)
        self._session.commit()