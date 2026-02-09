"""FinEdge API integration for 14 financial flags."""

import logging
import os
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class FinEdgeService:
    """Service for fetching financial data from FinEdge API and calculating 14 flags."""
    
    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None):
        """Initialize FinEdge service."""
        self.api_url = api_url or os.getenv("FINEDGE_API_URL", "https://data.finedgeapi.com/api/v1")
        self.api_token = api_token or os.getenv("FINEDGE_API_TOKEN", "")
        
        if not self.api_token:
            raise ValueError("FINEDGE_API_TOKEN is required")
        
        self.headers = {
            "X-API-KEY": self.api_token,
            "Content-Type": "application/json"
        }
        
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol exists in FinEdge stock list."""
        try:
            # Read stock list from finedge/stock_symbol_api.txt
            stock_list_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../finedge/stock_symbol_api.txt"
            )
            
            if not os.path.exists(stock_list_path):
                logger.warning(f"Stock list file not found: {stock_list_path}")
                return True  # Allow if file not found
            
            with open(stock_list_path, 'r') as f:
                import json
                stocks = json.load(f)
                
            # Check if symbol exists
            symbols = [s.get("symbol", "") for s in stocks]
            return symbol.upper() in [s.upper() for s in symbols]
            
        except Exception as e:
            logger.error(f"Error validating symbol: {e}")
            return True  # Allow if validation fails
    
    def get_financials(self, symbol: str, statement_code: str, years: int = 5) -> List[Dict]:
        """
        Fetch financial statements from FinEdge API.
        
        Args:
            symbol: Stock symbol (e.g., RELIANCE)
            statement_code: pl (P&L), bs (Balance Sheet), or cf (Cash Flow)
            years: Number of years to fetch
            
        Returns:
            List of financial data dictionaries
        """
        try:
            url = f"{self.api_url}/financials/{symbol}"
            params = {
                "statement_type": "c",  # consolidated
                "statement_code": statement_code,
                "period": "annual"
            }
            
            logger.info(f"Fetching {statement_code} for {symbol}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Return last N years
            if isinstance(data, list):
                return data[:years]
            elif isinstance(data, dict) and "data" in data:
                return data["data"][:years]
            else:
                return [data]
                
        except requests.exceptions.RequestException as e:
            logger.error(f"FinEdge API error for {symbol}/{statement_code}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching financials: {e}")
            return []
    
    def calculate_flags(self, symbol: str, fiscal_year: int) -> List[Dict]:
        """
        Calculate all 14 FinEdge-based flags.
        
        Returns list of flag dictionaries matching the format expected by flag_engine.
        """
        flags = []
        
        # Fetch all required financial data
        logger.info(f"Fetching financial data for {symbol}")
        pl_data = self.get_financials(symbol, "pl", years=5)
        bs_data = self.get_financials(symbol, "bs", years=5)
        cf_data = self.get_financials(symbol, "cf", years=5)
        
        if not pl_data or not bs_data or not cf_data:
            logger.warning(f"Incomplete financial data for {symbol}")
            # Return all flags as not triggered with low confidence
            return self._get_default_flags("Insufficient financial data from FinEdge API")
        
        # Calculate each flag
        flags.extend(self._calculate_cashflow_flags(pl_data, bs_data, cf_data, fiscal_year))
        flags.extend(self._calculate_promoter_flags(symbol, fiscal_year))
        flags.extend(self._calculate_balance_sheet_flags(pl_data, bs_data, fiscal_year))
        flags.extend(self._calculate_revenue_flags(symbol, fiscal_year))
        
        return flags
    
    def _calculate_cashflow_flags(self, pl_data: List[Dict], bs_data: List[Dict], 
                                   cf_data: List[Dict], fiscal_year: int) -> List[Dict]:
        """Calculate 8 cash flow flags (#7-14)."""
        flags = []
        
        # Helper to extract values safely
        def get_value(data_list, index, field_name, default=0):
            try:
                if index < len(data_list):
                    return float(data_list[index].get(field_name, default) or default)
                return default
            except (ValueError, TypeError):
                return default
        
        # Flag #7: PAT Growing, CFO Flat
        try:
            pat_curr = get_value(pl_data, 0, "net_profit")
            pat_prev = get_value(pl_data, 1, "net_profit")
            cfo_curr = get_value(cf_data, 0, "cash_from_operations")
            cfo_prev = get_value(cf_data, 1, "cash_from_operations")
            
            pat_growth = ((pat_curr - pat_prev) / abs(pat_prev) * 100) if pat_prev != 0 else 0
            cfo_growth = ((cfo_curr - cfo_prev) / abs(cfo_prev) * 100) if cfo_prev != 0 else 0
            
            triggered = pat_growth > 10 and abs(cfo_growth) < 5
            
            flags.append({
                "flag_id": 7,
                "flag_name": "PAT Growing, CFO Flat",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": f"PAT growth: {pat_growth:.1f}%, CFO growth: {cfo_growth:.1f}%",
                "page_references": [],
                "confidence": 85,
                "value": {"pat_growth": pat_growth, "cfo_growth": cfo_growth}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #7: {e}")
            flags.append(self._get_default_flag(7, "PAT Growing, CFO Flat", "Cash Flow", "HIGH"))
        
        # Flag #8: Receivables Growing > Revenue
        try:
            receivables_curr = get_value(bs_data, 0, "trade_receivables")
            receivables_prev = get_value(bs_data, 1, "trade_receivables")
            revenue_curr = get_value(pl_data, 0, "revenue")
            revenue_prev = get_value(pl_data, 1, "revenue")
            
            recv_growth = ((receivables_curr - receivables_prev) / abs(receivables_prev) * 100) if receivables_prev != 0 else 0
            rev_growth = ((revenue_curr - revenue_prev) / abs(revenue_prev) * 100) if revenue_prev != 0 else 0
            
            triggered = recv_growth > rev_growth and (recv_growth - rev_growth) > 10
            
            flags.append({
                "flag_id": 8,
                "flag_name": "Receivables Growing > Revenue",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": f"Receivables growth: {recv_growth:.1f}%, Revenue growth: {rev_growth:.1f}%",
                "page_references": [],
                "confidence": 85,
                "value": {"receivables_growth": recv_growth, "revenue_growth": rev_growth}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #8: {e}")
            flags.append(self._get_default_flag(8, "Receivables Growing > Revenue", "Cash Flow", "HIGH"))
        
        # Flag #9: Inventory Growing > COGS
        try:
            inventory_curr = get_value(bs_data, 0, "inventory")
            inventory_prev = get_value(bs_data, 1, "inventory")
            cogs_curr = get_value(pl_data, 0, "cost_of_goods_sold")
            cogs_prev = get_value(pl_data, 1, "cost_of_goods_sold")
            
            inv_growth = ((inventory_curr - inventory_prev) / abs(inventory_prev) * 100) if inventory_prev != 0 else 0
            cogs_growth = ((cogs_curr - cogs_prev) / abs(cogs_prev) * 100) if cogs_prev != 0 else 0
            
            triggered = inv_growth > cogs_growth and (inv_growth - cogs_growth) > 10
            
            flags.append({
                "flag_id": 9,
                "flag_name": "Inventory Growing > COGS",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": f"Inventory growth: {inv_growth:.1f}%, COGS growth: {cogs_growth:.1f}%",
                "page_references": [],
                "confidence": 85,
                "value": {"inventory_growth": inv_growth, "cogs_growth": cogs_growth}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #9: {e}")
            flags.append(self._get_default_flag(9, "Inventory Growing > COGS", "Cash Flow", "HIGH"))
        
        # Flag #10: Capex > Depreciation (>3x)
        try:
            capex = abs(get_value(cf_data, 0, "capital_expenditure"))
            depreciation = get_value(pl_data, 0, "depreciation")
            
            ratio = capex / depreciation if depreciation > 0 else 0
            triggered = ratio > 3
            
            flags.append({
                "flag_id": 10,
                "flag_name": "Capex > Depreciation (>3x)",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": f"Capex: {capex:.2f}, Depreciation: {depreciation:.2f}, Ratio: {ratio:.2f}x",
                "page_references": [],
                "confidence": 90,
                "value": {"capex": capex, "depreciation": depreciation, "ratio": ratio}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #10: {e}")
            flags.append(self._get_default_flag(10, "Capex > Depreciation (>3x)", "Cash Flow", "MEDIUM"))
        
        # Flag #11: Frequent Exceptional Items
        try:
            exceptional_count = 0
            for i in range(min(3, len(pl_data))):
                exceptional_items = get_value(pl_data, i, "exceptional_items")
                if abs(exceptional_items) > 0:
                    exceptional_count += 1
            
            triggered = exceptional_count >= 2
            
            flags.append({
                "flag_id": 11,
                "flag_name": "Frequent Exceptional Items",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": f"Exceptional items found in {exceptional_count} out of last 3 years",
                "page_references": [],
                "confidence": 80,
                "value": {"years_with_exceptional_items": exceptional_count}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #11: {e}")
            flags.append(self._get_default_flag(11, "Frequent Exceptional Items", "Cash Flow", "MEDIUM"))
        
        # Flag #12: Negative CFO
        try:
            cfo_curr = get_value(cf_data, 0, "cash_from_operations")
            triggered = cfo_curr < 0
            
            flags.append({
                "flag_id": 12,
                "flag_name": "Negative CFO",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": f"Cash from operations: {cfo_curr:.2f}",
                "page_references": [],
                "confidence": 95,
                "value": {"cash_from_operations": cfo_curr}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #12: {e}")
            flags.append(self._get_default_flag(12, "Negative CFO", "Cash Flow", "HIGH"))
        
        # Flag #13: CCC > 120 days
        try:
            receivables = get_value(bs_data, 0, "trade_receivables")
            inventory = get_value(bs_data, 0, "inventory")
            payables = get_value(bs_data, 0, "trade_payables")
            revenue = get_value(pl_data, 0, "revenue")
            cogs = get_value(pl_data, 0, "cost_of_goods_sold")
            
            # Days calculations
            dso = (receivables / revenue * 365) if revenue > 0 else 0
            dio = (inventory / cogs * 365) if cogs > 0 else 0
            dpo = (payables / cogs * 365) if cogs > 0 else 0
            
            ccc = dso + dio - dpo
            triggered = ccc > 120
            
            flags.append({
                "flag_id": 13,
                "flag_name": "CCC > 120 days",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": f"Cash Conversion Cycle: {ccc:.1f} days (DSO: {dso:.1f}, DIO: {dio:.1f}, DPO: {dpo:.1f})",
                "page_references": [],
                "confidence": 85,
                "value": {"ccc": ccc, "dso": dso, "dio": dio, "dpo": dpo}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #13: {e}")
            flags.append(self._get_default_flag(13, "CCC > 120 days", "Cash Flow", "MEDIUM"))
        
        # Flag #14: Unusual Other Income > 10%
        try:
            other_income = get_value(pl_data, 0, "other_income")
            revenue = get_value(pl_data, 0, "revenue")
            
            percentage = (other_income / revenue * 100) if revenue > 0 else 0
            triggered = percentage > 10
            
            flags.append({
                "flag_id": 14,
                "flag_name": "Unusual Other Income > 10%",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": f"Other income: {other_income:.2f}, Revenue: {revenue:.2f}, Percentage: {percentage:.1f}%",
                "page_references": [],
                "confidence": 85,
                "value": {"other_income": other_income, "revenue": revenue, "percentage": percentage}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #14: {e}")
            flags.append(self._get_default_flag(14, "Unusual Other Income > 10%", "Cash Flow", "MEDIUM"))
        
        return flags
    
    def _calculate_promoter_flags(self, symbol: str, fiscal_year: int) -> List[Dict]:
        """Calculate 3 promoter flags (#22-24)."""
        flags = []
        
        # These require shareholding pattern data from FinEdge
        # For now, return defaults as this data might need different endpoint
        
        flags.append(self._get_default_flag(22, "Promoter Pledge > 50%", "Promoter", "CRITICAL",
                                           "Shareholding pattern data not available from FinEdge API"))
        flags.append(self._get_default_flag(23, "Promoter Pledge Increasing QoQ", "Promoter", "HIGH",
                                           "Shareholding pattern data not available from FinEdge API"))
        flags.append(self._get_default_flag(24, "Promoter Selling Shares", "Promoter", "MEDIUM",
                                           "Shareholding pattern data not available from FinEdge API"))
        
        return flags
    
    def _calculate_balance_sheet_flags(self, pl_data: List[Dict], bs_data: List[Dict], 
                                        fiscal_year: int) -> List[Dict]:
        """Calculate 3 balance sheet flags (#32, #33, #38)."""
        flags = []
        
        def get_value(data_list, index, field_name, default=0):
            try:
                if index < len(data_list):
                    return float(data_list[index].get(field_name, default) or default)
                return default
            except (ValueError, TypeError):
                return default
        
        # Flag #32: Debt Growing Faster than Equity
        try:
            debt_curr = get_value(bs_data, 0, "total_debt")
            debt_prev = get_value(bs_data, 1, "total_debt")
            equity_curr = get_value(bs_data, 0, "shareholders_equity")
            equity_prev = get_value(bs_data, 1, "shareholders_equity")
            
            debt_growth = ((debt_curr - debt_prev) / abs(debt_prev) * 100) if debt_prev != 0 else 0
            equity_growth = ((equity_curr - equity_prev) / abs(equity_prev) * 100) if equity_prev != 0 else 0
            
            triggered = debt_growth > equity_growth and (debt_growth - equity_growth) > 10
            
            flags.append({
                "flag_id": 32,
                "flag_name": "Debt Growing Faster than Equity",
                "category": "Balance Sheet",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": f"Debt growth: {debt_growth:.1f}%, Equity growth: {equity_growth:.1f}%",
                "page_references": [],
                "confidence": 85,
                "value": {"debt_growth": debt_growth, "equity_growth": equity_growth}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #32: {e}")
            flags.append(self._get_default_flag(32, "Debt Growing Faster than Equity", "Balance Sheet", "HIGH"))
        
        # Flag #33: Interest Coverage < 2x
        try:
            ebit = get_value(pl_data, 0, "ebit")
            interest_expense = get_value(pl_data, 0, "interest_expense")
            
            coverage = ebit / interest_expense if interest_expense > 0 else 999
            triggered = coverage < 2
            
            flags.append({
                "flag_id": 33,
                "flag_name": "Interest Coverage < 2x",
                "category": "Balance Sheet",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": f"EBIT: {ebit:.2f}, Interest: {interest_expense:.2f}, Coverage: {coverage:.2f}x",
                "page_references": [],
                "confidence": 90,
                "value": {"ebit": ebit, "interest_expense": interest_expense, "coverage": coverage}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #33: {e}")
            flags.append(self._get_default_flag(33, "Interest Coverage < 2x", "Balance Sheet", "HIGH"))
        
        # Flag #38: Intangible Assets Growing Fast
        try:
            intangibles_curr = get_value(bs_data, 0, "intangible_assets")
            intangibles_prev = get_value(bs_data, 1, "intangible_assets")
            
            growth = ((intangibles_curr - intangibles_prev) / abs(intangibles_prev) * 100) if intangibles_prev != 0 else 0
            triggered = growth > 30
            
            flags.append({
                "flag_id": 38,
                "flag_name": "Intangible Assets Growing Fast",
                "category": "Balance Sheet",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": f"Intangible assets growth: {growth:.1f}%",
                "page_references": [],
                "confidence": 80,
                "value": {"growth_percentage": growth}
            })
        except Exception as e:
            logger.error(f"Error calculating flag #38: {e}")
            flags.append(self._get_default_flag(38, "Intangible Assets Growing Fast", "Balance Sheet", "MEDIUM"))
        
        return flags
    
    def _calculate_revenue_flags(self, symbol: str, fiscal_year: int) -> List[Dict]:
        """Calculate 1 revenue quality flag (#39)."""
        flags = []
        
        # Flag #39 requires quarterly data which may not be available
        flags.append(self._get_default_flag(39, "Revenue Concentrated in Q4 (>40%)", "Revenue Quality", "MEDIUM",
                                           "Quarterly revenue data not available from FinEdge API"))
        
        return flags
    
    def _get_default_flag(self, flag_id: int, name: str, category: str, 
                         severity: str, evidence: str = "Insufficient data") -> Dict:
        """Return a default flag with triggered=False."""
        return {
            "flag_id": flag_id,
            "flag_name": name,
            "category": category,
            "triggered": False,
            "severity": severity,
            "evidence": evidence,
            "page_references": [],
            "confidence": 0,
            "value": None
        }
    
    def _get_default_flags(self, reason: str) -> List[Dict]:
        """Return all 14 default flags when data is unavailable."""
        flag_definitions = [
            (7, "PAT Growing, CFO Flat", "Cash Flow", "HIGH"),
            (8, "Receivables Growing > Revenue", "Cash Flow", "HIGH"),
            (9, "Inventory Growing > COGS", "Cash Flow", "HIGH"),
            (10, "Capex > Depreciation (>3x)", "Cash Flow", "MEDIUM"),
            (11, "Frequent Exceptional Items", "Cash Flow", "MEDIUM"),
            (12, "Negative CFO", "Cash Flow", "HIGH"),
            (13, "CCC > 120 days", "Cash Flow", "MEDIUM"),
            (14, "Unusual Other Income > 10%", "Cash Flow", "MEDIUM"),
            (22, "Promoter Pledge > 50%", "Promoter", "CRITICAL"),
            (23, "Promoter Pledge Increasing QoQ", "Promoter", "HIGH"),
            (24, "Promoter Selling Shares", "Promoter", "MEDIUM"),
            (32, "Debt Growing Faster than Equity", "Balance Sheet", "HIGH"),
            (33, "Interest Coverage < 2x", "Balance Sheet", "HIGH"),
            (38, "Intangible Assets Growing Fast", "Balance Sheet", "MEDIUM"),
            (39, "Revenue Concentrated in Q4 (>40%)", "Revenue Quality", "MEDIUM"),
        ]
        
        return [
            self._get_default_flag(fid, name, cat, sev, reason)
            for fid, name, cat, sev in flag_definitions
        ]
