from playwright.sync_api import Page

BASE_URL = "https://gcore.com"

class BasePage:
    def __init__(self, page: Page, base_url: str = BASE_URL):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str):
        full_url = f"{self.base_url}{path}"
        self.page.goto(full_url, wait_until="networkidle")