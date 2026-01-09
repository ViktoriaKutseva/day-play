
from allure import step
from playwright.sync_api import Page
from e2e.pages.base_page import BasePage
import time
from datetime import datetime, timedelta

class DashboardPage(BasePage):

    URL = "http://127.0.0.1:8001/"
    
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

    def __init__(self, page: Page):
        """Initialize the DashboardPage.
        Args:
            page (Page): The Playwright Page object.
        """
        super().__init__(page)

    @step("Open the dashboard page")
    def open(self) -> "DashboardPage":
        """Navigate to the dashboard page."""
        self.navigate_to(self.URL)
        return self

    @step("Wait for the dashboard to finish loading")
    def wait_for_load(self) -> "DashboardPage":
        """Wait for the loading spinner to disappear."""
        self.page.locator(self.LOADING_SPINNER).wait_for(state="hidden")
        return self

    @step("Get the daily progress percentage")
    def get_daily_progress(self) -> str:
        """Get the text of the daily progress percentage."""
        return self.page.locator(self.DAILY_PROGRESS_TEXT).inner_text()

    @step("Get the current level")
    def get_level(self) -> str:
        """Get the current level text."""
        return self.page.locator(self.LEVEL_TEXT).first.inner_text()

    @step("Get the current XP")
    def get_xp(self) -> str:
        """Get the current XP text."""
        return self.page.locator(self.XP_TEXT).inner_text()

    @step("Click the 'Create New Task' button")
    def click_create_task(self) -> "DashboardPage":
        """Open the create task modal."""
        self.page.locator(self.CREATE_TASK_BUTTON).click()
        return self

    @step("Wait for the create task modal to be visible")
    def wait_for_modal(self) -> "DashboardPage":
        """Wait for the create task modal to appear."""
        self.page.locator(self.MODAL_CONTAINER).wait_for(state="visible")
        return self

    @step("Close the create task modal")
    def close_modal(self) -> "DashboardPage":
        """Close the create task modal using the cancel button."""
        self.page.locator(self.CANCEL_BUTTON).click()
        time.sleep(0.5)  # Wait for modal close animation
        return self

    @step("Fill in the task title")
    def fill_title(self, title: str) -> "DashboardPage":
        """Fill the title in the create task modal."""
        self.page.locator(self.TITLE_INPUT).fill(title)
        return self

    @step("Fill in the task description")
    def fill_description(self, description: str) -> "DashboardPage":
        """Fill the description in the create task modal."""
        self.page.locator(self.DESCRIPTION_INPUT).fill(description)
        return self

    @step("Set task priority to {priority}")
    def set_priority(self, priority: str) -> "DashboardPage":
        """Set the task priority (low, medium, high)."""
        selector = f"div:has(> label:has-text('Priority')) button:has-text('{priority.capitalize()}')"
        self.page.locator(selector).click()
        return self

    @step("Set task urgency to {urgency}")
    def set_urgency(self, urgency: str) -> "DashboardPage":
        """Set the task urgency (low, medium, high)."""
        selector = f"div:has(> label:has-text('Urgency')) button:has-text('{urgency.capitalize()}')"
        self.page.locator(selector).click()
        return self

    @step("Click the submit button to create the task")
    def submit_task(self) -> None:
        """Submit the task creation form."""
        self.page.locator(self.SUBMIT_BUTTON).click()

    @step("Create a new task with given details")
    def create_task(self, title: str, description: str = "", priority: str = "medium", urgency: str = "medium") -> None:
        """Perform the full task creation flow."""
        self.click_create_task()
        self.wait_for_modal()
        self.fill_title(title)
        if description:
            self.fill_description(description)
        self.set_priority(priority)
        self.set_urgency(urgency)
        self.submit_task()
        # Wait for success message or modal to close
        self.page.locator(self.SUCCESS_MESSAGE).wait_for(state="visible")

    @step("Check if a task with title '{title}' exists")
    def has_task(self, title: str) -> bool:
        """Check if a task with the given title is visible in the list."""
        return self.page.locator(self.TASK_ITEMS).filter(has_text=title).is_visible()

    @step("Complete the task with title '{title}'")
    def complete_task(self, title: str) -> None:
        """Click the complete button for a specific task."""
        task_locator = self.page.locator(self.TASK_ITEMS).filter(has_text=title)
        task_locator.locator(self.COMPLETE_BUTTON).click()

    @step("Check if error message is visible")
    def is_error_displayed(self) -> bool:
        """Check if the dashboard error message is visible."""
        return self.page.locator(self.ERROR_MESSAGE).is_visible()
    
    def set_due_date_to_today(self) -> "DashboardPage":
        """Set the due date input to 1 hour from now."""
        future_time = datetime.now() + timedelta(hours=1)
        date_str = future_time.strftime("%Y-%m-%dT%H:%M")
        self.page.locator(self.DUE_DATE_INPUT).fill(date_str)
        self.page.locator(self.DUE_DATE_INPUT).dispatch_event("input")
        return self