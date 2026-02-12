"""NSE India API client for fetching annual reports."""

import requests  # Changed from httpx
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

    def _init_session(self):
            return True

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Make request to NSE API with retry logic - direct call without session init."""
        for attempt in range(max_retries):
            try:
                # Direct headers for each request (no cookies needed)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements',
                    'Origin': 'https://www.nseindia.com',
                    'Connection': 'keep-alive',
                }

                logger.info(f"Making direct NSE API request (attempt {attempt + 1}/{max_retries})")
                
                response = requests.get(url, headers=headers, timeout=30)

                # Debug logging
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Content-Type: {response.headers.get('content-type')}")
                logger.info(f"Content-Length: {len(response.content)}")

                if response.status_code == 200:
                    # Check if response is empty
                    if not response.text or len(response.text.strip()) == 0:
                        logger.error("NSE returned empty response")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        return None
                    
                    # Check if response is HTML (error page)
                    if response.text.strip().startswith('<'):
                        logger.error("NSE returned HTML instead of JSON")
                        logger.error(f"HTML preview: {response.text[:200]}")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        return None
                    
                    # Parse JSON
                    data = response.json()
                    logger.info(f"Successfully parsed JSON response")
                    return data
                    
                else:
                    logger.error(f"NSE API returned status {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue

            except requests.exceptions.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Response preview: {response.text[:200] if 'response' in locals() else 'No response'}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
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

            # Sort by toYr to get latest
            sorted_reports = sorted(
                reports,
                key=lambda r: int(r.get("toYr", 0)) if str(r.get("toYr", "")).isdigit() else 0,
                reverse=True
            )

            latest = sorted_reports[0]

            # Get PDF URL from fileName field (NSE format)
            pdf_url = latest.get("fileName")

            if pdf_url:
                logger.info(f"Latest annual report URL for {symbol}: {pdf_url}")
                logger.info(f"Year: {latest.get('fromYr')}-{latest.get('toYr')}")
                return pdf_url
            else:
                logger.warning(f"No fileName found in latest report for {symbol}: {latest}")
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

            # Direct request with headers (no cookies needed)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.nseindia.com/',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers, timeout=60)

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

            # Sort by toYr to get latest
            sorted_reports = sorted(
                reports,
                key=lambda r: int(r.get("toYr", 0)) if str(r.get("toYr", "")).isdigit() else 0,
                reverse=True
            )

            latest = sorted_reports[0]

            # Get PDF URL from fileName field
            pdf_url = latest.get("fileName")

            if not pdf_url:
                logger.warning(f"No fileName in report: {latest}")
                return None

            return {
                "year": f"{latest.get('fromYr', 'Unknown')}-{latest.get('toYr', 'Unknown')}",
                "pdf_url": pdf_url,
                "company_name": latest.get("companyName"),
                "raw_data": latest,
            }

        except Exception as e:
            logger.error(f"Failed to get latest annual report for {symbol}: {e}", exc_info=True)
            return None


# Singleton instance
nse_client = NSEClient()