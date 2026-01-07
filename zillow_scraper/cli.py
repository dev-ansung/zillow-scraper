import argparse
import asyncio
import csv
import logging
import os
from datetime import datetime

from .api import fetch_listings, fetch_property_by_address


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


def is_zillow_url(target: str) -> bool:
    """Check if the target is a Zillow URL."""
    return target.startswith("http://") or target.startswith("https://")


def is_listing_search_url(target: str) -> bool:
    """Check if the target is a listing search URL (contains /homes or location-based)."""
    return "/homes" in target or (
        "-" in target and "zillow.com" in target and "/homedetails/" not in target
    )


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Zillow listings or fetch detailed property information."
    )
    parser.add_argument(
        "target",
        help=(
            "Target can be: "
            "(1) A Zillow property detail URL, "
            "(2) A property address string, or "
            "(3) A Zillow listing search URL"
        ),
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run without a visible browser window"
    )
    parser.add_argument(
        "--csv",
        help="Output CSV file name for listing searches (default: auto-generated in ./output)",
        default=None,
    )
    parser.add_argument(
        "--json",
        help="Output JSON file name for property details (default: print to console)",
        default=None,
    )
    args = parser.parse_args()

    setup_logging()

    try:
        # Detect what type of target we have
        if is_zillow_url(args.target):
            if is_listing_search_url(args.target):
                # It's a listing search URL - use fetch_listings
                logging.info(f"Detected listing search URL: {args.target}")
                properties = asyncio.run(fetch_listings(args.target, headless=args.headless))

                print(f"\n{'=' * 60}")
                print(f"SCRAPE COMPLETE: Found {len(properties)} Listings")
                print(f"{'=' * 60}\n")

                for p in properties:
                    print(format_property_listing(p))

                # Save to CSV if properties found
                if properties:
                    save_to_csv(properties, args.csv)
                else:
                    logging.warning("No properties found.")

            else:
                # It's a property detail URL - use fetch_property_by_address
                logging.info(f"Detected property detail URL: {args.target}")
                property_detail = asyncio.run(
                    fetch_property_by_address(args.target, headless=args.headless)
                )

                if property_detail:
                    # Output JSON
                    json_output = property_detail.to_json(indent=2)

                    if args.json:
                        # Save to file
                        output_dir = "./output"
                        os.makedirs(output_dir, exist_ok=True)
                        json_path = (
                            args.json
                            if os.path.isabs(args.json)
                            else os.path.join(output_dir, args.json)
                        )
                        with open(json_path, "w", encoding="utf-8") as f:
                            f.write(json_output)
                        logging.info(f"Property details saved to {json_path}")
                        print(f"\nProperty details saved to: {json_path}")
                    else:
                        # Print to console
                        print(json_output)
                else:
                    print("No property found.")
        else:
            # It's an address string - use fetch_property_by_address
            logging.info(f"Detected address string: {args.target}")
            property_detail = asyncio.run(
                fetch_property_by_address(args.target, headless=args.headless)
            )

            if property_detail:
                # Output JSON
                json_output = property_detail.to_json(indent=2)

                if args.json:
                    # Save to file
                    output_dir = "./output"
                    os.makedirs(output_dir, exist_ok=True)
                    json_path = (
                        args.json
                        if os.path.isabs(args.json)
                        else os.path.join(output_dir, args.json)
                    )
                    with open(json_path, "w", encoding="utf-8") as f:
                        f.write(json_output)
                    logging.info(f"Property details saved to {json_path}")
                    print(f"\nProperty details saved to: {json_path}")
                else:
                    # Print to console
                    print(json_output)
            else:
                print("No property found.")

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"Error: {e}")


def save_to_csv(properties, csv_arg):
    """Save properties to CSV file."""
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    if csv_arg:
        csv_path = csv_arg if os.path.isabs(csv_arg) else os.path.join(output_dir, csv_arg)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(output_dir, f"results_{timestamp}.csv")

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
    print(f"Data saved to: {csv_path}")


def format_property_listing(p):
    listing_parts = [
        f"{p.price:<12}",
        f"{p.beds:>2} bd",
        f"{p.baths:>2} ba",
        f"{p.sqft:>6} sqft",
        f"{p.address}",
    ]
    return " | ".join(listing_parts)


if __name__ == "__main__":
    main()
