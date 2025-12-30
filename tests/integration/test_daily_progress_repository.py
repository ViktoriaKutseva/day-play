from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker

from day_play.integrations.database.repositories.daily_progress_repository import (
    SQLAlchemyDailyProgressRepository,
)
from day_play.models.entities import DailyProgress


@pytest.fixture 
def daily_progress_repository(in_memory_db):
    return SQLAlchemyDailyProgressRepository(in_memory_db)

def sample_daily_progresses(number: int = 1):
    fake = Faker()
    daily_progresses = []
    for _ in range(number):
        daily_progress = DailyProgress(
            user_id=1,
            date=datetime.now(UTC).date(),
            tasks_completed=fake.random_int(min=0, max=10),
            tasks_total=fake.random_int(min=10, max=20),
            completion_percentage=fake.random.uniform(0.0, 100.0),
            daily_xp_earned=fake.random_int(min=0, max=500),
        )
        daily_progresses.append(daily_progress)
    return daily_progresses

class TestDailyProgressRepository:
    def test_create_progress(self, daily_progress_repository):
        daily_progress = sample_daily_progresses(1)[0]
        daily_progress.user_id = 1
        daily_progress.date = datetime.now(UTC).date()
        created_progress = daily_progress_repository.create_or_update_progress(daily_progress)
        assert created_progress.id is not None
        assert created_progress.user_id == 1

    def test_update_progress(self, daily_progress_repository):
        daily_progress = sample_daily_progresses(1)[0]
        daily_progress.user_id = 1
        daily_progress.date = datetime.now(UTC).date()
        created_progress = daily_progress_repository.create_or_update_progress(daily_progress)

        # Update values
        created_progress.tasks_completed += 2
        created_progress.daily_xp_earned += 100

        updated_progress = daily_progress_repository.create_or_update_progress(created_progress)
        assert updated_progress.tasks_completed == created_progress.tasks_completed
        assert updated_progress.daily_xp_earned == created_progress.daily_xp_earned

    def test_get_progress_by_date(self, daily_progress_repository):
        daily_progress = sample_daily_progresses(1)[0]
        daily_progress.user_id = 2
        daily_progress.date = datetime.now(UTC).date()
        created_progress = daily_progress_repository.create_or_update_progress(daily_progress)

        fetched_progress = daily_progress_repository.get_progress_by_date(
            user_id=2,
            date_progress=daily_progress.date,
        )
        assert fetched_progress is not None
        assert fetched_progress.id == created_progress.id

    def test_get_progress_by_date_not_found(self, daily_progress_repository):
        result = daily_progress_repository.get_progress_by_date(
            user_id=999,
            date_progress=datetime.now(UTC).date(),
        )
        assert result is None

    def test_get_date_range(self, daily_progress_repository):
        user_id = 3
        base_date = datetime.now(UTC).date()
        list_of_progresses  = sample_daily_progresses(5)
        for i, progress in enumerate(list_of_progresses):
            progress.user_id = user_id
            progress.date = base_date + timedelta(days=i)
            daily_progress_repository.create_or_update_progress(progress)
        start_date = base_date
        end_date = base_date + timedelta(days=4)
        progresses = daily_progress_repository.get_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        assert len(progresses) == 5