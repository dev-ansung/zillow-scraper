import asyncio
import logging
from typing import List, Optional

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


async def fetch_property_by_address(address: str, headless: bool = True) -> Optional[PropertyData]:
    """
    Asynchronously fetches detailed property information for a specific address.

    This function searches for a property by its address, navigates to its
    detail page, and extracts comprehensive information including price,
    beds, baths, square footage, property type, year built, lot size, and HOA fees.

    Args:
        address (str): The property address to search for (e.g., "123 Main St, City, State ZIP").
        headless (bool): If True, initializes the browser in headless mode.
                         Defaults to True.

    Returns:
        Optional[PropertyData]: Detailed property information or None if not found.
    """
    return await asyncio.to_thread(_execute_address_search, address, headless)


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


def _execute_address_search(address: str, headless: bool) -> Optional[PropertyData]:
    """
    Internal synchronous execution handler for address-based property search.
    """
    browser = SmartScrollerBrowser(headless=headless)
    parser = ZillowExactParser()
    service = ZillowService(browser, parser)

    try:
        return service.search_by_address(address)
    except Exception as e:
        logger.error(f"Address search execution failed: {e}", exc_info=True)
        return None
    # Note: Service cleanup is handled within service methods
