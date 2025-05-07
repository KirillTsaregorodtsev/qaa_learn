import pytest
from playwright.sync_api import Page, expect, Error

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
        """
        Sets the price range for the server cards and checks that the number of cards
        changes after setting the range.

        :param min_price: Minimal price to set
        :param max_price: Maximal price to set
        """
        logger.info(f"Setting price range: min={min_price}, max={max_price}")
        initial_card_count = self._cards_list.count()
        logger.info(f"Initial number of cards: {initial_card_count}")

        logger.info("Setting min price")
        self._min_price_input.fill(str(min_price))

        logger.info("Setting max price")
        self._max_price_input.fill(str(max_price))


        expect(self._cards_list.locator(':visible')).not_to_have_count(initial_card_count, timeout=5000)

    def check_the_servers_price_range(self, min_price: int, max_price: int):
        """
        Checks that all server cards have prices in the given range.

        :param min_price: Minimal price to check
        :param max_price: Maximal price to check
        """
        logger.info("Checking server prices in range")

        card_count = self._cards_list.count()
        logger.debug(f"Found {card_count} price cards")
        assert card_count > 0, "No cards found after setting price range"

        cards = self._cards_list.locator('div.gc-price-card-header').all()
        for card in cards:
            price_text = card.locator('span').nth(1).inner_text()
            logger.debug(f"Price text: {price_text}")
            price_cleaned = ''.join(char for char in price_text[1:] if char.isdigit())
            price = int(price_cleaned)
            assert min_price <= price <= max_price, f"Price {price} is out of range [{min_price}, {max_price}]"

    def validate_numeric_input_behavior(self, input_locator, paired_input_locator=None, is_min=True):
        """
        Performs comprehensive validation of a numeric input field:
        - Keeps default if input is lower than default or negative
        - Ignores letters and special characters
        - For min fields: Adjusts to (max_value - 1) if input exceeds max_value
        - For max fields: Adjusts to (min_value + 1) if input is below min_value

        Args:
            input_locator: Locator of the input field to validate
            paired_input_locator: Locator of paired field (max for min, min for max)
            is_min: Boolean indicating if this is a min field (True) or max field (False)
        """
        logger.info(f"Starting validation of {'min' if is_min else 'max'} input behavior")

        default_value = int(input_locator.input_value())

        paired_value = None
        if paired_input_locator:
            paired_value = int(paired_input_locator.input_value())

        logger.info(f"Default value: {default_value}, Paired value: {paired_value}")

        # Test: Input less than default (for min) or greater than default (for max)
        test_value = default_value - 1 if is_min else default_value + 1
        input_locator.fill(str(test_value))
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("Tab")
        actual_value = int(input_locator.input_value())

        expected_value = default_value
        assert_message = f"Input {'below' if is_min else 'above'} default was not reset to default: {actual_value}"
        assert actual_value == expected_value, assert_message

        # Test: Input negative number
        input_locator.fill("-100")
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("Tab")
        actual_value = int(input_locator.input_value())
        assert actual_value == default_value, f"Negative value not reset to default: {actual_value}"

        # Test: Input letters
        with pytest.raises(Error) as exc_info:
            input_locator.fill("abc")
            self.page.keyboard.press("Tab")
        assert "Cannot type text into input[type=number]" in str(exc_info.value), \
            f"Unexpected error: {exc_info.value}"

        # Test: Input special characters
        with pytest.raises(Error) as exc_info:
            input_locator.fill("@#$")
            self.page.keyboard.press("Tab")
        assert "Cannot type text into input[type=number]" in str(exc_info.value), \
            f"Unexpected error: {exc_info.value}"

        if paired_input_locator and paired_value is not None:
            if is_min:
                test_value = paired_value + 10
                expected_value = paired_value - 1
                assert_message = f"Min input greater than max not set to max-1: {{actual}} vs {expected_value}"
            else:
                test_value = paired_value - 10
                expected_value = paired_value + 1
                assert_message = f"Max input less than min not set to min+1: {{actual}} vs {expected_value}"

            input_locator.fill(str(test_value))
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Tab")
            actual_value = int(input_locator.input_value())
            assert actual_value == expected_value, assert_message.format(actual=actual_value)

    def validate_min_price_input_behavior(self):
        self.validate_numeric_input_behavior(
            input_locator=self._min_price_input,
            paired_input_locator=self._max_price_input,
            is_min=True
        )

    def validate_max_price_input_behavior(self):
        self.validate_numeric_input_behavior(
            input_locator=self._max_price_input,
            paired_input_locator=self._min_price_input,
            is_min=False
        )