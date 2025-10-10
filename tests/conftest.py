"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.day_play.config.environments.testing import TestingSettings
from src.day_play.models.entities import Task
from src.day_play.integrations.database.repositories import SQLiteTaskRepository


@pytest.fixture
def test_settings() -> TestingSettings:
    """Test settings fixture."""
    return TestingSettings()


@pytest.fixture
def test_db_session(test_settings: TestingSettings):
    """Database session fixture for testing."""
    engine = create_engine(test_settings.database_url, connect_args={"check_same_thread": False})

    # Create tables
    Task.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Clean up database
        Task.metadata.drop_all(engine)


@pytest.fixture
def task_repository(test_settings: TestingSettings) -> SQLiteTaskRepository:
    """Task repository fixture."""
    return SQLiteTaskRepository(test_settings.database_url)
