import logging
from typing import List

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