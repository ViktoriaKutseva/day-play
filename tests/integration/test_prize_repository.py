import random
from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from day_play.integrations.database.repositories.prize_repository import (
    SQLAlchemyPrizeRepository,
)
from day_play.models.entities import Prize


@pytest.fixture
def prize_repository(in_memory_db):
    """Create repository instance with in-memory database."""
    return SQLAlchemyPrizeRepository(in_memory_db)


def sample_prizes(number: int = 1):
    fake = Faker()
    prizes = []
    for _ in range(number):
        prize = Prize(
            name=fake.name_female(),
            description=fake.name_male(),
            cost_xp=random.randint(0, 1000),
            redeemed=False,
            redeemed_at=None,
            user_id=1,
            )
        prizes.append(prize)
    return prizes

class TestPrizeRepository:
    def test_create_prize(self, prize_repository):
        prize = sample_prizes(1)[0]
        prize.name = "Test Prize"
        created_prize = prize_repository.create(prize)
        assert created_prize.id is not None
        assert created_prize.name == "Test Prize"

    def test_get_by_id(self, prize_repository):
        prize = sample_prizes(1)[0]
        created_prize = prize_repository.create(prize)
        fetched_prize = prize_repository.get_by_id(created_prize.id)
        assert fetched_prize is not None
        assert fetched_prize.id == created_prize.id
    
    def test_get_by_user_id(self, prize_repository):
        prizes = sample_prizes(3)
        prizes[0].user_id = 2
        for prize in prizes:
            prize_repository.create(prize)
        fetched_prizes = prize_repository.get_by_user_id(1)
        assert len(fetched_prizes) == 2

    def test_get_available(self, prize_repository):
        prizes = sample_prizes(4)
        prizes[0].redeemed = True
        for prize in prizes:
            prize_repository.create(prize)
        available_prizes = prize_repository.get_available(1)
        assert len(available_prizes) == 3

    def test_get_redeemed(self, prize_repository):
        prizes = sample_prizes(4)
        prizes[1].redeemed = True
        prizes[3].redeemed = True
        for prize in prizes:
            prize_repository.create(prize)
        redeemed_prizes = prize_repository.get_redeemed(1)
        assert len(redeemed_prizes) == 2

    def test_get_by_id_not_found(self, prize_repository):
        result = prize_repository.get_by_id(9999)
        assert result is None

    def test_no_prizes_for_user(self, prize_repository):
        prizes = prize_repository.get_by_user_id(9999)
        assert len(prizes) == 0 

    def test_no_available_prizes(self, prize_repository): 
        prizes = sample_prizes(2)
        for prize in prizes:
            prize.redeemed = True
            prize_repository.create(prize)
        available_prizes = prize_repository.get_available(1)
        assert len(available_prizes) == 0
    
    def test_update_prize(self, prize_repository):
        prize = sample_prizes(1)[0]
        created_prize = prize_repository.create(prize)
        created_prize.name = "Updated Prize Name"
        created_prize.redeemed = True
        updated_prize = prize_repository.update(created_prize)
        assert updated_prize.name == "Updated Prize Name"
        assert updated_prize.redeemed is True
        fetched_prize = prize_repository.get_by_id(updated_prize.id)
        assert fetched_prize.name == "Updated Prize Name"
        assert fetched_prize.redeemed is True

    def test_delete_prize(self, prize_repository):
        prize = sample_prizes(1)[0]
        created_prize = prize_repository.create(prize)
        prize_repository.delete(created_prize.id)
        fetched_prize = prize_repository.get_by_id(created_prize.id)
        assert fetched_prize is None