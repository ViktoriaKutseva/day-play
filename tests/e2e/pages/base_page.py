
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page
    
    def navigate(self, url: str):
        self.page.goto(url)

    def navigate_to(self, url: str):
        """Alias for navigate to match example style."""
        self.navigate(url)

    def get_url(self) -> str:
        return self.page.url
    
    def get_title(self) -> str:
        return self.page.title()

