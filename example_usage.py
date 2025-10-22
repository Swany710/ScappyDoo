"""
Example usage of ScappyDoo permit scraper.
This demonstrates how to use the scraper programmatically.
"""
import json
from permit_scraper import PermitScraper
from exporters import PermitExporter


def example_basic_scraping():
    """Example: Basic permit scraping with CSV export."""
    print("=" * 60)
    print("Example 1: Basic Permit Scraping")
    print("=" * 60)

    # Load configuration
    with open('configs/generic_table_config.json', 'r') as f:
        config = json.load(f)

    # Initialize scraper
    scraper_settings = config.get('scraper_settings', {})
    with PermitScraper(config, **scraper_settings) as scraper:
        # Scrape permits (replace with actual URL)
        url = "https://example.city.gov/permits"
        permits = scraper.scrape_permits(url, max_pages=5)

        # Export to CSV
        if permits:
            PermitExporter.to_csv(permits, 'output/permits.csv')
            print(f"\nScraped {len(permits)} permits and saved to output/permits.csv")
        else:
            print("\nNo permits found!")


def example_with_summary():
    """Example: Scraping with summary statistics."""
    print("\n" + "=" * 60)
    print("Example 2: Scraping with Summary Statistics")
    print("=" * 60)

    # Load configuration
    with open('configs/example_config.json', 'r') as f:
        config = json.load(f)

    # Initialize scraper
    scraper_settings = config.get('scraper_settings', {})
    with PermitScraper(config, **scraper_settings) as scraper:
        # Scrape permits
        url = "https://example.city.gov/permits"
        permits = scraper.scrape_permits(url, max_pages=10)

        if permits:
            # Generate summary
            summary = PermitExporter.generate_summary(permits)

            # Print summary
            print(f"\nTotal Permits: {summary['total_permits']}")

            if 'permit_types' in summary:
                print("\nPermit Types:")
                for ptype, count in summary['permit_types'].items():
                    print(f"  - {ptype}: {count}")

            if 'status_counts' in summary:
                print("\nStatus Distribution:")
                for status, count in summary['status_counts'].items():
                    print(f"  - {status}: {count}")

            # Save summary
            PermitExporter.save_summary(summary, 'output/summary.json')
            print("\nSummary saved to output/summary.json")


def example_detailed_scraping():
    """Example: Scraping with detailed permit information."""
    print("\n" + "=" * 60)
    print("Example 3: Detailed Permit Scraping")
    print("=" * 60)

    # Load configuration
    with open('configs/example_config.json', 'r') as f:
        config = json.load(f)

    # Initialize scraper
    scraper_settings = config.get('scraper_settings', {})
    with PermitScraper(config, **scraper_settings) as scraper:
        # Scrape basic permit list
        url = "https://example.city.gov/permits"
        permits = scraper.scrape_permits(url, max_pages=3)

        if permits:
            print(f"\nFound {len(permits)} permits. Fetching details...")

            # Scrape details for each permit
            detailed_permits = []
            for i, permit in enumerate(permits[:5], 1):  # Limit to first 5 for demo
                print(f"Scraping details for permit {i}/5...")
                detailed_permit = scraper.scrape_permit_details(permit)
                detailed_permits.append(detailed_permit)

            # Export to Excel
            PermitExporter.to_excel(detailed_permits, 'output/detailed_permits.xlsx')
            print("\nDetailed permits saved to output/detailed_permits.xlsx")


def example_custom_processing():
    """Example: Custom data processing with pandas."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Data Processing")
    print("=" * 60)

    # Load configuration
    with open('configs/generic_table_config.json', 'r') as f:
        config = json.load(f)

    # Initialize scraper
    scraper_settings = config.get('scraper_settings', {})
    with PermitScraper(config, **scraper_settings) as scraper:
        # Scrape permits
        url = "https://example.city.gov/permits"
        permits = scraper.scrape_permits(url, max_pages=5)

        if permits:
            # Convert to DataFrame
            df = PermitExporter.to_dataframe(permits)

            print(f"\nTotal permits: {len(df)}")
            print(f"Columns: {', '.join(df.columns)}")

            # Example analysis
            if 'permit_type' in df.columns:
                print("\nMost common permit types:")
                print(df['permit_type'].value_counts().head())

            if 'status' in df.columns:
                print("\nPermit status breakdown:")
                print(df['status'].value_counts())

            # Filter and export
            if 'permit_type' in df.columns:
                residential = df[df['permit_type'].str.contains('Residential', case=False, na=False)]
                if not residential.empty:
                    PermitExporter.to_csv(
                        residential.to_dict('records'),
                        'output/residential_only.csv'
                    )
                    print(f"\nExported {len(residential)} residential permits")


def example_custom_config():
    """Example: Creating and using a custom configuration."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Configuration")
    print("=" * 60)

    # Create custom configuration
    custom_config = {
        "city_name": "My Custom City",
        "description": "Custom configuration created in code",
        "selectors": {
            "permit_container": "div.permit",
            "permit_number": "span.number",
            "permit_type": "span.type",
            "address": "div.address",
            "status": "span.status",
            "issue_date": "span.date"
        },
        "scraper_settings": {
            "rate_limit": 2.0,
            "timeout": 30,
            "use_selenium": False
        }
    }

    # Save configuration
    with open('configs/custom_config.json', 'w') as f:
        json.dump(custom_config, f, indent=2)

    print("Custom configuration created and saved to configs/custom_config.json")

    # Use the custom configuration
    scraper_settings = custom_config.get('scraper_settings', {})
    with PermitScraper(custom_config, **scraper_settings) as scraper:
        url = "https://example.city.gov/permits"
        permits = scraper.scrape_permits(url, max_pages=1)

        if permits:
            PermitExporter.to_json(permits, 'output/custom_config_permits.json')
            print(f"Scraped {len(permits)} permits using custom configuration")


if __name__ == '__main__':
    print("\nScappyDoo - Example Usage Demonstrations")
    print("=" * 60)
    print("\nNOTE: These examples use placeholder URLs.")
    print("Replace 'https://example.city.gov/permits' with actual city permit URLs.")
    print("=" * 60)

    # Uncomment the examples you want to run:

    # example_basic_scraping()
    # example_with_summary()
    # example_detailed_scraping()
    # example_custom_processing()
    # example_custom_config()

    print("\n" + "=" * 60)
    print("To run these examples, uncomment the function calls above")
    print("and update the URLs with actual city permit portal URLs.")
    print("=" * 60)
