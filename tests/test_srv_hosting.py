import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://gcore.com"

class BasePage:
    def __init__(self, page: Page, base_url: str = BASE_URL):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str):
        full_url = f"{self.base_url}{path}"
        self.page.goto(full_url, wait_until="networkidle")


class HostingPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Локаторы
        self._server_type = lambda value: page.locator(f'gcore-server-configurator input[type="radio"][value="{value}"]')
        self._currency_option = lambda value: page.locator(f'gcore-switcher-currency input[type="radio"][value="{value}"]')

    def select_server_type(self, server_type: str):
        self._server_type(server_type).click()

    def select_currency_type(self, currency_type: str):
        self._currency_option(currency_type).click()

    def check_server_switcher(self, expected_value: str):
        selected_server = self._server_type(expected_value)
        expect(selected_server).to_be_checked()

    def check_currency_switcher(self, expected_value: str):
        selected_currency = self._currency_option(expected_value)
        expect(selected_currency).to_be_checked()


@pytest.fixture(scope="function")
def hosting_page(page: Page):
    return HostingPage(page)


# Основной тест
def test_gcore_hosting_page(hosting_page: HostingPage):
    hosting_page.navigate("/hosting")

    hosting_page.select_server_type("dedicated")
    hosting_page.check_server_switcher("dedicated")

    hosting_page.select_currency_type("USD")
    hosting_page.check_currency_switcher("USD")