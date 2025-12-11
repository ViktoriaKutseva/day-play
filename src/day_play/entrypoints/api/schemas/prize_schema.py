from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from day_play.models.entities import Prize


class PrizeCreate(BaseModel):
    """Schema for creating a new prize."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Prize title",
        examples=["Gift Card"],
        )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Detailed prize description",
        )
    cost_xp: int = Field(
        default=0,
        ge=0,
        description="XP required to unlock this prize",
        examples=[500],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()

    def to_entity(self, user_id: int = 1) -> Prize:
        """Convert schema to Task entity."""
        return Prize(
            name=self.name,
            description=self.description,
            cost_xp=self.cost_xp,
            user_id=user_id,
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Movie night",
                    "description": "Watch a movie of your choice",
                    "cost_xp": 500,
                }
            ]
        }
    }

class PrizeUpdate(BaseModel):
    """Schema for updating an existing prize (partial updates)."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New prize title",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="New prize description",
    )
    cost_xp: int | None = Field(
        default=None,
        ge=0,
        description="New XP cost to unlock this prize",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Ensure name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip() if v else v

class PrizeResponse(BaseModel):
    """Schema for prize response."""
    id: int = Field(description="Unique prize identifier")
    name: str = Field(description="Prize name")
    description: str | None = Field(description="Prize description")
    cost_xp: int = Field(description="XP cost to unlock this prize")
    redeemed: bool = Field(description="Whether the prize has been redeemed")
    redeemed_at: datetime | None = Field(description="When prize was redeemed")
    is_available: bool = Field(description="Whether user has enough XP to redeem (computed)")
    user_id: int | None = Field(description="User who owns this prize")
    created_at: datetime = Field(description="When prize was created")
    updated_at: datetime | None = Field(description="When achievement was last updated")

    @classmethod
    def from_entity(cls, prize: "Prize", user_total_xp: int = 0) -> "PrizeResponse":
        """Create PrizeResponse from Prize entity.

        Args:
            prize: Prize entity from business layer
            user_total_xp: User's total XP (to compute is_available)

        Returns:
            PrizeResponse schema instance
        """

        return cls(
            id=prize.id or 0,
            name=prize.name,
            description=prize.description,
            user_id=prize.user_id,
            cost_xp=prize.cost_xp,
            redeemed=prize.redeemed,
            redeemed_at=prize.redeemed_at,
            created_at=prize.created_at or datetime.now(),
            updated_at=prize.updated_at,
            is_available=not prize.redeemed and user_total_xp >= prize.cost_xp,
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Movie night",
                    "description": "Watch a movie of your choice",
                    "cost_xp": 500,
                    "redeemed": False,
                    "redeemed_at": None,
                    "is_available": True,
                    "user_id": 1,
                }
            ]
        }
    }
