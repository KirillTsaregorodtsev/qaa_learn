from pages.hosting_page import HostingPage
from utils.logging_config import setup_logger

import pytest
from playwright.sync_api import Page, expect


logger = setup_logger(__name__)


@pytest.fixture(scope="function")
def hosting_page(page: Page, context):
    logger.info("Starting tracing for test")
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield HostingPage(page)
    context.tracing.stop(path="trace.zip")


def test_gcore_hosting_page(hosting_page: HostingPage):
    min_price = 400
    max_price = 450
    logger.info(f"Starting test with price range: {min_price}–{max_price}")
    hosting_page.navigate("/hosting")

    hosting_page.select_server_type("dedicated")
    hosting_page.check_server_switcher("dedicated")

    hosting_page.select_currency_type("USD")
    hosting_page.check_currency_switcher("USD")

    hosting_page.click_price_filter()
    hosting_page.set_price_range(min_price=min_price, max_price=max_price)
    hosting_page.check_the_servers_price_range(min_price=min_price, max_price=max_price)