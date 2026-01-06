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
uv tool install git+[https://github.com/dev-ansung/zillow-scraper.git](https://github.com/dev-ansung/zillow-scraper.git)

```

## Usage

### Library Usage (Python)

The package exposes a high-level asynchronous API, `fetch_listings`, designed for seamless integration into application event loops.

```python
import asyncio
from zillow_scraper import fetch_listings

async def main():
    # Execute the scraping pipeline
    properties = await fetch_listings(
        url="[https://www.zillow.com/mountain-view-ca-94043](https://www.zillow.com/mountain-view-ca-94043)", 
        headless=True
    )
    
    print(f"Extracted {len(properties)} listings:")
    for p in properties:
        print(f"[{p.timestamp}] {p.price} - {p.address}")

if __name__ == "__main__":
    asyncio.run(main())

```

### Command Line Usage

If installed via `uv tool`, the `zillow-scrape` command is available directly:

```bash
zillow-scrape "[https://www.zillow.com/mountain-view-ca-94043](https://www.zillow.com/mountain-view-ca-94043)" --csv output.csv

```

**Options:**

* `--headless`: Execute without a visible UI window.
* `--csv [PATH]`: Define the output path for the CSV file. Defaults to `./output/`.

## Output Artifacts

The application generates artifacts in the `./output` directory relative to the execution root:

* **Logs**: `./output/logs/YYYYMMDD_HHMMSS.log` (Runtime events and debug traces).
* **Data**: `./output/results_YYYYMMDD_HHMMSS.csv` (Scraped dataset).

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