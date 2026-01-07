import logging
from typing import TYPE_CHECKING, List, Optional

from bs4 import BeautifulSoup

from .interfaces import IParser
from .models import PropertyData

if TYPE_CHECKING:
    from .models import (
        AddressInfo,
        CommunityAmenities,
        InteriorFeatures,
        ListingInfo,
        LocationScores,
        PriceDetails,
        PropertyBasics,
        PropertyDetail,
        SchoolInfo,
    )


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


class ZillowComprehensiveDetailParser:
    """Parser for extracting comprehensive property details from Zillow property pages."""

    def __init__(self):
        self.logger = logging.getLogger("ZillowComprehensiveDetailParser")

    def parse(self, html_content: str, url: str = "N/A") -> Optional["PropertyDetail"]:
        """
        Parses a Zillow property detail page and extracts comprehensive information.

        Args:
            html_content: The HTML content of the property detail page.
            url: The URL of the property page.

        Returns:
            PropertyDetail object with all extracted information, or None if parsing fails.
        """
        from .models import (
            PropertyDetail,
        )

        soup = BeautifulSoup(html_content, "html.parser")

        try:
            # Parse address
            address_info = self._parse_address(soup)

            # Parse price details
            price_details = self._parse_price_details(soup)

            # Parse property basics
            property_basics = self._parse_property_basics(soup)

            # Parse interior features
            interior_features = self._parse_interior_features(soup)

            # Parse community amenities
            community_amenities = self._parse_community_amenities(soup)

            # Parse location scores
            location_scores = self._parse_location_scores(soup)

            # Parse nearby schools
            nearby_schools = self._parse_nearby_schools(soup)

            # Parse listing info
            listing_info = self._parse_listing_info(soup)

            return PropertyDetail(
                address=address_info,
                price_details=price_details,
                property_basics=property_basics,
                interior_features=interior_features,
                community_amenities=community_amenities,
                location_scores=location_scores,
                nearby_schools=nearby_schools,
                listing_info=listing_info,
                url=url,
            )

        except Exception as e:
            self.logger.error(f"Failed to parse comprehensive property details: {e}", exc_info=True)
            return None

    def _parse_address(self, soup: BeautifulSoup) -> "AddressInfo":
        """Parse address information."""
        from .models import AddressInfo

        address_info = AddressInfo()

        # Try to find address in h1 tag
        h1_tag = soup.find("h1", {"class": "ds-address-container"})
        if not h1_tag:
            h1_tag = soup.find("h1")

        if h1_tag:
            full_address = h1_tag.get_text(strip=True)
            # Parse the address string
            parts = [p.strip() for p in full_address.split(",")]
            if len(parts) >= 1:
                address_info.street = parts[0]
            if len(parts) >= 2:
                address_info.city = parts[1]
            if len(parts) >= 3:
                # Last part contains state and zip
                state_zip = parts[2].strip().split()
                if len(state_zip) >= 1:
                    address_info.state = state_zip[0]
                if len(state_zip) >= 2:
                    address_info.zip_code = state_zip[1]

        return address_info

    def _parse_price_details(self, soup: BeautifulSoup) -> "PriceDetails":
        """Parse price and financial details."""
        from .models import PriceDetails

        price_details = PriceDetails()

        # Extract list price
        price_tag = soup.find("span", {"data-testid": "price"})
        if not price_tag:
            price_tag = soup.find("span", {"class": "ds-value"})
        if price_tag:
            price_text = price_tag.get_text().strip().replace("$", "").replace(",", "")
            try:
                price_details.list_price = int(price_text)
            except:
                pass

        # Extract price per sqft
        price_sqft_spans = soup.find_all("span")
        for span in price_sqft_spans:
            text = span.get_text().lower()
            if "/sqft" in text or "per sq ft" in text:
                try:
                    price_per_sqft = (
                        text.replace("$", "").replace("/sqft", "").replace(",", "").strip()
                    )
                    price_details.price_per_sqft = int(float(price_per_sqft))
                except:
                    pass
                break

        # Extract monthly payment estimate
        payment_spans = soup.find_all("span")
        for span in payment_spans:
            text = span.get_text()
            if "Est. payment" in text or "mo" in text.lower():
                try:
                    # Look for sibling or nearby elements with the amount
                    parent = span.find_parent()
                    if parent:
                        amount_text = (
                            parent.get_text().replace("$", "").replace(",", "").replace("/mo", "")
                        )
                        import re

                        numbers = re.findall(r"\d+", amount_text)
                        if numbers:
                            price_details.est_monthly_payment = int(numbers[0])
                except:
                    pass
                break

        # Extract Zestimate
        zestimate_divs = soup.find_all("div")
        for div in zestimate_divs:
            text = div.get_text()
            if "Zestimate" in text:
                try:
                    import re

                    numbers = re.findall(r"\$([0-9,]+)", text)
                    if numbers:
                        price_details.zestimate = int(numbers[0].replace(",", ""))
                except:
                    pass
                break

        # Extract tax information
        tax_spans = soup.find_all("span")
        for span in tax_spans:
            text = span.get_text()
            if "Tax assessed value" in text or "Assessed Value" in text:
                try:
                    parent = span.find_parent()
                    if parent:
                        import re

                        numbers = re.findall(r"\$([0-9,]+)", parent.get_text())
                        if numbers:
                            price_details.tax_assessed_value = int(numbers[0].replace(",", ""))
                except:
                    pass

            if "Annual tax amount" in text or "Property taxes" in text:
                try:
                    parent = span.find_parent()
                    if parent:
                        import re

                        numbers = re.findall(r"\$([0-9,]+)", parent.get_text())
                        if numbers:
                            price_details.annual_tax_amount = int(numbers[0].replace(",", ""))
                except:
                    pass

        return price_details

    def _parse_property_basics(self, soup: BeautifulSoup) -> "PropertyBasics":
        """Parse basic property characteristics."""
        from .models import PropertyBasics

        basics = PropertyBasics()

        # Find all fact items
        fact_items = soup.find_all("span")

        for span in fact_items:
            text = span.get_text(" ", strip=True)

            # Extract bedrooms
            if ("bed" in text.lower() or "bd" in text.lower()) and basics.bedrooms is None:
                try:
                    import re

                    numbers = re.findall(r"(\d+)", text)
                    if numbers:
                        basics.bedrooms = int(numbers[0])
                except:
                    pass

            # Extract bathrooms
            if ("bath" in text.lower() or "ba" in text.lower()) and basics.bathrooms is None:
                try:
                    import re

                    numbers = re.findall(r"(\d+\.?\d*)", text)
                    if numbers:
                        basics.bathrooms = float(numbers[0])
                        basics.full_bathrooms = int(float(numbers[0]))
                except:
                    pass

            # Extract square footage
            if (
                "sqft" in text.lower() or "sq. ft" in text.lower()
            ) and basics.square_footage is None:
                try:
                    import re

                    numbers = re.findall(r"([0-9,]+)", text)
                    if numbers:
                        basics.square_footage = int(numbers[0].replace(",", ""))
                except:
                    pass

        # Find facts in the fact list
        fact_list = soup.find("div", {"class": "ds-home-fact-list"})
        if not fact_list:
            fact_list = soup.find("ul", {"class": "ds-home-facts-and-features"})

        if fact_list:
            fact_rows = fact_list.find_all(["li", "div"])
            for row in fact_rows:
                text = row.get_text(" ", strip=True)

                # Home type
                if "Type" in text or "Property Type" in text:
                    parts = text.split(":")
                    if len(parts) > 1:
                        basics.home_type = parts[1].strip()

                # Year built
                if "Year Built" in text or "Built in" in text:
                    try:
                        import re

                        numbers = re.findall(r"(\d{4})", text)
                        if numbers:
                            basics.year_built = int(numbers[0])
                    except:
                        pass

                # Stories
                if "Stories" in text or "Floor" in text.lower():
                    try:
                        import re

                        numbers = re.findall(r"(\d+)", text)
                        if numbers:
                            basics.stories = int(numbers[0])
                    except:
                        pass

                # Zoning
                if "Zoning" in text:
                    parts = text.split(":")
                    if len(parts) > 1:
                        basics.zoning = parts[1].strip()

                # Parcel number
                if "Parcel" in text or "APN" in text:
                    parts = text.split(":")
                    if len(parts) > 1:
                        basics.parcel_number = parts[1].strip()

        return basics

    def _parse_interior_features(self, soup: BeautifulSoup) -> "InteriorFeatures":
        """Parse interior features."""
        from .models import InteriorFeatures

        features = InteriorFeatures()

        # Find the features section
        feature_sections = soup.find_all(
            "div", {"class": ["ds-home-facts-and-features", "fact-group"]}
        )

        for section in feature_sections:
            section_text = section.get_text()

            # Flooring
            if "Flooring" in section_text or "Floor" in section_text:
                items = section.find_all("li")
                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) < 100:  # Reasonable length for a feature
                        features.flooring.append(text)

            # Kitchen features
            if "Kitchen" in section_text or "Appliances" in section_text:
                items = section.find_all("li")
                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) < 100:
                        features.kitchen.append(text)

            # Bathroom features
            if "Bathroom" in section_text:
                items = section.find_all("li")
                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) < 100:
                        features.bathroom_features.append(text)

            # Laundry
            if "Laundry" in section_text:
                text = section.get_text(strip=True)
                if ":" in text:
                    features.laundry = text.split(":")[-1].strip()

            # Cooling
            if "Cooling" in section_text:
                text = section.get_text(strip=True)
                if ":" in text:
                    features.cooling = text.split(":")[-1].strip()

            # Heating
            if "Heating" in section_text:
                text = section.get_text(strip=True)
                if ":" in text:
                    features.heating = text.split(":")[-1].strip()

        return features

    def _parse_community_amenities(self, soup: BeautifulSoup) -> "CommunityAmenities":
        """Parse community amenities."""
        from .models import CommunityAmenities, ParkingInfo

        amenities = CommunityAmenities()
        amenities.parking = ParkingInfo()

        # Find HOA fee
        hoa_spans = soup.find_all("span")
        for span in hoa_spans:
            text = span.get_text()
            if "HOA" in text or "hoa" in text.lower():
                try:
                    import re

                    numbers = re.findall(r"\$([0-9,]+)", text)
                    if numbers:
                        amenities.hoa_fee_monthly = int(numbers[0].replace(",", ""))
                except:
                    pass
                break

        # Find parking information
        parking_text = soup.find_all(string=lambda text: text and "parking" in text.lower())
        for text in parking_text:
            try:
                import re

                numbers = re.findall(r"(\d+)", str(text))
                if numbers and amenities.parking.total_spaces is None:
                    amenities.parking.total_spaces = int(numbers[0])
            except:
                pass

        return amenities

    def _parse_location_scores(self, soup: BeautifulSoup) -> "LocationScores":
        """Parse walk, transit, and bike scores."""
        from .models import LocationScores

        scores = LocationScores()

        # Find score elements
        score_divs = soup.find_all("div")
        for div in score_divs:
            text = div.get_text()

            if "Walk Score" in text:
                try:
                    import re

                    numbers = re.findall(r"(\d+)", text)
                    if numbers:
                        scores.walk_score = int(numbers[0])
                except:
                    pass

            if "Transit Score" in text:
                try:
                    import re

                    numbers = re.findall(r"(\d+)", text)
                    if numbers:
                        scores.transit_score = int(numbers[0])
                except:
                    pass

            if "Bike Score" in text:
                try:
                    import re

                    numbers = re.findall(r"(\d+)", text)
                    if numbers:
                        scores.bike_score = int(numbers[0])
                except:
                    pass

        return scores

    def _parse_nearby_schools(self, soup: BeautifulSoup) -> List["SchoolInfo"]:
        """Parse nearby schools information."""
        from .models import SchoolInfo

        schools = []

        # Find school section
        school_section = soup.find("div", {"class": lambda x: x and "schools" in x.lower()})
        if school_section:
            school_items = school_section.find_all("div", recursive=True)

            for item in school_items:
                text = item.get_text(strip=True)
                # Simple school detection - you may need to adjust based on actual HTML structure
                if "Elementary" in text or "Middle" in text or "High" in text:
                    school = SchoolInfo()
                    school.name = text
                    schools.append(school)

        return schools

    def _parse_listing_info(self, soup: BeautifulSoup) -> "ListingInfo":
        """Parse listing status and agent information."""
        from .models import ListingInfo

        listing = ListingInfo()

        # Find listing status
        status_spans = soup.find_all("span")
        for span in status_spans:
            text = span.get_text(strip=True)
            if text in ["For Sale", "For Rent", "Sold", "Pending", "Active"]:
                listing.status = text
                break

        # Find days on Zillow
        days_text = soup.find_all(
            string=lambda text: text and "days on Zillow" in str(text).lower()
        )
        if days_text:
            try:
                import re

                numbers = re.findall(r"(\d+)", str(days_text[0]))
                if numbers:
                    listing.days_on_zillow = int(numbers[0])
            except:
                pass

        # Find MLS number
        mls_text = soup.find_all(string=lambda text: text and "MLS" in str(text))
        if mls_text:
            try:
                import re

                # Look for MLS number pattern
                match = re.search(r"MLS[#:\s]+([A-Z0-9]+)", str(mls_text[0]))
                if match:
                    listing.mls_number = match.group(1)
            except:
                pass

        # Find listing agent
        agent_divs = soup.find_all("div", {"class": lambda x: x and "agent" in str(x).lower()})
        for div in agent_divs:
            text = div.get_text(strip=True)
            if text and "(" in text and ")" in text:
                listing.listing_agent = text
                break

        return listing
