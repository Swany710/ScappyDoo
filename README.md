# ScappyDoo

A flexible and configurable web scraper for extracting permit information from city and municipal websites.

## Features

- **Configurable CSS Selectors**: Easily adapt to different city website structures
- **Multiple Export Formats**: Export data to JSON, CSV, or Excel
- **Rate Limiting**: Respectful scraping with configurable request delays
- **Error Handling**: Robust retry logic and error recovery
- **JavaScript Support**: Optional Selenium integration for dynamic websites
- **Pagination**: Automatic handling of multi-page permit listings
- **Detail Scraping**: Extract additional information from individual permit pages
- **Summary Statistics**: Generate insights about scraped permit data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ScappyDoo.git
cd ScappyDoo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. **Create a configuration file** for your target city website (see Configuration section below)

2. **Run the scraper**:
```bash
python main.py --config configs/example_config.json \
               --url "https://city.gov/permits" \
               --output permits.csv
```

## Usage

### Basic Command

```bash
python main.py -c <config_file> -u <url> -o <output_file>
```

### Command-Line Options

- `-c, --config`: Path to configuration JSON file (required)
- `-u, --url`: Starting URL to scrape permits from (required)
- `-o, --output`: Output file path - supports .json, .csv, or .xlsx (required)
- `--max-pages`: Maximum number of pages to scrape (optional)
- `--scrape-details`: Scrape detailed information for each permit (optional, slower)
- `--summary`: Path to save summary statistics in JSON format (optional)
- `--debug`: Enable debug logging (optional)

### Examples

**Scrape permits and save to CSV:**
```bash
python main.py -c configs/generic_table_config.json \
               -u "https://permits.cityofexample.gov/search" \
               -o output/permits.csv
```

**Limit to 10 pages and export to JSON:**
```bash
python main.py -c configs/example_config.json \
               -u "https://city.gov/permits" \
               -o permits.json \
               --max-pages 10
```

**Scrape with detailed information and generate summary:**
```bash
python main.py -c configs/example_config.json \
               -u "https://city.gov/permits" \
               -o permits.xlsx \
               --scrape-details \
               --summary summary.json
```

**Enable debug mode:**
```bash
python main.py -c configs/example_config.json \
               -u "https://city.gov/permits" \
               -o permits.csv \
               --debug
```

## Configuration

Configuration files define how to extract permit data from a specific city website. They use JSON format with CSS selectors.

### Configuration Structure

```json
{
  "city_name": "Example City",
  "description": "Configuration for Example City permit portal",
  "selectors": {
    "permit_container": "CSS selector for each permit item",
    "permit_number": "CSS selector for permit number",
    "permit_type": "CSS selector for permit type",
    "address": "CSS selector for address",
    "status": "CSS selector for status",
    "issue_date": "CSS selector for issue date",
    "description": "CSS selector for description",
    "applicant": "CSS selector for applicant name",
    "contractor": "CSS selector for contractor name",
    "value": "CSS selector for permit value",
    "expiration_date": "CSS selector for expiration date",
    "detail_link": "CSS selector for detail page link",
    "next_page": "CSS selector for next page button/link"
  },
  "detail_selectors": {
    "additional_field": "CSS selector for additional fields on detail pages"
  },
  "scraper_settings": {
    "rate_limit": 1.5,
    "timeout": 30,
    "use_selenium": false,
    "headless": true
  }
}
```

### Selector Syntax

- **Standard selectors**: `"field_name": "div.class-name"` - extracts text content
- **Attribute selectors**: `"field_name": "a.link@href"` - extracts href attribute (use `@attribute_name`)
- **CSS selector syntax**: Supports all standard CSS selectors (classes, IDs, nth-child, etc.)

### Example Configurations

Three example configurations are provided in the `configs/` directory:

1. **example_config.json**: Template with common permit fields
2. **generic_table_config.json**: For table-based permit listings
3. **javascript_heavy_config.json**: For sites requiring JavaScript rendering

### Creating a Custom Configuration

1. **Inspect the target website** using browser developer tools
2. **Identify CSS selectors** for each permit field
3. **Copy an example config** and modify the selectors
4. **Test with limited pages** using `--max-pages 1`
5. **Refine selectors** based on results

## Project Structure

```
ScappyDoo/
├── scraper.py              # Base scraper with rate limiting and error handling
├── permit_scraper.py       # Permit-specific scraping logic
├── exporters.py            # Data export utilities (JSON, CSV, Excel)
├── main.py                 # Command-line interface
├── configs/                # Configuration files
│   ├── example_config.json
│   ├── generic_table_config.json
│   └── javascript_heavy_config.json
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Advanced Usage

### Using as a Library

```python
from permit_scraper import PermitScraper
from exporters import PermitExporter
import json

# Load configuration
with open('configs/example_config.json', 'r') as f:
    config = json.load(f)

# Initialize scraper
scraper_settings = config.get('scraper_settings', {})
scraper = PermitScraper(config, **scraper_settings)

# Scrape permits
permits = scraper.scrape_permits(
    start_url="https://city.gov/permits",
    max_pages=10
)

# Export to CSV
PermitExporter.to_csv(permits, 'output.csv')

# Generate summary
summary = PermitExporter.generate_summary(permits)
print(f"Total permits: {summary['total_permits']}")

# Clean up
scraper.close()
```

### Custom Data Processing

```python
from permit_scraper import PermitScraper
from exporters import PermitExporter

# ... initialize scraper ...

# Scrape permits
permits = scraper.scrape_permits(url)

# Convert to DataFrame for analysis
df = PermitExporter.to_dataframe(permits)

# Filter and analyze
residential_permits = df[df['permit_type'] == 'Residential']
print(f"Residential permits: {len(residential_permits)}")

# Export filtered results
PermitExporter.to_csv(residential_permits.to_dict('records'), 'residential.csv')
```

## Best Practices

1. **Respect robots.txt**: Check the website's robots.txt file before scraping
2. **Use appropriate rate limiting**: Set `rate_limit` to avoid overwhelming servers
3. **Test incrementally**: Start with `--max-pages 1` to test your configuration
4. **Handle errors gracefully**: Review logs for failed requests
5. **Cache results**: Save intermediate results to avoid re-scraping
6. **Legal compliance**: Ensure you have the right to scrape and use the data

## Troubleshooting

### Common Issues

**No permits extracted:**
- Check if selectors match the actual HTML structure
- Enable debug mode (`--debug`) to see detailed logs
- Try using Selenium (`"use_selenium": true`) for JavaScript-heavy sites

**Rate limiting errors:**
- Increase `rate_limit` in configuration
- Reduce concurrent requests

**Timeout errors:**
- Increase `timeout` in configuration
- Check internet connection
- Website may be slow or down

**Missing data fields:**
- Verify CSS selectors in browser developer tools
- Some fields may not be present on all permits
- Check the summary for missing data statistics

## Dependencies

- requests: HTTP requests
- beautifulsoup4: HTML parsing
- lxml: Fast XML/HTML parser
- pandas: Data manipulation and export
- selenium: JavaScript rendering
- webdriver-manager: Automatic WebDriver management
- openpyxl: Excel file support

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational and research purposes. Always ensure you have permission to scrape websites and comply with their terms of service and robots.txt files. The developers are not responsible for misuse of this tool.