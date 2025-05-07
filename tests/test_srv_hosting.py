import allure

from pages.hosting_page import HostingPage
from utils.logging_config import setup_logger

import pytest
from playwright.sync_api import Page


logger = setup_logger(__name__)


@pytest.fixture(scope="function")
def hosting_page(page: Page, context):
    logger.info("Starting tracing for test")
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield HostingPage(page)
    context.tracing.stop(path="trace.zip")


@allure.epic("Hosting Services")
@allure.feature("Dedicated Hosting")
@allure.story("Price Filter Functionality")
@allure.severity(allure.severity_level.CRITICAL)
def test_gcore_hosting_page(hosting_page: HostingPage):
    min_price = 400
    max_price = 450

    with allure.step(f"Starting test with price range: {min_price}–{max_price}"):
        logger.info(f"Starting test with price range: {min_price}–{max_price}")

    with allure.step("Navigate to hosting page"):
        hosting_page.navigate("/hosting")

    with allure.step("Select dedicated server type"):
        hosting_page.select_server_type("dedicated")

    with allure.step("Verify dedicated server type is selected"):
        hosting_page.check_server_switcher("dedicated")

    with allure.step("Select USD currency"):
        hosting_page.select_currency_type("USD")

    with allure.step("Verify USD currency is selected"):
        hosting_page.check_currency_switcher("USD")

    with allure.step("Open price filter"):
        hosting_page.click_price_filter()

    with allure.step("Validate minimum price input behavior"):
        hosting_page.validate_min_price_input_behavior()

    with allure.step(f"Set price range to {min_price}-{max_price}"):
        hosting_page.set_price_range(min_price=min_price, max_price=max_price)

    with allure.step(f"Verify servers displayed match price range {min_price}-{max_price}"):
        hosting_page.check_the_servers_price_range(min_price=min_price, max_price=max_price)