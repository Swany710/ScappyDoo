# ScappyDoo GUI - Quick Start Guide

## Launching the Application

### Windows
1. Double-click `run_app.bat`
2. Wait for the app to start
3. Your browser will open automatically

### Linux/Mac
1. Open terminal in the ScappyDoo directory
2. Run: `./run_app.sh`
3. Your browser will open automatically

### Manual Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Using the GUI

### 1. Home Tab
- View welcome message and quick stats
- Check scraping status
- See available configurations

### 2. Scraper Tab
This is where you scrape permits!

**Step-by-step:**
1. **Select Configuration**
   - Choose from pre-built configs (Generic Table, JavaScript Heavy, etc.)
   - Or select "Custom Configuration" to build your own

2. **Enter Scraping Parameters**
   - **Target URL**: The city permit website URL
   - **Maximum Pages**: How many pages to scrape (start with 1 for testing)
   - **Scrape Detailed Information**: Check to get more data (slower)
   - **Unlimited Pages**: Check to scrape all available pages

3. **Start Scraping**
   - Click "Start Scraping" button
   - Watch the progress bar
   - See results in the Results tab

**Example:**
```
Configuration: generic_table_config
URL: https://permits.cityofexample.gov/search
Max Pages: 5
```

### 3. Configuration Tab
Build custom configurations for different city websites!

**Creating a New Configuration:**

1. **Basic Information**
   - City Name: "Example City"
   - Description: Brief description
   - Use Selenium: Check if site uses JavaScript
   - Rate Limit: How long to wait between requests (1.5s recommended)

2. **CSS Selectors** (Use browser DevTools to find these!)
   - **Permit Container**: Selector that wraps each permit
     - Example: `div.permit-item` or `table tbody tr`
   - **Permit Number**: Where the permit number is
     - Example: `span.permit-number` or `td:nth-child(1)`
   - **Permit Type**: Type of permit
   - **Address**: Property address
   - **Status**: Permit status (Approved, Pending, etc.)
   - **Issue Date**: When permit was issued
   - **Detail Link**: Link to more info (use `@href` to get URL)
     - Example: `a.details-link@href`
   - **Next Page**: Link/button to next page
     - Example: `a.next-page` or `button.pagination-next`

3. **Save**
   - Click "Save Configuration"
   - It will be available in the Scraper tab!

### 4. Results Tab
View, analyze, and export your scraped data!

**Summary Statistics:**
- Total permits scraped
- Permit type distribution (pie chart)
- Status distribution (bar chart)
- Missing data analysis

**Data Preview:**
- View all permits in a table
- Filter by permit type or status
- Sort columns

**Export Options:**
- **Download CSV**: Opens in Excel/Sheets
- **Download JSON**: For developers
- **Export to Excel**: Saves to `output/` folder
- **Download Summary**: Statistics in JSON format

## Tips & Tricks

### Finding CSS Selectors

1. Open the city permit website
2. Right-click on a permit → "Inspect" or "Inspect Element"
3. Browser DevTools opens
4. Hover over HTML elements to see them highlighted
5. Right-click element → Copy → Copy selector
6. Paste into ScappyDoo configuration

**Example HTML:**
```html
<div class="permit-card">
  <h3 class="permit-id">2024-001</h3>
  <p class="address">123 Main St</p>
  <span class="status">Approved</span>
</div>
```

**CSS Selectors:**
- Permit Container: `div.permit-card`
- Permit Number: `h3.permit-id`
- Address: `p.address`
- Status: `span.status`

### Testing Configurations

1. Always start with **Max Pages = 1**
2. Click "Start Scraping"
3. Check the Results tab
4. If data looks good, increase max pages
5. If data is wrong, adjust CSS selectors

### Common Issues

**No permits found:**
- Check if URL is correct
- Try enabling "Use Selenium" for JavaScript sites
- Verify CSS selectors in browser DevTools

**Missing data:**
- Some fields may not exist on all permits (normal)
- Check "Missing Data Analysis" in Results tab
- Adjust selectors if needed

**Rate limiting errors:**
- Increase rate limit to 2-3 seconds
- City website may be blocking requests

**Slow scraping:**
- Reduce max pages
- Don't use "Scrape Detailed Information" unless needed
- Check your internet connection

## Example Workflow

### Scraping Example City Permits

1. **Launch App**
   ```bash
   ./run_app.sh
   ```

2. **Go to Scraper Tab**

3. **Select Configuration**
   - Choose "generic_table_config"

4. **Enter URL**
   - URL: `https://permits.examplecity.gov/search`
   - Max Pages: 1 (testing)

5. **Start Scraping**
   - Click "Start Scraping"
   - Wait for completion

6. **Check Results**
   - Go to Results tab
   - Review data in table
   - Check summary statistics

7. **Export Data**
   - Click "Download CSV"
   - Open in Excel

8. **Scale Up** (if results look good)
   - Go back to Scraper tab
   - Increase Max Pages to 10
   - Run again

## Advanced Features

### Building Complex Selectors

**Table-based:**
```
Permit Container: table#permits tbody tr
Permit Number: td:nth-child(1)
Type: td:nth-child(2)
Address: td:nth-child(3)
```

**Card-based:**
```
Permit Container: div.permit-card
Permit Number: h3.card-title
Type: span.badge-primary
Address: p.card-text:nth-child(2)
```

**Getting Attributes:**
```
Detail Link: a.view-details@href
Image: img.permit-photo@src
Date: time@datetime
```

### Pagination Selectors

**Link-based:**
```
Next Page: a[rel='next']
Next Page: a.pagination-next
```

**Button-based:**
```
Next Page: button.next-page
Next Page: button[aria-label='Next']
```

**Page numbers:**
```
Next Page: a.page-link:last-child
```

## Need More Help?

1. Check the main README.md for detailed documentation
2. Look at example configurations in `configs/` folder
3. Test with `max_pages=1` before large scrapes
4. Use browser DevTools to inspect HTML structure

## Keyboard Shortcuts

- `Ctrl+C` in terminal: Stop the app
- `R` in browser: Rerun Streamlit app
- `F5` in browser: Refresh page
