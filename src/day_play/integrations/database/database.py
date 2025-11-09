from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from day_play.config.settings import settings
from day_play.integrations.database import models  # noqa: F401

# Create database engine
engine: Engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database_url
    else {},
)

# Create session factory
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db() -> None:
    """Initialize the database by creating all tables."""
    SQLModel.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """
    Get a new database session with automatic cleanup.

    This is a generator function for FastAPI dependency injection.
    The session is automatically closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
