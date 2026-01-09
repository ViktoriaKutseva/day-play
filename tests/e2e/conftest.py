"""Pytest configuration for E2E tests."""
import pytest
from playwright.sync_api import sync_playwright

from e2e.pages.dashboard import DashboardPage


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

@pytest.fixture
def dashboard_page(page):
    """Provide DashboardPage instance for tests."""
    return DashboardPage(page)
