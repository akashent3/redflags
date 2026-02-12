"""FinEdge API client for fetching Indian stock market financial data."""

import httpx
import logging
import os
from typing import Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://data.finedgeapi.com/api/v1"


class FinEdgeClient:
    def __init__(self, token: str = None):
        self.token = token or settings.finedge_api_token
        if not self.token:
            raise ValueError("FinEdge API token required. Set FINEDGE_API_TOKEN env var.")
        self.client = httpx.Client(timeout=30.0)
        self._symbols_cache = None

    def _get(self, endpoint: str, params: dict = None) -> dict:
        params = params or {}
        params["token"] = self.token
        url = f"{BASE_URL}/{endpoint}"
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _get_all_symbols(self) -> List[Dict]:
        if self._symbols_cache is None:
            self._symbols_cache = self._get("stock-symbols")
        return self._symbols_cache

    def search_symbol(self, company_name: str) -> Optional[Dict]:
        """Search for a stock symbol by company name or symbol code."""
        symbols = self._get_all_symbols()
        query = company_name.lower().strip()

        # Exact name match
        for s in symbols:
            if s["name"].lower() == query:
                return s

        # Exact symbol/code match
        for s in symbols:
            if s.get("symbol", "").lower() == query or \
               s.get("nse_code", "").lower() == query or \
               s.get("bse_code", "").lower() == query:
                return s

        # Partial name match - find best (shortest matching name)
        matches = [s for s in symbols if query in s["name"].lower()]
        if matches:
            return min(matches, key=lambda x: len(x["name"]))

        # Partial symbol match
        matches = [s for s in symbols if query in s.get("symbol", "").lower()]
        if matches:
            return matches[0]

        return None

    def get_all_symbols(self) -> List[Dict]:
        """Get all stock symbols for search functionality."""
        return self._get_all_symbols()

    def get_company_profile(self, symbol: str) -> Dict:
        return self._get(f"company-profile/{symbol}")

    def get_financials(self, symbol: str, statement_code: str,
                       statement_type: str = "c", period: str = "annual") -> Dict:
        """Fetch financial statements.
        statement_code: pl (P&L), bs (Balance Sheet), cf (Cash Flow)
        statement_type: c (consolidated), s (standalone)
        period: annual, quarterly
        """
        return self._get(f"financials/{symbol}", {
            "statement_type": statement_type,
            "statement_code": statement_code,
            "period": period
        })

    def get_shareholding_pattern(self, symbol: str, period: str = "quarterly") -> Dict:
        return self._get(f"shareholdings/pattern/{symbol}", {"period": period})

    def get_shareholding_declaration(self, symbol: str, period: str = "quarterly") -> Dict:
        return self._get(f"shareholdings/declaration/{symbol}", {"period": period})

    def fetch_all_data(self, symbol: str, consolidated: bool = True) -> Dict:
        """Fetch all financial data needed for flag calculations.
        Tries consolidated first; falls back to standalone if empty.
        """
        st = "c" if consolidated else "s"
        data = {"symbol": symbol, "statement_type": "consolidated" if consolidated else "standalone"}

        # Company profile
        try:
            data["profile"] = self.get_company_profile(symbol)
        except Exception as e:
            logger.warning(f"Failed to fetch profile: {e}")
            data["profile"] = {}

        # Annual P&L
        try:
            pl = self.get_financials(symbol, "pl", st, "annual")
            data["pl_annual"] = pl.get("financials", [])
        except Exception as e:
            logger.warning(f"Failed to fetch annual P&L: {e}")
            data["pl_annual"] = []

        # Annual Balance Sheet
        try:
            bs = self.get_financials(symbol, "bs", st, "annual")
            data["bs_annual"] = bs.get("financials", [])
        except Exception as e:
            logger.warning(f"Failed to fetch annual BS: {e}")
            data["bs_annual"] = []

        # Annual Cash Flow
        try:
            cf = self.get_financials(symbol, "cf", st, "annual")
            data["cf_annual"] = cf.get("financials", [])
        except Exception as e:
            logger.warning(f"Failed to fetch annual CF: {e}")
            data["cf_annual"] = []

        # Quarterly P&L (for Q4 concentration check)
        try:
            pl_q = self.get_financials(symbol, "pl", st, "quarterly")
            data["pl_quarterly"] = pl_q.get("financials", [])
        except Exception as e:
            logger.warning(f"Failed to fetch quarterly P&L: {e}")
            data["pl_quarterly"] = []

        # Shareholding pattern
        try:
            data["shareholding_pattern"] = self.get_shareholding_pattern(symbol)
        except Exception as e:
            logger.warning(f"Failed to fetch shareholding pattern: {e}")
            data["shareholding_pattern"] = {}

        # Shareholding declaration (pledge data)
        try:
            data["shareholding_declaration"] = self.get_shareholding_declaration(symbol)
        except Exception as e:
            logger.warning(f"Failed to fetch shareholding declaration: {e}")
            data["shareholding_declaration"] = {}

        # If consolidated data is empty, fall back to standalone
        if not data["pl_annual"] and consolidated:
            logger.info("No consolidated data found, trying standalone...")
            return self.fetch_all_data(symbol, consolidated=False)

        return data


# Singleton instance
finedge_client = FinEdgeClient()
