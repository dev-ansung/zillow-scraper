import argparse
import csv
import logging
import os
from datetime import datetime

from .browsers import SmartScrollerBrowser
from .parsers import ZillowExactParser
from .services import ZillowService


def setup_logging():
    """Configures logging to stream to both console and a file."""
    log_dir = "./output/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File Handler (Streams to ./output/logs/TIMESTAMP.log)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console Handler (Streams to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Writing to {log_file}")

def main():
    parser = argparse.ArgumentParser(description="Scrape Zillow listings.")
    parser.add_argument(
        "url", help="The Zillow URL to scrape")
    parser.add_argument(
        "--headless", action="store_true", help="Run without a visible browser window")
    parser.add_argument(
        "--csv",
        help="Output file name (default: auto-generated in ./output)",
        default=None)
    args = parser.parse_args()

    setup_logging()
    
    browser = SmartScrollerBrowser(headless=args.headless)
    parser = ZillowExactParser()
    service = ZillowService(browser, parser)

    try:
        properties = service.run(args.url)

        print(f"\n{'='*60}")
        print(f"SCRAPE COMPLETE: Found {len(properties)} Listings")
        print(f"{'='*60}")
        
        for p in properties:
            print(format_property_listing(p))

        # Determine output path
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        
        if args.csv:
            # If user provided a path, check if it is absolute. If not, put it in output_dir
            csv_path = args.csv if os.path.isabs(args.csv) else os.path.join(output_dir, args.csv)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(output_dir, f"results_{timestamp}.csv")

        if properties:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Scraped_At", "Price", "Beds", "Baths", "Sqft", "Address", "Link"])
                for p in properties:
                    writer.writerow(p.to_csv_row())
            logging.info(f"Data saved to {csv_path}")
        else:
            logging.warning("No data found, skipping CSV generation.")

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        pass

def format_property_listing(p):
    listing_parts = [
        f"{p.price:<12}",
        f"{p.beds:>2} bd",
        f"{p.baths:>2} ba",
        f"{p.sqft:>6} sqft",
        f"{p.address}"
    ]
    return " | ".join(listing_parts)

if __name__ == "__main__":
    main()