import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from day_play.integrations.database.models import SQLModel


@pytest.fixture
def in_memory_db():
    """Create in-memory database for testing."""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session factory
    SessionLocal = sessionmaker(bind=engine)

    yield SessionLocal

    # Cleanup
    engine.dispose()
