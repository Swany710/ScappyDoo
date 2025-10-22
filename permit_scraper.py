"""
City permit scraper with configurable selectors.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from scraper import BaseScraper

logger = logging.getLogger(__name__)


class PermitScraper(BaseScraper):
    """Scraper for extracting permit information from city websites."""

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize permit scraper with configuration.

        Args:
            config: Configuration dictionary with selectors and settings
            **kwargs: Additional arguments passed to BaseScraper
        """
        super().__init__(**kwargs)
        self.config = config
        self.permits = []

    def scrape_permits(self, start_url: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape permits from the configured website.

        Args:
            start_url: Starting URL for scraping
            max_pages: Maximum number of pages to scrape (None for unlimited)

        Returns:
            List of permit dictionaries
        """
        logger.info(f"Starting permit scraping from {start_url}")
        self.permits = []

        pages_scraped = 0
        current_url = start_url

        while current_url:
            if max_pages and pages_scraped >= max_pages:
                logger.info(f"Reached maximum pages limit: {max_pages}")
                break

            html = self.fetch_page(current_url)
            if not html:
                logger.error(f"Failed to fetch page: {current_url}")
                break

            soup = self.parse_html(html)

            # Extract permits from current page
            page_permits = self._extract_permits_from_page(soup, current_url)
            self.permits.extend(page_permits)
            logger.info(f"Extracted {len(page_permits)} permits from page {pages_scraped + 1}")

            # Find next page
            current_url = self._find_next_page(soup, current_url)
            pages_scraped += 1

        logger.info(f"Total permits scraped: {len(self.permits)}")
        return self.permits

    def _extract_permits_from_page(self, soup, page_url: str) -> List[Dict[str, Any]]:
        """
        Extract permit information from a single page.

        Args:
            soup: BeautifulSoup object
            page_url: URL of the current page

        Returns:
            List of permit dictionaries
        """
        permits = []
        selectors = self.config.get('selectors', {})

        # Find permit containers
        container_selector = selectors.get('permit_container')
        if not container_selector:
            logger.error("No permit_container selector configured")
            return permits

        containers = soup.select(container_selector)
        logger.debug(f"Found {len(containers)} permit containers")

        for container in containers:
            permit = self._extract_permit_details(container, selectors)
            if permit:
                permit['source_url'] = page_url
                permit['scraped_at'] = datetime.now().isoformat()
                permits.append(permit)

        return permits

    def _extract_permit_details(self, container, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Extract details from a single permit container.

        Args:
            container: BeautifulSoup element containing permit data
            selectors: Dictionary of CSS selectors for permit fields

        Returns:
            Dictionary of permit details, or None if extraction fails
        """
        permit = {}

        # Define field mappings
        field_mappings = {
            'permit_number': 'permit_number',
            'permit_type': 'permit_type',
            'address': 'address',
            'status': 'status',
            'issue_date': 'issue_date',
            'description': 'description',
            'applicant': 'applicant',
            'contractor': 'contractor',
            'value': 'value',
            'expiration_date': 'expiration_date'
        }

        for field_name, selector_key in field_mappings.items():
            selector = selectors.get(selector_key)
            if selector:
                value = self._extract_field(container, selector)
                if value:
                    permit[field_name] = value.strip()

        # Extract detail link if configured
        detail_link_selector = selectors.get('detail_link')
        if detail_link_selector:
            detail_link = container.select_one(detail_link_selector)
            if detail_link and detail_link.get('href'):
                permit['detail_url'] = detail_link['href']

        # Only return permit if we extracted at least some data
        return permit if permit else None

    def _extract_field(self, container, selector: str) -> Optional[str]:
        """
        Extract a single field value using a CSS selector.

        Args:
            container: BeautifulSoup element to search within
            selector: CSS selector string

        Returns:
            Extracted text or None
        """
        try:
            # Handle attribute extraction (e.g., "a@href" to get href attribute)
            if '@' in selector:
                element_selector, attribute = selector.split('@', 1)
                element = container.select_one(element_selector)
                if element:
                    return element.get(attribute)
            else:
                element = container.select_one(selector)
                if element:
                    return element.get_text()
        except Exception as e:
            logger.debug(f"Failed to extract field with selector '{selector}': {e}")

        return None

    def _find_next_page(self, soup, current_url: str) -> Optional[str]:
        """
        Find the URL of the next page.

        Args:
            soup: BeautifulSoup object
            current_url: Current page URL

        Returns:
            Next page URL or None if no next page
        """
        next_page_selector = self.config.get('selectors', {}).get('next_page')
        if not next_page_selector:
            return None

        try:
            next_link = soup.select_one(next_page_selector)
            if next_link and next_link.get('href'):
                from urllib.parse import urljoin
                return urljoin(current_url, next_link['href'])
        except Exception as e:
            logger.debug(f"Error finding next page: {e}")

        return None

    def scrape_permit_details(self, permit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape detailed information for a specific permit.

        Args:
            permit: Permit dictionary with at least a 'detail_url' field

        Returns:
            Updated permit dictionary with additional details
        """
        detail_url = permit.get('detail_url')
        if not detail_url:
            logger.warning("No detail URL provided for permit")
            return permit

        html = self.fetch_page(detail_url)
        if not html:
            logger.error(f"Failed to fetch permit details from {detail_url}")
            return permit

        soup = self.parse_html(html)
        detail_selectors = self.config.get('detail_selectors', {})

        # Extract additional fields from detail page
        for field_name, selector in detail_selectors.items():
            if field_name not in permit:  # Don't overwrite existing fields
                value = self._extract_field(soup, selector)
                if value:
                    permit[field_name] = value.strip()

        return permit

    def get_permits(self) -> List[Dict[str, Any]]:
        """Get the list of scraped permits."""
        return self.permits
