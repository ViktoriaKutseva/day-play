import allure
import pytest

from day_play.integrations.database.database import SessionLocal
from day_play.integrations.database.models import Task
from e2e.pages.dashboard import DashboardPage
from datetime import datetime, date
@allure.feature("Dashboard Page")

class TestDashboardPage:

    def test_dashboard_loads(self, dashboard_page: DashboardPage):
        """Test that the dashboard page loads correctly."""
        dashboard_page.open().wait_for_load()

        # Verify key elements are visible
        assert dashboard_page.page.locator(dashboard_page.DAILY_PROGRESS_TEXT).is_visible()
        assert dashboard_page.page.locator(dashboard_page.LEVEL_TEXT).is_visible()
        assert dashboard_page.page.locator(dashboard_page.CREATE_TASK_BUTTON).is_visible()

    def test_create_task_modal(self, dashboard_page: DashboardPage):
        """Test opening and closing the create task modal."""
        dashboard_page.open().wait_for_load()
        dashboard_page.click_create_task().wait_for_modal()

        # Verify modal elements are visible
        assert dashboard_page.page.locator(dashboard_page.TITLE_INPUT).is_visible()
        assert dashboard_page.page.locator(dashboard_page.DESCRIPTION_INPUT).is_visible()
        assert dashboard_page.page.locator(dashboard_page.DUE_DATE_INPUT).is_visible()

        dashboard_page.close_modal()

        # Verify modal is closed
        assert not dashboard_page.page.locator(dashboard_page.MODAL_CONTAINER).is_visible()

    def test_fill_create_task_form(self, dashboard_page: DashboardPage):
        """Test filling in the create task form."""
        dashboard_page.open().wait_for_load()
        dashboard_page.click_create_task().wait_for_modal()

        # Fill in the form
        dashboard_page.fill_title("Test Task")
        dashboard_page.fill_description("This is a test task description.")
        dashboard_page.set_priority("medium")
        dashboard_page.set_urgency("medium")

        # Verify form values
        assert dashboard_page.page.locator(dashboard_page.TITLE_INPUT).input_value() == "Test Task"
        assert dashboard_page.page.locator(dashboard_page.DESCRIPTION_INPUT).input_value() == "This is a test task description."

        # Submit the form
        dashboard_page.submit_task()

        # Wait for success message
        dashboard_page.page.locator(dashboard_page.SUCCESS_MESSAGE).wait_for(state="visible")

        # Verify the task is in the database
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.title == "Test Task").first()
            assert task is not None, "Task was not created in the database"
            assert task.description == "This is a test task description."
            assert task.user_id == 1  # Assuming default user
            assert task.priority == "medium"
            assert task.urgency == "medium"
        finally:
            db.close()

    def test_create_task_for_today(self, dashboard_page: DashboardPage):
        """Test creating a task scheduled for today."""
        dashboard_page.open().wait_for_load()
        dashboard_page.click_create_task().wait_for_modal()

        # Fill in the form with due date today
        dashboard_page.fill_title("Today's Task")
        dashboard_page.fill_description("Task due today.")
        dashboard_page.set_priority("high")
        dashboard_page.set_urgency("high")
        dashboard_page.set_due_date_to_today()

        # Submit the form
        dashboard_page.submit_task()

        # Wait for success message
        dashboard_page.page.locator(dashboard_page.SUCCESS_MESSAGE).wait_for(state="visible")

        # Verify the task is in the database with today's due date
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.title == "Today's Task").first()
            assert task is not None, "Task was not created in the database"
            assert task.due_date.date() == date.today(), f"Task due date is {task.due_date}, expected today"
        finally:
            db.close()