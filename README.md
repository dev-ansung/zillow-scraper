Here is the revised `README.md` formatted to match the technical and austere style of a Chromium repository or high-standard open-source infrastructure project.

---

# Zillow Scraper

A command-line interface tool for extracting real estate listing data from Zillow. This utility utilizes `SeleniumBase` (Undetected ChromeDriver) to circumvent automated bot detection systems and implements a scroll heuristics engine to handle lazy-loaded DOM elements.

## Overview

This tool provides a mechanism to programmatically retrieve property data—including pricing, address, structural details (beds, baths, square footage), and listing URLs—from Zillow search result pages. It is designed to operate in environments where standard HTTP requests fail due to TLS fingerprinting or CAPTCHA challenges.

## Features

* **Bot Detection Evasion**: Implements an undetected browser instance to bypass Cloudflare/Akamai security layers.
* **Lazy Loading Handler**: Simulates human-like scroll events to trigger AJAX requests for paginated data, ensuring complete dataset retrieval.
* **Structured Parsing**: Utilizes `BeautifulSoup` with stable selector targeting (`data-test` attributes) to maximize resilience against frontend regressions.
* **Data Serialization**: Exports extracted entities to CSV format with ISO 8601 timestamping.
* **Logging**: Streams execution logs to file for auditing and debugging purposes.

## Prerequisites

* Python 3.10 or higher
* Google Chrome (latest stable release)
* `uv` (Python package manager)

## Installation

This project is managed via `uv`. To install the package in editable mode for local development:

```bash
git clone https://github.com/yourusername/zillow-scraper.git
cd zillow-scraper
uv pip install -e .

```

*Note: The installation process automatically pulls `seleniumbase` and `beautifulsoup4` dependencies.*

## Usage

Upon installation, the `zillow-scrape` entry point is registered in the environment path.

### Command Line Interface

```bash
zillow-scrape [URL] [OPTIONS]

```

### Arguments

* `URL`: The target Zillow search URL (Required).

### Options

* `--headless`: Execute in headless mode without a visible UI window.
* `--csv [FILE_PATH]`: Define the output path for the CSV file. If omitted, the file is saved to `./output/` with a generated timestamp.
* `-h`, `--help`: Show the help message and exit.

### Examples

**Standard execution:**

```bash
uv run zillow-scrape "https://www.zillow.com/mountain-view-ca-94043"

```

**Execution with specific output path:**

```bash
uv run zillow-scrape "https://www.zillow.com/mountain-view-ca-94043" --csv /data/extracts/mv_homes.csv

```

**Headless execution:**

```bash
uv run zillow-scrape "https://www.zillow.com/mountain-view-ca-94043" --headless

```

## Output Artifacts

The application generates output in the `./output` directory relative to the execution root:

* **Logs**: stored in `./output/logs/YYYYMMDD_HHMMSS.log`. Contains runtime events, debug information, and error traces.
* **Data**: stored in `./output/results_YYYYMMDD_HHMMSS.csv` (default). Contains the scraped dataset.

## Development

### Project Structure

* `zillow_scraper/`: Source code package.
* `cli.py`: Entry point and argument parsing.
* `browsers.py`: SeleniumBase wrapper and scrolling logic.
* `parsers.py`: HTML parsing logic.
* `services.py`: Application orchestration.
* `models.py`: Data transfer objects.


* `tests/`: Unit tests and HTML fixtures.

### Testing

Unit tests are implemented using `pytest`. Tests validate parsing logic against static HTML fixtures to ensure stability independent of live site availability.

```bash
uv run pytest

```

### Linting and Formatting

This project enforces code style using `ruff`.

**Check for linting errors:**

```bash
uv run ruff check .

```

**Apply formatting:**

```bash
uv run ruff format .

```

## Troubleshooting

### Zero Results Returned

If the tool returns 0 listings or terminates immediately, Zillow may have presented a CAPTCHA or a "Press and Hold" challenge.
**Resolution**: Run the tool without the `--headless` flag. Manually solve the challenge in the browser window. The script will detect the DOM update and resume execution.

### Module Not Found Errors

If `ImportError` or `ModuleNotFoundError` occurs, ensure the command is executed via `uv run` to utilize the correct virtual environment context.

## Disclaimer

This software is for educational and research purposes only. The scraping of Zillow data may violate the Zillow Terms of Use. The maintainers of this repository assume no liability for misuse of this software or any resulting IP blocks.