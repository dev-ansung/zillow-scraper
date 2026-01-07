# Zillow Scraper

A robust extraction engine for retrieving real estate listing data from Zillow. This utility leverages `SeleniumBase` (Undetected ChromeDriver) to circumvent automated bot detection systems and implements a heuristics engine to manage lazy-loaded DOM elements.

## Overview

This package provides a mechanism to programmatically retrieve property data—including pricing, address, structural details (beds, baths, square footage), and listing URLs—from Zillow search result pages. It is designed for environments where standard HTTP requests fail due to TLS fingerprinting or CAPTCHA challenges.

## Features

* **Bot Detection Evasion**: Implements an undetected browser instance to bypass Cloudflare/Akamai security layers.
* **Lazy Loading Handler**: Simulates human-like scroll events to trigger AJAX requests for paginated data, ensuring complete dataset retrieval.
* **Async API**: Non-blocking asynchronous interface for integration into modern Python applications.
* **Structured Parsing**: Utilizes `BeautifulSoup` with stable selector targeting (`data-test` attributes).
* **Data Serialization**: Exports extracted entities to CSV format with ISO 8601 timestamping.

## Prerequisites

* Python 3.10 or higher
* Google Chrome (latest stable release)
* `uv` (Python package manager)

## Installation

### Library Integration (Recommended)
To add the scraper as a dependency in your existing Python project:

```bash
uv add git+[https://github.com/dev-ansung/zillow-scraper.git](https://github.com/dev-ansung/zillow-scraper.git)

```

### CLI Tool Installation

To install the package globally as a standalone command-line tool:

```bash
uv tool install git+https://github.com/dev-ansung/zillow-scraper.git

```

## Usage

### Library Usage (Python)

#### Fetch Listings by Location

The package exposes a high-level asynchronous API, `fetch_listings`, designed for seamless integration into application event loops.

```python
import asyncio
from zillow_scraper import fetch_listings

async def main():
    # Execute the scraping pipeline for a location
    properties = await fetch_listings(
        url="https://www.zillow.com/mountain-view-ca-94043", 
        headless=True
    )
    
    print(f"Extracted {len(properties)} listings:")
    for p in properties:
        print(f"[{p.timestamp}] {p.price} - {p.address}")

if __name__ == "__main__":
    asyncio.run(main())

```

#### Fetch Comprehensive Property Details by Address or URL

Fetch detailed information for a specific property by providing either an address or a direct Zillow property URL. Returns a comprehensive `PropertyDetail` object with extensive information.

```python
import asyncio
from zillow_scraper import fetch_property_by_address

async def main():
    # Option 1: By address
    property_detail = await fetch_property_by_address(
        address_or_url="1033 Crestview Dr APT 216, Mountain View, CA 94040",
        headless=True
    )
    
    # Option 2: By Zillow URL
    property_detail = await fetch_property_by_address(
        address_or_url="https://www.zillow.com/homedetails/1033-Crestview-Dr-APT-216-Mountain-View-CA-94040/19538316_zpid/",
        headless=True
    )
    
    if property_detail:
        # Access detailed information
        print(f"Address: {property_detail.address.street}, {property_detail.address.city}")
        print(f"Price: ${property_detail.price_details.list_price}")
        print(f"Bedrooms: {property_detail.property_basics.bedrooms}")
        print(f"Home Type: {property_detail.property_basics.home_type}")
        print(f"HOA: ${property_detail.community_amenities.hoa_fee_monthly}/mo")
        
        # Export to JSON
        json_data = property_detail.to_json(indent=2)
        print(json_data)
    else:
        print("Property not found")

if __name__ == "__main__":
    asyncio.run(main())

```

### Command Line Usage

If installed via `uv tool`, the `zillow-scrape` command is available directly. The CLI automatically detects whether you're providing a URL or an address.

#### Scrape Listings by Location

```bash
zillow-scrape "https://www.zillow.com/mountain-view-ca-94043" --csv output.csv

```

#### Fetch Property Details by Address

Returns comprehensive JSON with detailed property information:

```bash
zillow-scrape "1033 Crestview Dr APT 216, Mountain View, CA 94040"

```

Output will be a JSON object with the following structure:
- `address`: Street, city, state, ZIP code
- `price_details`: List price, price per sqft, monthly payment estimate, Zestimate, tax info
- `property_basics`: Home type, bedrooms, bathrooms, square footage, year built, stories, zoning, parcel number
- `interior_features`: Flooring, kitchen, bathroom features, laundry, cooling, heating, highlights
- `community_amenities`: HOA fees, parking, pool, accessibility, storage
- `location_scores`: Walk score, transit score, bike score
- `nearby_schools`: Names, ratings, grades
- `listing_info`: Status, days on Zillow, MLS number, agent, last updated

#### Fetch Property Details by URL

```bash
zillow-scrape "https://www.zillow.com/homedetails/1033-Crestview-Dr-APT-216-Mountain-View-CA-94040/19538316_zpid/"

```

#### Save JSON Output to File

```bash
zillow-scrape "1033 Crestview Dr APT 216, Mountain View, CA 94040" --json property.json

```

**Options:**

* `--headless`: Execute without a visible UI window.
* `--csv [PATH]`: Define the output path for CSV file (for listing searches only).
* `--json [PATH]`: Define the output path for JSON file (for property details). If omitted, prints to console.

* `--headless`: Execute without a visible UI window.
* `--csv [PATH]`: Define the output path for CSV file (for listing searches only).
* `--json [PATH]`: Define the output path for JSON file (for property details). If omitted, prints to console.

## Output Artifacts

The application generates artifacts in the `./output` directory relative to the execution root:

* **Logs**: `./output/logs/YYYYMMDD_HHMMSS.log` (Runtime events and debug traces).
* **CSV Data** (for listing searches): `./output/results_YYYYMMDD_HHMMSS.csv` (Scraped dataset with columns: Scraped_At, Price, Beds, Baths, Sqft, Address, Link, Property_Type, Year_Built, Lot_Size, HOA).
* **JSON Data** (for property details): Comprehensive property information in JSON format with address, price details, property basics, interior features, community amenities, location scores, nearby schools, and listing info.

## Development

### Project Structure

* `zillow_scraper/`: Core package.
* `api.py`: Asynchronous public API.
* `browsers.py`: SeleniumBase wrapper and scrolling logic.
* `parsers.py`: HTML parsing logic.
* `services.py`: Pipeline orchestration.
* `models.py`: Data transfer objects.


* `tests/`: Unit tests and HTML fixtures.

### Testing & Quality

```bash
# Run unit tests
uv run pytest

# Check for linting errors
uv run ruff check .

# Apply formatting
uv run ruff format .

```

## Troubleshooting

### Zero Results Returned

If the tool returns 0 listings, Zillow may have presented a CAPTCHA.
**Resolution**: Set `headless=False` (in Python) or remove the `--headless` flag (in CLI). Manually solve the challenge in the browser window; execution will resume automatically.

## Disclaimer

This software is for educational and research purposes only. Scraping Zillow data may violate their Terms of Use. The maintainers assume no liability for misuse or IP blocks.
