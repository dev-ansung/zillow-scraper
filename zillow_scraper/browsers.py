import logging
import random
import time

from selenium.webdriver.common.by import By
from seleniumbase import Driver

from .interfaces import IPageSourceProvider


class SmartScrollerBrowser(IPageSourceProvider):
    def __init__(self, headless=False):
        self.logger = logging.getLogger("Browser")
        # uc=True is essential for bypassing Zillow bot detection
        self.driver = Driver(uc=True, headless=headless)

    def _find_scrollable_element(self):
        """
        Locates the specific DIV on the right side that holds the listings.
        """
        selectors = [
            (By.ID, "search-page-list-container"),
            (By.CSS_SELECTOR, "div.search-page-list-container"),
            (By.CSS_SELECTOR, "[class*='search-page-list-container']") 
        ]
        
        for by_type, selector in selectors:
            try:
                el = self.driver.find_element(by_type, selector)
                self.logger.info(f"Found scroll container using: {selector}")
                return el
            except Exception:
                continue
        
        self.logger.warning("Could not identify specific list container. Falling back to body.")
        return self.driver.find_element(By.TAG_NAME, "body")

    def _human_scroll(self, element):
        """
        Scrolls the element gradually, waiting for new content to expand the container.
        """
        self.logger.info("Starting human-like gradual scroll...")
        
        current_position = 0
        
        while True:
            # 1. Scroll down by a small random chunk (simulates mouse wheel)
            chunk = random.randint(100, 200)
            current_position += chunk
            
            self.driver.execute_script(
                f"arguments[0].scrollTo(0, {current_position});", 
                element
            )
            
            # 2. Wait for the 'loading' spinner to finish
            time.sleep(random.uniform(0.01, 0.1))
            
            # 3. Check if we hit the bottom of the CURRENT rendered content
            visible_height = self.driver.execute_script("return arguments[0].clientHeight", element)
            scrolled_height = self.driver.execute_script("return arguments[0].scrollTop", element)
            total_height = self.driver.execute_script("return arguments[0].scrollHeight", element)

            if (scrolled_height + visible_height) >= (total_height - 100):
                self.logger.info("Hit bottom. Waiting for lazy load...")
                time.sleep(2.5) 
                
                # Check if new items loaded
                new_total_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", element)
                
                if new_total_height == total_height:
                    self.logger.info("Height did not increase. End of list reached.")
                    break
                else:
                    self.logger.info(
                        f"New items loaded! Height grew from {total_height} to {new_total_height}")
                    total_height = new_total_height

    def fetch_source(self, url: str) -> str:
        try:
            self.logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Initial wait for page framework
            time.sleep(5)
            
            # Find the div and scroll it
            scroll_container = self._find_scrollable_element()
            if scroll_container:
                self._human_scroll(scroll_container)
            
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Browser error: {e}")
            return ""
    
    def close(self):
        self.logger.info("Closing browser...")
        self.driver.quit()