"""
Base web scraper with rate limiting and error handling.
"""
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for web scraping with rate limiting and error handling."""

    def __init__(
        self,
        rate_limit: float = 1.0,
        timeout: int = 30,
        use_selenium: bool = False,
        headless: bool = True
    ):
        """
        Initialize the scraper.

        Args:
            rate_limit: Minimum seconds between requests (default: 1.0)
            timeout: Request timeout in seconds (default: 30)
            use_selenium: Use Selenium for JavaScript-heavy sites (default: False)
            headless: Run browser in headless mode if using Selenium (default: True)
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.use_selenium = use_selenium
        self.headless = headless
        self.last_request_time = 0
        self.session = requests.Session()
        self.driver = None

        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        if self.use_selenium:
            self._setup_selenium()

    def _setup_selenium(self):
        """Set up Selenium WebDriver."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            raise

    def _respect_rate_limit(self):
        """Ensure rate limit is respected between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def fetch_page(self, url: str, retry: int = 3) -> Optional[str]:
        """
        Fetch a web page with retry logic.

        Args:
            url: URL to fetch
            retry: Number of retry attempts (default: 3)

        Returns:
            HTML content as string, or None if failed
        """
        self._respect_rate_limit()

        for attempt in range(retry):
            try:
                if self.use_selenium:
                    return self._fetch_with_selenium(url)
                else:
                    return self._fetch_with_requests(url)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{retry} failed for {url}: {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retry} attempts")
                    return None

    def _fetch_with_requests(self, url: str) -> str:
        """Fetch page using requests library."""
        logger.info(f"Fetching {url} with requests")
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _fetch_with_selenium(self, url: str) -> str:
        """Fetch page using Selenium."""
        if not self.driver:
            self._setup_selenium()

        logger.info(f"Fetching {url} with Selenium")
        self.driver.get(url)
        # Wait for body to be present
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Additional wait for JavaScript to execute
        time.sleep(2)
        return self.driver.page_source

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup.

        Args:
            html: HTML content as string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')

    def extract_links(self, soup: BeautifulSoup, base_url: str, filter_pattern: Optional[str] = None) -> list:
        """
        Extract all links from a page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            filter_pattern: Optional pattern to filter links

        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)

            if filter_pattern is None or filter_pattern in absolute_url:
                links.append(absolute_url)

        return list(set(links))  # Remove duplicates

    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
