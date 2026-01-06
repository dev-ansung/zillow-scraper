import logging
from typing import List

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

                results.append(PropertyData(
                    address=address,
                    price=price,
                    link=link,
                    beds=beds,
                    baths=baths,
                    sqft=sqft
                ))

            except Exception as e:
                logging.warning(f"Skipping a card due to error: {e}")
                continue
                
        return results