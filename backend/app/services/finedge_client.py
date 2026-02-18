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

    # ========== Live Quote via /quote endpoint ==========
    def get_live_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote for a symbol.

        Calls: GET /api/v1/quote?symbol=SYMBOL&token=...

        Actual API response structure:
            {
                "ITC": {
                    "current_price": 318.1,
                    "change": "1.39%",      # percent string e.g. "1.39%" or "-1.20%"
                    "high52": 444.2,        # 52-week high
                    "low52": 302,           # 52-week low
                    "high_price": 318.25,   # day high
                    "low_price": 313.15,    # day low
                    "open_price": 313.75,
                    "market_cap": 398546.22,
                    "shares": 12245059584,
                    "tradetime": "2026-02-16T15:30:03Z",
                    "volume": 11693055
                }
            }

        Returns normalised dict or None on failure.
        """
        try:
            resp = self._get("quote", {"symbol": symbol})
            # Response is keyed by symbol name (e.g. {"ITC": {...}})
            data = resp.get(symbol) or (list(resp.values())[0] if resp else None)
            if not data:
                return None

            # Parse change percent string "1.39%" → 1.39  (handles negatives too)
            raw_change = data.get("change", "0%")
            try:
                change_percent = float(str(raw_change).replace("%", "").strip())
            except (ValueError, TypeError):
                change_percent = None

            return {
                "current_price": data.get("current_price"),   # field is "current_price" (not "price")
                "change_percent": change_percent,
                "high52": data.get("high52"),                  # 52-week high
                "low52": data.get("low52"),                    # 52-week low
                "volume": data.get("volume"),
                "market_cap": data.get("market_cap"),
                "trade_time": data.get("tradetime"),
            }
        except Exception as e:
            logger.warning(f"Failed to fetch quote for {symbol}: {e}")
            return None
    # ====================================================

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

    # ========== NEW METHODS for consolidated_ind detection ==========

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get symbol info including consolidated_ind flag.
        
        Returns:
            {
                "symbol": "RELIANCE",
                "name": "Reliance Industries Limited",
                "consolidated_ind": true,  ← Tells us if consolidated data exists
                "exchange": "NSE",
                ...
            }
        """
        symbols = self._get_all_symbols()
        
        # Match by symbol/code (case-insensitive)
        for s in symbols:
            if s.get("symbol", "").upper() == symbol.upper() or \
               s.get("nse_code", "").upper() == symbol.upper() or \
               s.get("bse_code", "").upper() == symbol.upper():
                return s
        
        return None

    def has_consolidated_financials(self, symbol: str) -> bool:
        """
        Check if company has consolidated financials available.
        Uses the consolidated_ind field from stock-symbols API.
        
        Args:
            symbol: NSE/BSE symbol
            
        Returns:
            True if consolidated available, False if standalone only
        """
        symbol_info = self.get_symbol_info(symbol)
        
        if not symbol_info:
            logger.warning(f"Symbol {symbol} not found in FinEdge database")
            return False  # Default to standalone if unknown
        
        # Check consolidated_ind field
        has_consolidated = symbol_info.get("consolidated_ind", False)
        
        logger.info(
            f"{symbol}: consolidated_ind={has_consolidated} "
            f"({'CONSOLIDATED data available' if has_consolidated else 'STANDALONE only'})"
        )
        
        return has_consolidated

    # ========== UPDATED fetch_all_data method ==========

    def fetch_all_data(self, symbol: str, consolidated: bool = None, is_financial_sector: bool = False) -> Dict:
        """
        Fetch all financial data needed for flag calculations.

        Args:
            symbol: NSE/BSE symbol
            consolidated: If None (default), auto-detect using consolidated_ind field.
                         If True/False, force that statement type.
            is_financial_sector: If True (bank/NBFC), always use STANDALONE regardless
                                 of consolidated_ind. Banks report key metrics (NPA ratios,
                                 capital adequacy) only in standalone statements.

        Returns:
            Dict with all financial data and statement type used
        """
        # Banks/NBFCs always use standalone — regulatory metrics (NPA, CRAR) are
        # reported on a standalone basis per RBI guidelines.
        if is_financial_sector:
            consolidated = False
            logger.info(f"{symbol}: BANK/NBFC — forcing STANDALONE (regulatory requirement)")
        # Step 1: Auto-detect if consolidated not explicitly specified
        elif consolidated is None:
            consolidated = self.has_consolidated_financials(symbol)
            logger.info(
                f"Auto-detected statement type for {symbol}: "
                f"{'CONSOLIDATED' if consolidated else 'STANDALONE'}"
            )
        
        st = "c" if consolidated else "s"
        data = {
            "symbol": symbol, 
            "statement_type": "consolidated" if consolidated else "standalone",
            "consolidated_ind": consolidated  # Store what we used
        }

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

        # Log summary
        logger.info(
            f"Fetched {st.upper()} data for {symbol}: "
            f"P&L={len(data.get('pl_annual', []))} years, "
            f"BS={len(data.get('bs_annual', []))} years, "
            f"CF={len(data.get('cf_annual', []))} years"
        )

        return data


# Global instance
finedge_client = FinEdgeClient()