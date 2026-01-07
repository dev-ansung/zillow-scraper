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
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    # Console Handler (Streams to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(console_handler)

    logging.info(f"Logging initialized. Writing to {log_file}")


def main():
    parser = argparse.ArgumentParser(description="Scrape Zillow listings.")
    parser.add_argument(
        "target", help="The Zillow URL to scrape or an address to search for (use --address flag)"
    )
    parser.add_argument(
        "--address",
        action="store_true",
        help="Treat the target as an address and fetch detailed property information",
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run without a visible browser window"
    )
    parser.add_argument(
        "--csv", help="Output file name (default: auto-generated in ./output)", default=None
    )
    args = parser.parse_args()

    setup_logging()

    browser = SmartScrollerBrowser(headless=args.headless)
    parser_obj = ZillowExactParser()
    service = ZillowService(browser, parser_obj)

    try:
        if args.address:
            # Address-based search for detailed property information
            property_data = service.search_by_address(args.target)

            if property_data:
                properties = [property_data]
                print(f"\n{'=' * 60}")
                print("PROPERTY FOUND: Detailed Information")
                print(f"{'=' * 60}")
                print(format_property_detail(property_data))
            else:
                properties = []
                print(f"\n{'=' * 60}")
                print(f"NO PROPERTY FOUND for address: {args.target}")
                print(f"{'=' * 60}")
        else:
            # Original URL-based search
            properties = service.run(args.target)

            print(f"\n{'=' * 60}")
            print(f"SCRAPE COMPLETE: Found {len(properties)} Listings")
            print(f"{'=' * 60}")

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
                writer.writerow(
                    [
                        "Scraped_At",
                        "Price",
                        "Beds",
                        "Baths",
                        "Sqft",
                        "Address",
                        "Link",
                        "Property_Type",
                        "Year_Built",
                        "Lot_Size",
                        "HOA",
                    ]
                )
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
        f"{p.address}",
    ]
    return " | ".join(listing_parts)


def format_property_detail(p):
    """Format detailed property information for console output."""
    lines = [
        f"Address:       {p.address}",
        f"Price:         {p.price}",
        f"Beds:          {p.beds}",
        f"Baths:         {p.baths}",
        f"Square Feet:   {p.sqft}",
        f"Property Type: {p.property_type}",
        f"Year Built:    {p.year_built}",
        f"Lot Size:      {p.lot_size}",
        f"HOA:           {p.hoa}",
        f"Link:          {p.link}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
