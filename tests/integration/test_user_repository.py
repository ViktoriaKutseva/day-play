import random
from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from day_play.integrations.database.repositories.user_repositories import (
    SQLAlchemyUserRepository,
)
from day_play.models.entities import User
from day_play.models.exceptions import UserNotFoundError


@pytest.fixture
def user_repository(in_memory_db):
    """Create repository instance with in-memory database."""
    return SQLAlchemyUserRepository(in_memory_db)

def sample_users(number: int = 1):
    fake = Faker()
    users = []
    for _ in range(number):
        user = User(
            username=fake.name_female(),
            current_level=random.randint(1, 10),
            total_xp=random.randint(0, 1000),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),)
        users.append(user)
    return users

class TestUserRepository:
    def test_create_user(self, user_repository):
        user = sample_users(1)[0]
        user.username = "Test User"
        created_user = user_repository.create(user)
        assert created_user.id is not None

    def test_get_user_by_id(self, user_repository):
        user = sample_users(1)[0]
        created_user = user_repository.create(user)
        fetched_user = user_repository.get_by_id(created_user.id)
        assert fetched_user is not None
        assert fetched_user.id == created_user.id

    def test_update_user(self, user_repository):
        user = sample_users(1)[0]
        created_user = user_repository.create(user)
        created_user.username = "Updated User"
        updated_user = user_repository.update(created_user)
        assert updated_user.username == "Updated User"
        assert updated_user.id == created_user.id

    def test_update_xp(self, user_repository):
        user = sample_users(1)[0]
        created_user = user_repository.create(user)
        xp_delta = 150
        updated_user = user_repository.update_xp(created_user.id, xp_delta)
        assert updated_user.total_xp == created_user.total_xp + xp_delta

    def test_update_level(self, user_repository):
        user = sample_users(1)[0]
        created_user = user_repository.create(user)
        new_level = created_user.current_level + 1
        updated_user = user_repository.update_level(created_user.id, new_level)
        assert updated_user.current_level == new_level

    def test_get_user_by_id_not_found(self, user_repository):
        result = user_repository.get_by_id(999999)
        assert result is None

    def test_update_user_not_found(self, user_repository):
        user = sample_users(1)[0]
        user.id = 9999 
        with pytest.raises(UserNotFoundError):
            user_repository.update(user)

    def test_update_xp_user_not_found(self, user_repository):
        with pytest.raises(UserNotFoundError):
            user_repository.update_xp(9999, 100)

    def test_update_level_user_not_found(self, user_repository):
        with pytest.raises(UserNotFoundError):
            user_repository.update_level(9999, 5)