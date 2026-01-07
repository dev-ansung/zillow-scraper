import logging
from typing import List, Optional
from urllib.parse import quote

from .interfaces import IPageSourceProvider, IParser
from .models import PropertyData


class ZillowService:
    def __init__(self, browser: IPageSourceProvider, parser: IParser):
        self.browser = browser
        self.parser = parser
        self.logger = logging.getLogger("ZillowService")

    def run(self, url: str) -> List[PropertyData]:
        self.logger.info("Starting scrape job...")
        try:
            html = self.browser.fetch_source(url)

            if not html:
                self.logger.error("Browser returned empty content.")
                return []

            data = self.parser.parse(html)
            self.logger.info(f"Successfully parsed {len(data)} properties.")
            return data

        finally:
            self.browser.close()

    def fetch_property_detail(self, url: str) -> Optional[PropertyData]:
        """
        Fetches detailed information for a single property from its detail page.

        Args:
            url (str): The full URL to the property detail page.

        Returns:
            Optional[PropertyData]: Extracted property data or None if fetching fails.
        """
        self.logger.info(f"Fetching property detail from: {url}")
        try:
            html = self.browser.fetch_source(url)

            if not html:
                self.logger.error("Browser returned empty content.")
                return None

            # Import here to avoid circular dependency
            from .parsers import ZillowPropertyDetailParser

            detail_parser = ZillowPropertyDetailParser()
            property_data = detail_parser.parse_detail(html)

            if property_data:
                self.logger.info(f"Successfully parsed property: {property_data.address}")
            else:
                self.logger.warning("Failed to parse property detail")

            return property_data

        finally:
            self.browser.close()

    def search_by_address(self, address: str) -> Optional[PropertyData]:
        """
        Searches for a property by address and returns detailed information.

        This method:
        1. Constructs a search URL from the address
        2. Finds the matching property in search results
        3. Navigates to the property detail page
        4. Extracts comprehensive information

        Args:
            address (str): The property address to search for.

        Returns:
            Optional[PropertyData]: Detailed property data or None if not found.
        """
        self.logger.info(f"Searching for property: {address}")

        try:
            # Construct search URL
            encoded_address = quote(address)
            search_url = f"https://www.zillow.com/homes/{encoded_address}_rb/"

            self.logger.info(f"Search URL: {search_url}")
            html = self.browser.fetch_source(search_url)

            if not html:
                self.logger.error("Browser returned empty content for search.")
                return None

            # Parse search results to find the property
            properties = self.parser.parse(html)

            if not properties:
                self.logger.warning(f"No properties found for address: {address}")
                return None

            # Get the first matching property (closest match)
            first_property = properties[0]
            property_url = first_property.link

            if not property_url or property_url == "N/A":
                self.logger.error("Could not find property detail URL")
                return None

            self.logger.info(f"Found property URL: {property_url}")

            # Now fetch the detail page
            # We need to create a new browser instance for the detail page
            # since the current one will be closed
            from .browsers import SmartScrollerBrowser

            detail_browser = SmartScrollerBrowser(headless=self.browser.headless)
            detail_service = ZillowService(detail_browser, self.parser)

            return detail_service.fetch_property_detail(property_url)

        except Exception as e:
            self.logger.error(f"Error searching by address: {e}", exc_info=True)
            return None
        finally:
            self.browser.close()
