from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time


def explore_playwright():
        
    # Main Dashboard Selectors
    LOADING_SPINNER = "[data-testid='loading-dashboard']"
    ERROR_MESSAGE = "[data-testid='error-message']"
    DAILY_PROGRESS_TEXT = "[data-testid='daily-progress']"
    LEVEL_TEXT = "[data-testid='level-display']"
    XP_TEXT = "[data-testid='level-display-xp']"
    TASK_ITEMS = "[data-testid='upcoming-tasks-list']"
    RECENT_ACHIEVEMENTS = "[data-testid='recent-achievements']"
    CREATE_TASK_BUTTON = "[data-testid='create-task-button']"
    
    # Task Item Selectors (relative to task item)
    TASK_TITLE = "[data-testid='task-title']"
    COMPLETE_BUTTON = "[data-testid='click-complete-button']"
    
    # Create Task Modal Selectors
    MODAL_CONTAINER = "[data-testid='task-create-container']"
    TITLE_INPUT = "[data-testid='title-input']"
    DESCRIPTION_INPUT = "[data-testid='description-input']"
    DUE_DATE_INPUT = "[data-testid='due-date-input']"
    SUBMIT_BUTTON = "[data-testid='submit-button']"
    CANCEL_BUTTON = "[data-testid='cancel-button']"
    SUCCESS_MESSAGE = "[data-testid='submit-success-message']"

    # Start Playwright
    with sync_playwright() as p:
        # Launch browser (headless=False means we can see it!)
        browser = p.chromium.launch(headless=False, slow_mo=500)
        
        # Create a new page/tab
        page = browser.new_page()
        
        # Navigate to SauceDemo
        page.goto("http://127.0.0.1:8001/")
        page.locator(CREATE_TASK_BUTTON).click()
        time.sleep(1)
        future_time = datetime.now() + timedelta(hours=2)
        date_str = future_time.strftime("%Y-%m-%dT%H:%M")
        page.locator(DUE_DATE_INPUT).fill(date_str)
        page.locator(DUE_DATE_INPUT).dispatch_event("input")
        time.sleep(5)

        # Wait a moment so we can see the page



if __name__ == "__main__":
    explore_playwright()

