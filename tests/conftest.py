"""Test configuration and fixtures."""
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.day_play.config.environments.testing import TestingSettings


@pytest.fixture(name="test_settings")
def test_settings_fixture():
    """Test settings fixture."""
    return TestingSettings()


@pytest.fixture(name="session")
def session_fixture():
    """Database session fixture for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session