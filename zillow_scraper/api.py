import asyncio
import logging
from typing import List

from .browsers import SmartScrollerBrowser
from .models import PropertyData
from .parsers import ZillowExactParser
from .services import ZillowService

# Configure module-level logger
logger = logging.getLogger(__name__)


async def fetch_listings(url: str, headless: bool = True) -> List[PropertyData]:
    """
    Asynchronously executes the scraping pipeline for a target Zillow URL.

    This function handles the instantiation of browser and parser components
    and executes the scraping logic within a separate thread executor. This
    ensures that the Selenium WebDriver (which is blocking) does not halt
    the main asyncio event loop.

    Args:
        url (str): The fully qualified Zillow search URL.
        headless (bool): If True, initializes the browser in headless mode.
                         Defaults to True.

    Returns:
        List[PropertyData]: A collection of extracted property data objects.
    """
    return await asyncio.to_thread(_execute_pipeline, url, headless)


def _execute_pipeline(url: str, headless: bool) -> List[PropertyData]:
    """
    Internal synchronous execution handler for the scraping service.
    """
    browser = SmartScrollerBrowser(headless=headless)
    parser = ZillowExactParser()
    service = ZillowService(browser, parser)

    try:
        return service.run(url)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return []
    # Note: Service cleanup is handled within service.run()