"""NSE India API client for fetching annual reports."""

import httpx
import logging
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

NSE_BASE_URL = "https://www.nseindia.com"
NSE_API_BASE = "https://www.nseindia.com/api"


class NSEClient:
    """Client for NSE India API."""

    def __init__(self):
        self.session = None
        self.cookies = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/",
        }

    def _init_session(self):
        """Initialize session with cookies by visiting NSE homepage."""
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                # Visit homepage to get cookies
                response = client.get(NSE_BASE_URL, headers=self.headers)
                self.cookies = dict(response.cookies)
                logger.info("NSE session initialized successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {e}")
            return False

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Make request to NSE API with retry logic."""
        for attempt in range(max_retries):
            try:
                # Initialize session if not done
                if not self.cookies:
                    if not self._init_session():
                        raise Exception("Failed to initialize NSE session")
                    time.sleep(1)  # Wait after session init

                with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                    response = client.get(url, headers=self.headers, cookies=self.cookies)

                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 401 or response.status_code == 403:
                        # Session expired, re-initialize
                        logger.warning(f"NSE session expired (status {response.status_code}), re-initializing...")
                        self.cookies = {}
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                    else:
                        logger.error(f"NSE API returned status {response.status_code}: {response.text[:200]}")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue

            except Exception as e:
                logger.error(f"NSE API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise

        return None

    def get_annual_reports(self, symbol: str) -> List[Dict]:
        """
        Fetch annual reports for a company from NSE.

        Args:
            symbol: NSE symbol (e.g., "RELIANCE", "TCS")

        Returns:
            List of annual report entries with download URLs
        """
        try:
            url = f"{NSE_API_BASE}/annual-reports?index=equities&symbol={symbol}"
            logger.info(f"Fetching annual reports for {symbol} from NSE")

            data = self._make_request(url)

            if not data:
                logger.warning(f"No data returned for symbol {symbol}")
                return []

            # NSE API returns array or dict with reports key
            if isinstance(data, list):
                reports = data
            elif isinstance(data, dict):
                reports = data.get("data", data.get("reports", []))
            else:
                logger.warning(f"Unexpected response format from NSE API: {type(data)}")
                return []

            logger.info(f"Found {len(reports)} annual reports for {symbol}")
            return reports

        except Exception as e:
            logger.error(f"Failed to fetch annual reports for {symbol}: {e}", exc_info=True)
            return []

    def get_latest_annual_report_url(self, symbol: str) -> Optional[str]:
        """
        Get the download URL for the latest annual report.

        Args:
            symbol: NSE symbol

        Returns:
            PDF download URL or None
        """
        try:
            reports = self.get_annual_reports(symbol)

            if not reports:
                logger.warning(f"No annual reports found for {symbol}")
                return None

            # Sort by year/date to get latest
            # NSE reports usually have 'year' or 'reportDate' field
            sorted_reports = sorted(
                reports,
                key=lambda r: (
                    r.get("year", 0),
                    r.get("reportDate", ""),
                    r.get("report_date", ""),
                ),
                reverse=True
            )

            latest = sorted_reports[0]

            # Get PDF URL - field names may vary
            pdf_url = latest.get("pdfUrl") or latest.get("pdf_url") or latest.get("url") or latest.get("link")

            if pdf_url:
                # If relative URL, make it absolute
                if not pdf_url.startswith("http"):
                    pdf_url = f"{NSE_BASE_URL}{pdf_url}"

                logger.info(f"Latest annual report URL for {symbol}: {pdf_url}")
                return pdf_url
            else:
                logger.warning(f"No PDF URL found in latest report for {symbol}: {latest}")
                return None

        except Exception as e:
            logger.error(f"Failed to get latest annual report URL for {symbol}: {e}", exc_info=True)
            return None

    def download_pdf(self, url: str) -> Optional[bytes]:
        """
        Download PDF from NSE.

        Args:
            url: PDF URL

        Returns:
            PDF bytes or None
        """
        try:
            logger.info(f"Downloading PDF from {url}")

            # Initialize session if needed
            if not self.cookies:
                self._init_session()
                time.sleep(1)

            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(url, headers=self.headers, cookies=self.cookies)

                if response.status_code == 200:
                    logger.info(f"Downloaded PDF successfully ({len(response.content)} bytes)")
                    return response.content
                else:
                    logger.error(f"Failed to download PDF: status {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {e}", exc_info=True)
            return None

    def get_latest_annual_report(self, symbol: str) -> Optional[Dict]:
        """
        Get the latest annual report info and download URL.

        Args:
            symbol: NSE symbol

        Returns:
            Dict with report info including download URL, year, etc.
        """
        try:
            reports = self.get_annual_reports(symbol)

            if not reports:
                return None

            # Sort by year to get latest
            sorted_reports = sorted(
                reports,
                key=lambda r: (
                    r.get("year", 0),
                    r.get("reportDate", ""),
                    r.get("report_date", ""),
                ),
                reverse=True
            )

            latest = sorted_reports[0]

            # Get PDF URL
            pdf_url = latest.get("pdfUrl") or latest.get("pdf_url") or latest.get("url") or latest.get("link")

            if pdf_url and not pdf_url.startswith("http"):
                pdf_url = f"{NSE_BASE_URL}{pdf_url}"

            return {
                "year": latest.get("year", latest.get("reportDate", "Unknown")),
                "pdf_url": pdf_url,
                "raw_data": latest,
            }

        except Exception as e:
            logger.error(f"Failed to get latest annual report for {symbol}: {e}", exc_info=True)
            return None


# Singleton instance
nse_client = NSEClient()
