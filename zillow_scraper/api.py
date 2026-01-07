import asyncio
import logging
from typing import List, Optional

from .browsers import SmartScrollerBrowser
from .models import PropertyData, PropertyDetail
from .parsers import ZillowComprehensiveDetailParser, ZillowExactParser
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


async def fetch_property_by_address(
    address_or_url: str, headless: bool = True
) -> Optional[PropertyDetail]:
    """
    Asynchronously fetches detailed property information for a specific address or URL.

    This function accepts either:
    - A Zillow property URL (e.g., "https://www.zillow.com/homedetails/...")
    - A property address string (e.g., "123 Main St, City, State ZIP")

    It automatically detects which type of input is provided and extracts comprehensive
    property information including price details, property basics, interior features,
    community amenities, location scores, nearby schools, and listing information.

    Args:
        address_or_url (str): Either a Zillow property URL or a property address string.
        headless (bool): If True, initializes the browser in headless mode.
                         Defaults to True.

    Returns:
        Optional[PropertyDetail]: Comprehensive property information or None if not found.
    """
    return await asyncio.to_thread(_execute_property_detail_fetch, address_or_url, headless)


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


def _execute_property_detail_fetch(address_or_url: str, headless: bool) -> Optional[PropertyDetail]:
    """
    Internal synchronous execution handler for property detail fetching.

    Detects if the input is a URL or address and fetches accordingly.
    """
    browser = SmartScrollerBrowser(headless=headless)
    parser = ZillowExactParser()

    try:
        # Detect if input is a URL or address
        if address_or_url.startswith("http://") or address_or_url.startswith("https://"):
            # It's a URL - fetch directly
            property_url = address_or_url
        else:
            # It's an address - search for it first
            from urllib.parse import quote

            encoded_address = quote(address_or_url)
            search_url = f"https://www.zillow.com/homes/{encoded_address}_rb/"

            logger.info(f"Searching for property at: {search_url}")
            html = browser.fetch_source(search_url)

            if not html:
                logger.error("Browser returned empty content for search.")
                browser.close()
                return None

            # Parse search results to find the property
            properties = parser.parse(html)

            if not properties:
                logger.warning(f"No properties found for address: {address_or_url}")
                browser.close()
                return None

            # Get the first matching property URL
            property_url = properties[0].link

            if not property_url or property_url == "N/A":
                logger.error("Could not find property detail URL")
                browser.close()
                return None

            logger.info(f"Found property URL: {property_url}")

            # Close the search browser
            browser.close()

            # Create a new browser for the detail page
            browser = SmartScrollerBrowser(headless=headless)

        # Fetch the property detail page
        logger.info(f"Fetching property details from: {property_url}")
        html = browser.fetch_source(property_url)

        if not html:
            logger.error("Browser returned empty content for property detail page.")
            browser.close()
            return None

        # Parse comprehensive property details
        detail_parser = ZillowComprehensiveDetailParser()
        property_detail = detail_parser.parse(html, url=property_url)

        if property_detail:
            logger.info(f"Successfully parsed property: {property_detail.address.street}")
        else:
            logger.warning("Failed to parse property detail")

        return property_detail

    except Exception as e:
        logger.error(f"Property detail fetch failed: {e}", exc_info=True)
        return None
    finally:
        browser.close()
