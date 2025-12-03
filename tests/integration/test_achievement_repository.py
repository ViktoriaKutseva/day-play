from datetime import UTC, datetime

import pytest
from faker import Faker

from day_play.integrations.database.repositories.achievement_repository import (
    SQLAlchemyAchievementRepository,
)
from day_play.models.entities import Achievement


@pytest.fixture
def achievement_repository(in_memory_db):
    """Create repository instance with in-memory database."""
    return SQLAlchemyAchievementRepository(in_memory_db)

def sample_achievements(number: int = 1):
    fake = Faker()
    achievements = []
    for _ in range(number):
        achievement = Achievement(
            name=fake.name(),
            description=fake.text(),
            icon=fake.image_url(),
            user_id=1,
            created_at=datetime.now(UTC),
        )
        achievements.append(achievement)
    return achievements

class TestAchievementRepository:
    def test_create_achievement(self, achievement_repository):
        achievement = sample_achievements(1)[0]
        achievement.name = "First Achievement"
        created_achievement = achievement_repository.create(achievement)
        assert created_achievement.id is not None
        assert created_achievement.name == "First Achievement"

    def test_get_by_id(self, achievement_repository):
        achievement = sample_achievements(1)[0]
        created_achievement = achievement_repository.create(achievement)
        fetched_achievement = achievement_repository.get_by_id(created_achievement.id)
        assert fetched_achievement is not None
        assert fetched_achievement.id == created_achievement.id

    def test_get_by_user_id(self, achievement_repository):
        achievements = sample_achievements(4)
        for achievement in achievements[:3]:
            achievement.user_id = 2
            achievement_repository.create(achievement)
        results = achievement_repository.get_by_user_id(2)
        assert len(results) == 3

    def test_get_unlocked(self, achievement_repository):
        achievements = sample_achievements(4)
        for i, achievement in enumerate(achievements):
            if i % 2 == 0:
                achievement.unlocked_at = datetime.now(UTC)
            achievement.user_id = 3
            achievement_repository.create(achievement)
        unlocked_achievements = achievement_repository.get_unlocked(3)
        assert len(unlocked_achievements) == 2 

    def test_update_achievement(self, achievement_repository):
        achievement = sample_achievements(1)[0]
        created_achievement = achievement_repository.create(achievement)
        created_achievement.name = "Updated Name"
        updated_achievement = achievement_repository.update(created_achievement)
        assert updated_achievement.name == "Updated Name"

    def test_delete_achievement(self, achievement_repository):
        achievement = sample_achievements(1)[0]
        created_achievement = achievement_repository.create(achievement)
        achievement_repository.delete(created_achievement.id)
        fetched_achievement = achievement_repository.get_by_id(created_achievement.id)
        assert fetched_achievement is None