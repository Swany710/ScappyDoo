"""
ScappyDoo - City Permit Web Scraper
Main entry point for scraping city permit data.
"""
import json
import argparse
import logging
from pathlib import Path
from permit_scraper import PermitScraper
from exporters import PermitExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise


def main():
    """Main function to run the permit scraper."""
    parser = argparse.ArgumentParser(
        description='ScappyDoo - City Permit Web Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape permits using a config file
  python main.py --config configs/example_config.json --url "https://example.com/permits" --output permits.csv

  # Scrape with JSON output
  python main.py -c configs/generic_table_config.json -u "https://city.gov/permits" -o permits.json

  # Limit to 5 pages and export to Excel
  python main.py -c configs/example_config.json -u "https://permits.city.gov" -o permits.xlsx --max-pages 5

  # Enable debug logging
  python main.py -c configs/example_config.json -u "https://city.gov/permits" -o permits.csv --debug
        """
    )

    parser.add_argument(
        '-c', '--config',
        required=True,
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='Starting URL to scrape permits from'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file path (.json, .csv, or .xlsx)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Maximum number of pages to scrape (default: unlimited)'
    )
    parser.add_argument(
        '--scrape-details',
        action='store_true',
        help='Scrape detailed information for each permit (slower)'
    )
    parser.add_argument(
        '--summary',
        help='Path to save summary statistics (JSON format)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    config = load_config(args.config)

    # Extract scraper settings
    scraper_settings = config.get('scraper_settings', {})

    # Initialize scraper
    logger.info(f"Initializing scraper for {config.get('city_name', 'Unknown City')}")
    with PermitScraper(config, **scraper_settings) as scraper:
        # Scrape permits
        permits = scraper.scrape_permits(args.url, max_pages=args.max_pages)

        if not permits:
            logger.warning("No permits were scraped!")
            return

        # Scrape details if requested
        if args.scrape_details:
            logger.info("Scraping detailed information for each permit...")
            detailed_permits = []
            for i, permit in enumerate(permits, 1):
                logger.info(f"Scraping details for permit {i}/{len(permits)}")
                detailed_permit = scraper.scrape_permit_details(permit)
                detailed_permits.append(detailed_permit)
            permits = detailed_permits

        # Export data
        output_path = Path(args.output)
        output_ext = output_path.suffix.lower()

        logger.info(f"Exporting {len(permits)} permits to {args.output}")

        if output_ext == '.json':
            PermitExporter.to_json(permits, args.output)
        elif output_ext == '.csv':
            PermitExporter.to_csv(permits, args.output)
        elif output_ext in ['.xlsx', '.xls']:
            PermitExporter.to_excel(permits, args.output)
        else:
            logger.error(f"Unsupported output format: {output_ext}")
            logger.info("Supported formats: .json, .csv, .xlsx")
            return

        # Generate and save summary if requested
        if args.summary:
            logger.info("Generating summary statistics...")
            summary = PermitExporter.generate_summary(permits)
            PermitExporter.save_summary(summary, args.summary)

            # Print summary to console
            print("\n" + "=" * 60)
            print("SCRAPING SUMMARY")
            print("=" * 60)
            print(f"Total Permits: {summary.get('total_permits', 0)}")

            if 'permit_types' in summary:
                print("\nPermit Types:")
                for ptype, count in summary['permit_types'].items():
                    print(f"  - {ptype}: {count}")

            if 'status_counts' in summary:
                print("\nStatus Counts:")
                for status, count in summary['status_counts'].items():
                    print(f"  - {status}: {count}")

            if 'date_range' in summary:
                print("\nDate Range:")
                print(f"  Earliest: {summary['date_range']['earliest']}")
                print(f"  Latest: {summary['date_range']['latest']}")

            print("=" * 60 + "\n")

    logger.info("Scraping completed successfully!")


if __name__ == '__main__':
    main()
