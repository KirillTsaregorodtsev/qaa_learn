from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

class HostingPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._server_type = lambda value: page.locator(f'gcore-server-configurator input[type="radio"][value="{value}"]')
        self._currency_option = lambda value: page.locator(f'gcore-switcher-currency input[type="radio"][value="{value}"]')
        self._filter_price_btn = page.get_by_role("button", name="Price")
        self._min_price_input = page.locator('gcore-range-multi-slider input[type="number"]').first
        self._max_price_input = page.locator('gcore-range-multi-slider input[type="number"]').last
        self._cards_list = page.locator('gcore-price-card')

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

    def click_price_filter(self):
        self.page.wait_for_timeout(1000)
        logger.info("Clicking price filter button")
        self._filter_price_btn.click()
        self.page.wait_for_selector('gcore-range-multi-slider', state='visible')

    def set_price_range(self, min_price: int, max_price: int):
        logger.info(f"Setting price range: min={min_price}, max={max_price}")
        initial_card_count = self._cards_list.count()
        logger.info(f"Initial number of cards: {initial_card_count}")

        logger.info("Setting max price")
        self._max_price_input.fill(str(max_price))
        #self.page.wait_for_timeout(1000)

        logger.info("Setting min price")
        self._min_price_input.fill(str(min_price))
        #self.page.wait_for_timeout(1000)

        expect(self._cards_list.locator(':visible')).not_to_have_count(initial_card_count, timeout=5000)

    def check_the_servers_price_range(self, min_price: int, max_price: int):
        logger.info("Checking server prices in range")

        card_count = self._cards_list.count()
        logger.info(f"Found {card_count} price cards")
        assert card_count > 0, "No cards found after setting price range"

        cards = self._cards_list.locator('div.gc-price-card-header').all()
        for card in cards:
            price_text = card.locator('span').nth(1).inner_text()
            logger.info(f"Price text: {price_text}")
            price_cleaned = ''.join(char for char in price_text[1:] if char.isdigit())
            price = int(price_cleaned)
            assert min_price <= price <= max_price, f"Price {price} is out of range [{min_price}, {max_price}]"
