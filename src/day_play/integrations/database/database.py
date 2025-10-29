from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models to ensure they are registered with SQLModel metadata
from src.day_play.models.models import User, Task, TaskCompletion  # noqa: F401


class DatabaseManager:
    def __init__(self, database_url: str):
        """
        Initialize database manager.

        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """Get database engine, creating it if necessary."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with proper configuration."""
        return create_engine(
            self.database_url,
            echo=False,  # Set to True for SQL query logging in development
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )

    def create_tables(self) -> None:
        """Create all database tables from SQLModel classes."""
        try:
            logger.info("Creating database tables")
            SQLModel.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def get_session(self):
        """Get a database session (for future use)."""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return SessionLocal()


def get_database_url() -> str:
    """Get database URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set. Please add it to your .env file.")
    return database_url


def init_database() -> DatabaseManager:
    database_url = get_database_url()
    logger.info(f"Initializing database with URL: {database_url.replace(database_url.split('://')[1].split('@')[-1] if '@' in database_url else database_url.split('://')[1], '***')}")

    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()

    return db_manager


# Global database manager instance
db_manager = init_database()