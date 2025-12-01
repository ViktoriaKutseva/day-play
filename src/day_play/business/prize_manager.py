from datetime import datetime

from loguru import logger

from day_play.business.interfaces import PrizeRepository, UserRepository
from day_play.models.entities import Prize
from day_play.models.exceptions import (
    InsufficientXPError,
    PrizeAlreadyRedeemedError,
    PrizeNotFoundError,
    UserNotFoundError,
)


class PrizeManager:
    def __init__(
        self, prize_repository: PrizeRepository, user_repository: UserRepository
    ):
        self._prize_repository = prize_repository
        self._user_repository = user_repository

    def create_prize(
        self, name: str, description: str, cost_xp: int, user_id: int
    ) -> Prize:
        """Create a new prize with validation.

        Args:
            name: Prize name
            description: Prize description
            cost_xp: XP threshold required to unlock this prize
            user_id: ID of the user creating the prize

        Returns:
            Created prize entity

        Raises:
            ValueError: If cost_xp is invalid
        """
        # Validate XP threshold
        if cost_xp <= 0:
            logger.error(f"Invalid cost_xp: {cost_xp}. Must be greater than 0.")
            raise ValueError("Prize XP threshold must be greater than 0")

        if cost_xp > 100000:
            logger.error(f"Invalid cost_xp: {cost_xp}. Exceeds maximum of 100,000 XP.")
            raise ValueError("Prize XP threshold cannot exceed 100,000")

        logger.info(
            f"Creating prize: name={name}, cost_xp={cost_xp}, user_id={user_id}"
        )
        prize = Prize(
            name=name,
            description=description,
            cost_xp=cost_xp,
            redeemed=False,
            user_id=user_id,
        )
        created_prize = self._prize_repository.create(prize)
        logger.info(f"Created prize: {created_prize}")
        return created_prize

    def redeem_prize(self, prize_id: int, user_id: int) -> Prize:
        """Redeem a prize (unlock milestone reward).

        Prizes work as milestone unlocks, not purchases. When a user reaches
        the XP threshold, they can redeem the prize without losing XP.

        Args:
            prize_id: ID of the prize to redeem
            user_id: ID of the user redeeming the prize

        Returns:
            Updated prize entity with redeemed status

        Raises:
            PrizeNotFoundError: If prize doesn't exist or doesn't belong to user
            UserNotFoundError: If user doesn't exist
            PrizeAlreadyRedeemedError: If prize was already redeemed
            InsufficientXPError: If user hasn't reached XP threshold
        """
        # Check if prize exists and belongs to user
        prize = self._prize_repository.get_by_id(prize_id)
        if not prize or prize.user_id != user_id:
            logger.warning(f"Prize not found: prize_id={prize_id}, user_id={user_id}")
            raise PrizeNotFoundError(
                f"Prize with ID {prize_id} not found for user {user_id}"
            )

        # Check if user exists
        user = self._user_repository.get_by_id(user_id)
        if not user:
            logger.error(f"User not found: user_id={user_id}")
            raise UserNotFoundError(f"User with ID {user_id} not found")

        # Check if prize already redeemed
        if prize.redeemed:
            logger.warning(
                f"Prize already redeemed: prize_id={prize_id}, user_id={user_id}"
            )
            raise PrizeAlreadyRedeemedError(
                f"Prize '{prize.name}' has already been redeemed"
            )

        # Check if user has reached XP threshold (milestone unlock, not purchase)
        if user.total_xp < prize.cost_xp:
            logger.info(
                f"Insufficient XP to unlock prize: prize_id={prize_id}, user_id={user_id}, "
                f"required={prize.cost_xp}, current={user.total_xp}"
            )
            raise InsufficientXPError(
                f"Need {prize.cost_xp} XP to unlock '{prize.name}' (current: {user.total_xp} XP)"
            )

        # Mark prize as redeemed (no XP deduction - this is a milestone unlock!)
        prize.redeemed = True
        prize.redeemed_at = datetime.now()
        updated_prize = self._prize_repository.update(prize)
        logger.info(
            f"Prize unlocked: prize_id={prize_id}, user_id={user_id}, prize_name={prize.name}, "
            f"user_xp={user.total_xp}"
        )
        return updated_prize

    def list_available_prizes(self, user_id: int) -> list[Prize]:
        """List all available (not redeemed) prizes for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of available prizes
        """
        return self._prize_repository.get_available(user_id)

    def list_redeemed_prizes(self, user_id: int) -> list[Prize]:
        """List all redeemed prizes for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of redeemed prizes
        """
        return self._prize_repository.get_redeemed(user_id)

    def can_redeem_prize(self, prize_id: int, user_id: int) -> bool:
        """Check if a prize can be redeemed by a user.

        Args:
            prize_id: ID of the prize to check
            user_id: ID of the user

        Returns:
            True if prize can be redeemed (exists, not redeemed, XP threshold met)
        """
        try:
            prize = self._prize_repository.get_by_id(prize_id)
            if not prize or prize.user_id != user_id or prize.redeemed:
                return False

            user = self._user_repository.get_by_id(user_id)
            if not user:
                return False

            return user.total_xp >= prize.cost_xp
        except Exception as e:
            logger.error(f"Error checking prize redeemability: {e}")
            return False
