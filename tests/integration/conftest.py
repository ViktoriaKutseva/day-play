import pytest
from playwright.sync_api import sync_playwright
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

    session = SessionLocal()

    yield session

    # Cleanup
    session.close()

@pytest.fixture(scope="session")
def playwright_browser():
    """Start Playwright browser for E2E tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(playwright_browser):
    """Create new page for each test."""
    context = playwright_browser.new_context()
    page = context.new_page()
    yield page
    context.close()