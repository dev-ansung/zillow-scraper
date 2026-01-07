import logging
from typing import List, Optional

from bs4 import BeautifulSoup

from .interfaces import IParser
from .models import PropertyData


class ZillowExactParser(IParser):
    def parse(self, html_content: str) -> List[PropertyData]:
        soup = BeautifulSoup(html_content, "html.parser")
        results = []

        # Target only valid property cards
        cards = soup.find_all("article", {"data-test": "property-card"})
        logging.info(f"Parser found {len(cards)} raw property cards.")

        for card in cards:
            try:
                price_tag = card.find("span", {"data-test": "property-card-price"})
                price = price_tag.get_text().strip() if price_tag else "N/A"

                addr_tag = card.find("address")
                address = addr_tag.get_text().strip() if addr_tag else "N/A"

                link = ""
                link_tag = card.find("a", {"data-test": "property-card-link"})
                if link_tag:
                    href_val = link_tag.get("href")

                    if isinstance(href_val, str):
                        link = href_val
                    elif isinstance(href_val, list) and len(href_val) > 0:
                        link = str(href_val[0])

                if link and not link.startswith("http"):
                    link = "https://www.zillow.com" + link

                # --- Details ---
                beds, baths, sqft = "N/A", "N/A", "N/A"
                details_ul = card.find("ul", {"data-testid": "property-card-details"})

                if details_ul:
                    lis = details_ul.find_all("li")
                    for li in lis:
                        text = li.get_text(" ", strip=True).lower()
                        if "bds" in text or "bd" in text:
                            beds = text.replace("bds", "").replace("bd", "").strip()
                        elif "ba" in text:
                            baths = text.replace("ba", "").strip()
                        elif "sqft" in text:
                            sqft = text.replace("sqft", "").strip()

                results.append(
                    PropertyData(
                        address=address, price=price, link=link, beds=beds, baths=baths, sqft=sqft
                    )
                )

            except Exception as e:
                logging.warning(f"Skipping a card due to error: {e}")
                continue

        return results


class ZillowPropertyDetailParser:
    """Parser for individual property detail pages."""

    @staticmethod
    def _clean_sqft_value(text: str) -> str:
        """
        Cleans and extracts square footage value from text.

        Args:
            text (str): Raw text containing square footage information.

        Returns:
            str: Cleaned square footage value.
        """
        return text.replace("sqft", "").replace("sq. ft.", "").replace(",", "").strip()

    def parse_detail(self, html_content: str) -> Optional[PropertyData]:
        """
        Parses a Zillow property detail page and extracts comprehensive information.

        Args:
            html_content (str): The HTML content of a property detail page.

        Returns:
            Optional[PropertyData]: Extracted property data or None if parsing fails.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        try:
            # Extract price
            price = "N/A"
            price_selectors = [
                ("span", {"data-testid": "price"}),
                ("span", {"class": "ds-value"}),
                ("h3", {"class": "ds-price"}),
            ]
            for tag, attrs in price_selectors:
                price_tag = soup.find(tag, attrs)
                if price_tag:
                    price = price_tag.get_text().strip()
                    break

            # Extract address
            address = "N/A"
            addr_tag = soup.find("h1", {"class": "ds-address-container"})
            if not addr_tag:
                addr_tag = soup.find("h1")
            if addr_tag:
                address = addr_tag.get_text().strip()

            # Extract basic details (beds, baths, sqft)
            beds, baths, sqft = "N/A", "N/A", "N/A"

            # Try to find the facts section
            facts_section = soup.find("div", {"class": "ds-home-fact-list"})
            if facts_section:
                fact_items = facts_section.find_all("span")
                for item in fact_items:
                    text = item.get_text(" ", strip=True).lower()
                    if "bed" in text or "bd" in text:
                        beds = text.split()[0]
                    elif "bath" in text or "ba" in text:
                        baths = text.split()[0]
                    elif "sqft" in text or "sq. ft" in text:
                        sqft = self._clean_sqft_value(text)

            # Fallback: Try the summary section
            if beds == "N/A" or baths == "N/A" or sqft == "N/A":
                summary = soup.find("div", {"class": "ds-summary-row"})
                if summary:
                    spans = summary.find_all("span")
                    for span in spans:
                        text = span.get_text(" ", strip=True).lower()
                        if "bed" in text and beds == "N/A":
                            beds = text.split()[0]
                        elif "bath" in text and baths == "N/A":
                            baths = text.split()[0]
                        elif ("sqft" in text or "sq. ft" in text) and sqft == "N/A":
                            sqft = self._clean_sqft_value(text)

            # Extract additional details
            property_type = "N/A"
            year_built = "N/A"
            lot_size = "N/A"
            hoa = "N/A"

            # Look for additional facts in the details section
            detail_rows = soup.find_all("div", {"class": "ds-home-fact-list-item"})
            for row in detail_rows:
                label_tag = row.find("span", {"class": "ds-home-fact-label"})
                value_tag = row.find("span", {"class": "ds-home-fact-value"})

                if label_tag and value_tag:
                    label = label_tag.get_text().strip().lower()
                    value = value_tag.get_text().strip()

                    if "type" in label:
                        property_type = value
                    elif "year built" in label or "built" in label:
                        year_built = value
                    elif "lot" in label:
                        lot_size = value
                    elif "hoa" in label:
                        hoa = value

            # Get the current URL as the link
            link = "N/A"
            canonical_tag = soup.find("link", {"rel": "canonical"})
            if canonical_tag and canonical_tag.get("href"):
                link = canonical_tag.get("href")

            return PropertyData(
                address=address,
                price=price,
                link=link,
                beds=beds,
                baths=baths,
                sqft=sqft,
                property_type=property_type,
                year_built=year_built,
                lot_size=lot_size,
                hoa=hoa,
            )

        except Exception as e:
            logging.error(f"Failed to parse property detail page: {e}")
            return None
