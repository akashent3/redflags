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
                
            # Check if symbol exists and get consolidated indicator
            for stock in stocks:
                if stock.get("symbol", "").upper() == symbol.upper():
                    return stock.get("consolidated_ind", True)
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating symbol: {e}")
            return True  # Allow if validation fails
    
    def check_consolidated(self, symbol: str) -> bool:
        """Check if company has consolidated statements."""
        try:
            stock_list_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../finedge/stock_symbol_api.txt"
            )
            
            if os.path.exists(stock_list_path):
                with open(stock_list_path, 'r') as f:
                    import json
                    stocks = json.load(f)
                    
                for stock in stocks:
                    if stock.get("symbol", "").upper() == symbol.upper():
                        return stock.get("consolidated_ind", False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking consolidated status: {e}")
            return False
    
    def get_financials(self, symbol: str, statement_code: str, years: int = 5, period: str = "annual") -> List[Dict]:
        """
        Fetch financial statements from FinEdge API.
        
        Args:
            symbol: Stock symbol (e.g., RELIANCE)
            statement_code: pl (P&L), bs (Balance Sheet), or cf (Cash Flow)
            years: Number of years to fetch
            period: annual or quarter
            
        Returns:
            List of financial data dictionaries
        """
        try:
            # Check if consolidated data available
            is_consolidated = self.check_consolidated(symbol)
            statement_type = "c" if is_consolidated else "s"
            
            url = f"{self.api_url}/financials/{symbol}"
            params = {
                "statement_type": statement_type,
                "statement_code": statement_code,
                "period": period,
                "token": self.api_token
            }
            
            logger.info(f"Fetching {statement_code} ({statement_type}) for {symbol}, period: {period}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Return last N years - handle both response formats
            if isinstance(data, dict) and "financials" in data:
                financials = data["financials"][:years * 4 if period == "quarter" else years]
                logger.info(f"Retrieved {len(financials)} {period} records for {symbol}")
                return financials
            elif isinstance(data, list):
                financials = data[:years * 4 if period == "quarter" else years]
                logger.info(f"Retrieved {len(financials)} {period} records for {symbol}")
                return financials
            else:
                logger.warning(f"Unexpected response format for {symbol}/{statement_code}")
                return []
                
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
        pl_quarterly = self.get_financials(symbol, "pl", years=2, period="quarter")
        
        if not pl_data or not bs_data or not cf_data:
            logger.warning(f"Incomplete financial data for {symbol}")
            return self._get_default_flags("Insufficient financial data from FinEdge API")
        
        # Calculate each flag
        flags.extend(self._calculate_cashflow_flags(pl_data, bs_data, cf_data, fiscal_year))
        flags.extend(self._calculate_promoter_flags(symbol, fiscal_year))
        flags.extend(self._calculate_balance_sheet_flags(pl_data, bs_data, fiscal_year))
        flags.extend(self._calculate_revenue_flags(pl_data, pl_quarterly, fiscal_year))
        
        return flags
    
    def _calculate_cashflow_flags(self, pl_data: List[Dict], bs_data: List[Dict], 
                                   cf_data: List[Dict], fiscal_year: int) -> List[Dict]:
        """Calculate 8 cash flow flags (#7-14)."""
        flags = []
        
        # Helper to extract values safely
        def get_value(data_list, index, field_name, default=0):
            try:
                if index < len(data_list):
                    value = data_list[index].get(field_name, default)
                    return float(value) if value is not None else default
                return default
            except (ValueError, TypeError):
                return default
        
        # Flag #7: PAT Growing, CFO Flat
        try:
            pat_curr = get_value(pl_data, 0, "profitLossForPeriod")
            pat_prev = get_value(pl_data, 1, "profitLossForPeriod")
            cfo_curr = get_value(cf_data, 0, "cashFlowsFromOperatingActivities")
            cfo_prev = get_value(cf_data, 1, "cashFlowsFromOperatingActivities")
            
            year_curr = pl_data[0].get("year", fiscal_year)
            year_prev = pl_data[1].get("year", fiscal_year - 1) if len(pl_data) > 1 else fiscal_year - 1
            
            pat_growth = ((pat_curr - pat_prev) / abs(pat_prev) * 100) if pat_prev != 0 else 0
            cfo_growth = ((cfo_curr - cfo_prev) / abs(cfo_prev) * 100) if cfo_prev != 0 else 0
            
            triggered = pat_growth > 10 and abs(cfo_growth) < 5
            
            calculation_detail = (
                f"PAT FY{year_curr}: ₹{pat_curr/10000000:.2f} Cr | "
                f"PAT FY{year_prev}: ₹{pat_prev/10000000:.2f} Cr | "
                f"PAT Growth: {pat_growth:.1f}% | "
                f"CFO FY{year_curr}: ₹{cfo_curr/10000000:.2f} Cr | "
                f"CFO FY{year_prev}: ₹{cfo_prev/10000000:.2f} Cr | "
                f"CFO Growth: {cfo_growth:.1f}% | "
                f"Trigger condition: PAT growth > 10% AND CFO growth < 5%"
            )
            
            flags.append({
                "flag_id": 7,
                "flag_name": "PAT Growing, CFO Flat",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "pat_curr": pat_curr,
                    "pat_prev": pat_prev,
                    "pat_growth": round(pat_growth, 2),
                    "cfo_curr": cfo_curr,
                    "cfo_prev": cfo_prev,
                    "cfo_growth": round(cfo_growth, 2),
                    "year_curr": year_curr,
                    "year_prev": year_prev
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #7: {e}")
            flags.append(self._get_default_flag(7, "PAT Growing, CFO Flat", "Cash Flow", "HIGH"))
        
        # Flag #8: Receivables Growing > Revenue
        try:
            receivables_curr = get_value(bs_data, 0, "tradeReceivablesCurrent")
            receivables_prev = get_value(bs_data, 1, "tradeReceivablesCurrent")
            revenue_curr = get_value(pl_data, 0, "revenueFromOperations")
            revenue_prev = get_value(pl_data, 1, "revenueFromOperations")
            
            year_curr = bs_data[0].get("year", fiscal_year)
            year_prev = bs_data[1].get("year", fiscal_year - 1) if len(bs_data) > 1 else fiscal_year - 1
            
            recv_growth = ((receivables_curr - receivables_prev) / abs(receivables_prev) * 100) if receivables_prev != 0 else 0
            rev_growth = ((revenue_curr - revenue_prev) / abs(revenue_prev) * 100) if revenue_prev != 0 else 0
            
            triggered = recv_growth > rev_growth and (recv_growth - rev_growth) > 10
            
            calculation_detail = (
                f"Receivables FY{year_curr}: ₹{receivables_curr/10000000:.2f} Cr | "
                f"Receivables FY{year_prev}: ₹{receivables_prev/10000000:.2f} Cr | "
                f"Receivables Growth: {recv_growth:.1f}% | "
                f"Revenue FY{year_curr}: ₹{revenue_curr/10000000:.2f} Cr | "
                f"Revenue FY{year_prev}: ₹{revenue_prev/10000000:.2f} Cr | "
                f"Revenue Growth: {rev_growth:.1f}% | "
                f"Difference: {recv_growth - rev_growth:.1f}% | "
                f"Trigger condition: Receivables growth > Revenue growth by >10%"
            )
            
            flags.append({
                "flag_id": 8,
                "flag_name": "Receivables Growing > Revenue",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "receivables_curr": receivables_curr,
                    "receivables_prev": receivables_prev,
                    "receivables_growth": round(recv_growth, 2),
                    "revenue_curr": revenue_curr,
                    "revenue_prev": revenue_prev,
                    "revenue_growth": round(rev_growth, 2),
                    "year_curr": year_curr,
                    "year_prev": year_prev
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #8: {e}")
            flags.append(self._get_default_flag(8, "Receivables Growing > Revenue", "Cash Flow", "HIGH"))
        
        # Flag #9: Inventory Growing > COGS
        try:
            inventory_curr = get_value(bs_data, 0, "inventories")
            inventory_prev = get_value(bs_data, 1, "inventories")
            cogs_curr = get_value(pl_data, 0, "costofGoodsSold")
            cogs_prev = get_value(pl_data, 1, "costofGoodsSold")
            
            year_curr = bs_data[0].get("year", fiscal_year)
            year_prev = bs_data[1].get("year", fiscal_year - 1) if len(bs_data) > 1 else fiscal_year - 1
            
            inv_growth = ((inventory_curr - inventory_prev) / abs(inventory_prev) * 100) if inventory_prev != 0 else 0
            cogs_growth = ((cogs_curr - cogs_prev) / abs(cogs_prev) * 100) if cogs_prev != 0 else 0
            
            triggered = inv_growth > cogs_growth and (inv_growth - cogs_growth) > 10
            
            calculation_detail = (
                f"Inventory FY{year_curr}: ₹{inventory_curr/10000000:.2f} Cr | "
                f"Inventory FY{year_prev}: ₹{inventory_prev/10000000:.2f} Cr | "
                f"Inventory Growth: {inv_growth:.1f}% | "
                f"COGS FY{year_curr}: ₹{cogs_curr/10000000:.2f} Cr | "
                f"COGS FY{year_prev}: ₹{cogs_prev/10000000:.2f} Cr | "
                f"COGS Growth: {cogs_growth:.1f}% | "
                f"Difference: {inv_growth - cogs_growth:.1f}% | "
                f"Trigger condition: Inventory growth > COGS growth by >10%"
            )
            
            flags.append({
                "flag_id": 9,
                "flag_name": "Inventory Growing > COGS",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "inventory_curr": inventory_curr,
                    "inventory_prev": inventory_prev,
                    "inventory_growth": round(inv_growth, 2),
                    "cogs_curr": cogs_curr,
                    "cogs_prev": cogs_prev,
                    "cogs_growth": round(cogs_growth, 2),
                    "year_curr": year_curr,
                    "year_prev": year_prev
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #9: {e}")
            flags.append(self._get_default_flag(9, "Inventory Growing > COGS", "Cash Flow", "HIGH"))
        
        # Flag #10: Capex > Depreciation (>3x)
        try:
            capex = abs(get_value(cf_data, 0, "paymentsForAssetAcquisition"))
            depreciation = get_value(pl_data, 0, "depreciationAndAmortisation")
            
            year_curr = cf_data[0].get("year", fiscal_year)
            
            ratio = capex / depreciation if depreciation > 0 else 0
            triggered = ratio > 3
            
            calculation_detail = (
                f"Capex FY{year_curr}: ₹{capex/10000000:.2f} Cr | "
                f"Depreciation FY{year_curr}: ₹{depreciation/10000000:.2f} Cr | "
                f"Capex/Depreciation Ratio: {ratio:.2f}x | "
                f"Trigger condition: Ratio > 3x"
            )
            
            flags.append({
                "flag_id": 10,
                "flag_name": "Capex > Depreciation (>3x)",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 90,
                "value": {
                    "capex": capex,
                    "depreciation": depreciation,
                    "ratio": round(ratio, 2),
                    "year": year_curr
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #10: {e}")
            flags.append(self._get_default_flag(10, "Capex > Depreciation (>3x)", "Cash Flow", "MEDIUM"))
        
        # Flag #11: Frequent Exceptional Items
        try:
            exceptional_years = []
            for i in range(min(3, len(pl_data))):
                exceptional_items = get_value(pl_data, i, "exceptionalItemsBeforeTax")
                year = pl_data[i].get("year", fiscal_year - i)
                if abs(exceptional_items) > 0:
                    exceptional_years.append({
                        "year": year,
                        "amount": exceptional_items
                    })
            
            exceptional_count = len(exceptional_years)
            triggered = exceptional_count >= 2
            
            years_detail = " | ".join([
                f"FY{item['year']}: ₹{item['amount']/10000000:.2f} Cr"
                for item in exceptional_years
            ])
            
            calculation_detail = (
                f"Exceptional items found in {exceptional_count} out of last 3 years | "
                f"{years_detail if years_detail else 'None'} | "
                f"Trigger condition: Present in ≥2 years"
            )
            
            flags.append({
                "flag_id": 11,
                "flag_name": "Frequent Exceptional Items",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 80,
                "value": {
                    "years_with_exceptional_items": exceptional_count,
                    "details": exceptional_years
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #11: {e}")
            flags.append(self._get_default_flag(11, "Frequent Exceptional Items", "Cash Flow", "MEDIUM"))
        
        # Flag #12: Negative CFO
        try:
            cfo_curr = get_value(cf_data, 0, "cashFlowsFromOperatingActivities")
            year_curr = cf_data[0].get("year", fiscal_year)
            
            triggered = cfo_curr < 0
            
            calculation_detail = (
                f"Cash from Operations FY{year_curr}: ₹{cfo_curr/10000000:.2f} Cr | "
                f"Trigger condition: CFO < 0"
            )
            
            flags.append({
                "flag_id": 12,
                "flag_name": "Negative CFO",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 95,
                "value": {
                    "cash_from_operations": cfo_curr,
                    "year": year_curr
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #12: {e}")
            flags.append(self._get_default_flag(12, "Negative CFO", "Cash Flow", "HIGH"))
        
        # Flag #13: CCC > 120 days
        try:
            receivables = get_value(bs_data, 0, "tradeReceivablesCurrent")
            inventory = get_value(bs_data, 0, "inventories")
            payables = get_value(bs_data, 0, "tradePayablesCurrent")
            revenue = get_value(pl_data, 0, "revenueFromOperations")
            cogs = get_value(pl_data, 0, "costofGoodsSold")
            
            year_curr = bs_data[0].get("year", fiscal_year)
            
            # Days calculations
            dso = (receivables / revenue * 365) if revenue > 0 else 0
            dio = (inventory / cogs * 365) if cogs > 0 else 0
            dpo = (payables / cogs * 365) if cogs > 0 else 0
            
            ccc = dso + dio - dpo
            triggered = ccc > 120
            
            calculation_detail = (
                f"FY{year_curr} | "
                f"DSO (Receivables/Revenue × 365): {dso:.1f} days | "
                f"DIO (Inventory/COGS × 365): {dio:.1f} days | "
                f"DPO (Payables/COGS × 365): {dpo:.1f} days | "
                f"CCC (DSO + DIO - DPO): {ccc:.1f} days | "
                f"Receivables: ₹{receivables/10000000:.2f} Cr | "
                f"Inventory: ₹{inventory/10000000:.2f} Cr | "
                f"Payables: ₹{payables/10000000:.2f} Cr | "
                f"Trigger condition: CCC > 120 days"
            )
            
            flags.append({
                "flag_id": 13,
                "flag_name": "CCC > 120 days",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "ccc": round(ccc, 1),
                    "dso": round(dso, 1),
                    "dio": round(dio, 1),
                    "dpo": round(dpo, 1),
                    "receivables": receivables,
                    "inventory": inventory,
                    "payables": payables,
                    "year": year_curr
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #13: {e}")
            flags.append(self._get_default_flag(13, "CCC > 120 days", "Cash Flow", "MEDIUM"))
        
        # Flag #14: Unusual Other Income > 10%
        try:
            other_income = get_value(pl_data, 0, "otherIncome")
            revenue = get_value(pl_data, 0, "revenueFromOperations")
            
            year_curr = pl_data[0].get("year", fiscal_year)
            
            percentage = (other_income / revenue * 100) if revenue > 0 else 0
            triggered = percentage > 10
            
            calculation_detail = (
                f"Other Income FY{year_curr}: ₹{other_income/10000000:.2f} Cr | "
                f"Revenue FY{year_curr}: ₹{revenue/10000000:.2f} Cr | "
                f"Other Income %: {percentage:.2f}% | "
                f"Trigger condition: Other Income > 10% of Revenue"
            )
            
            flags.append({
                "flag_id": 14,
                "flag_name": "Unusual Other Income > 10%",
                "category": "Cash Flow",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "other_income": other_income,
                    "revenue": revenue,
                    "percentage": round(percentage, 2),
                    "year": year_curr
                }
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
                    value = data_list[index].get(field_name, default)
                    return float(value) if value is not None else default
                return default
            except (ValueError, TypeError):
                return default
        
        # Flag #32: Debt Growing Faster than Equity
        try:
            # Total debt = current borrowings + non-current borrowings
            debt_curr = (get_value(bs_data, 0, "borrowingsCurrent") + 
                        get_value(bs_data, 0, "borrowingsNoncurrent"))
            debt_prev = (get_value(bs_data, 1, "borrowingsCurrent") + 
                        get_value(bs_data, 1, "borrowingsNoncurrent"))
            equity_curr = get_value(bs_data, 0, "totalEquity")
            equity_prev = get_value(bs_data, 1, "totalEquity")
            
            year_curr = bs_data[0].get("year", fiscal_year)
            year_prev = bs_data[1].get("year", fiscal_year - 1) if len(bs_data) > 1 else fiscal_year - 1
            
            debt_growth = ((debt_curr - debt_prev) / abs(debt_prev) * 100) if debt_prev != 0 else 0
            equity_growth = ((equity_curr - equity_prev) / abs(equity_prev) * 100) if equity_prev != 0 else 0
            
            triggered = debt_growth > equity_growth and (debt_growth - equity_growth) > 10
            
            calculation_detail = (
                f"Total Debt FY{year_curr}: ₹{debt_curr/10000000:.2f} Cr | "
                f"Total Debt FY{year_prev}: ₹{debt_prev/10000000:.2f} Cr | "
                f"Debt Growth: {debt_growth:.1f}% | "
                f"Total Equity FY{year_curr}: ₹{equity_curr/10000000:.2f} Cr | "
                f"Total Equity FY{year_prev}: ₹{equity_prev/10000000:.2f} Cr | "
                f"Equity Growth: {equity_growth:.1f}% | "
                f"Difference: {debt_growth - equity_growth:.1f}% | "
                f"Trigger condition: Debt growth > Equity growth by >10%"
            )
            
            flags.append({
                "flag_id": 32,
                "flag_name": "Debt Growing Faster than Equity",
                "category": "Balance Sheet",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "debt_curr": debt_curr,
                    "debt_prev": debt_prev,
                    "debt_growth": round(debt_growth, 2),
                    "equity_curr": equity_curr,
                    "equity_prev": equity_prev,
                    "equity_growth": round(equity_growth, 2),
                    "year_curr": year_curr,
                    "year_prev": year_prev
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #32: {e}")
            flags.append(self._get_default_flag(32, "Debt Growing Faster than Equity", "Balance Sheet", "HIGH"))
        
        # Flag #33: Interest Coverage < 2x
        try:
            # EBIT = profitBeforeTax + financeCosts
            pbt = get_value(pl_data, 0, "profitBeforeTax")
            interest_expense = get_value(pl_data, 0, "financeCosts")
            ebit = pbt + interest_expense
            
            year_curr = pl_data[0].get("year", fiscal_year)
            
            coverage = ebit / interest_expense if interest_expense > 0 else 999
            triggered = coverage < 2 and interest_expense > 0
            
            calculation_detail = (
                f"FY{year_curr} | "
                f"Profit Before Tax: ₹{pbt/10000000:.2f} Cr | "
                f"Finance Costs (Interest): ₹{interest_expense/10000000:.2f} Cr | "
                f"EBIT (PBT + Interest): ₹{ebit/10000000:.2f} Cr | "
                f"Interest Coverage (EBIT/Interest): {coverage:.2f}x | "
                f"Trigger condition: Coverage < 2x"
            )
            
            flags.append({
                "flag_id": 33,
                "flag_name": "Interest Coverage < 2x",
                "category": "Balance Sheet",
                "triggered": triggered,
                "severity": "HIGH",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 90,
                "value": {
                    "ebit": ebit,
                    "interest_expense": interest_expense,
                    "coverage": round(coverage, 2),
                    "year": year_curr
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #33: {e}")
            flags.append(self._get_default_flag(33, "Interest Coverage < 2x", "Balance Sheet", "HIGH"))
        
        # Flag #38: Intangible Assets Growing Fast
        try:
            intangibles_curr = get_value(bs_data, 0, "otherIntangibleAssets")
            intangibles_prev = get_value(bs_data, 1, "otherIntangibleAssets")
            
            year_curr = bs_data[0].get("year", fiscal_year)
            year_prev = bs_data[1].get("year", fiscal_year - 1) if len(bs_data) > 1 else fiscal_year - 1
            
            growth = ((intangibles_curr - intangibles_prev) / abs(intangibles_prev) * 100) if intangibles_prev != 0 else 0
            triggered = growth > 30
            
            calculation_detail = (
                f"Intangible Assets FY{year_curr}: ₹{intangibles_curr/10000000:.2f} Cr | "
                f"Intangible Assets FY{year_prev}: ₹{intangibles_prev/10000000:.2f} Cr | "
                f"Growth: {growth:.1f}% | "
                f"Trigger condition: Growth > 30%"
            )
            
            flags.append({
                "flag_id": 38,
                "flag_name": "Intangible Assets Growing Fast",
                "category": "Balance Sheet",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 80,
                "value": {
                    "intangibles_curr": intangibles_curr,
                    "intangibles_prev": intangibles_prev,
                    "growth_percentage": round(growth, 2),
                    "year_curr": year_curr,
                    "year_prev": year_prev
                }
            })
        except Exception as e:
            logger.error(f"Error calculating flag #38: {e}")
            flags.append(self._get_default_flag(38, "Intangible Assets Growing Fast", "Balance Sheet", "MEDIUM"))
        
        return flags
    
    def _calculate_revenue_flags(self, pl_annual: List[Dict], pl_quarterly: List[Dict], 
                                  fiscal_year: int) -> List[Dict]:
        """Calculate 1 revenue quality flag (#39)."""
        flags = []
        
        def get_value(data_list, index, field_name, default=0):
            try:
                if index < len(data_list):
                    value = data_list[index].get(field_name, default)
                    return float(value) if value is not None else default
                return default
            except (ValueError, TypeError):
                return default
        
        # Flag #39: Revenue Concentrated in Q4 (>40%)
        try:
            if not pl_quarterly or len(pl_quarterly) < 4:
                flags.append(self._get_default_flag(39, "Revenue Concentrated in Q4 (>40%)", 
                                                    "Revenue Quality", "MEDIUM",
                                                    "Quarterly revenue data not available from FinEdge API"))
                return flags
            
            # Get Q4 revenue (most recent quarter should be Q4)
            # Filter quarters for the fiscal year
            year_quarters = [q for q in pl_quarterly if q.get("year") == fiscal_year]
            
            if len(year_quarters) < 4:
                flags.append(self._get_default_flag(39, "Revenue Concentrated in Q4 (>40%)", 
                                                    "Revenue Quality", "MEDIUM",
                                                    f"Incomplete quarterly data for FY{fiscal_year}"))
                return flags
            
            # Get annual revenue for the fiscal year
            annual_revenue = get_value(pl_annual, 0, "revenueFromOperations")
            
            # Calculate quarterly revenues
            q_revenues = []
            for i, quarter in enumerate(year_quarters[:4]):
                q_rev = get_value([quarter], 0, "revenueFromOperations")
                q_revenues.append({
                    "quarter": f"Q{i+1}",
                    "revenue": q_rev,
                    "percentage": (q_rev / annual_revenue * 100) if annual_revenue > 0 else 0
                })
            
            # Q4 is typically the last quarter
            q4_revenue = q_revenues[-1]["revenue"]
            q4_percentage = (q4_revenue / annual_revenue * 100) if annual_revenue > 0 else 0
            
            triggered = q4_percentage > 40
            
            quarters_detail = " | ".join([
                f"{q['quarter']}: ₹{q['revenue']/10000000:.2f} Cr ({q['percentage']:.1f}%)"
                for q in q_revenues
            ])
            
            calculation_detail = (
                f"FY{fiscal_year} | "
                f"Annual Revenue: ₹{annual_revenue/10000000:.2f} Cr | "
                f"{quarters_detail} | "
                f"Q4 concentration: {q4_percentage:.1f}% | "
                f"Trigger condition: Q4 > 40% of annual revenue"
            )
            
            flags.append({
                "flag_id": 39,
                "flag_name": "Revenue Concentrated in Q4 (>40%)",
                "category": "Revenue Quality",
                "triggered": triggered,
                "severity": "MEDIUM",
                "evidence": calculation_detail,
                "page_references": [],
                "confidence": 85,
                "value": {
                    "annual_revenue": annual_revenue,
                    "q4_revenue": q4_revenue,
                    "q4_percentage": round(q4_percentage, 2),
                    "quarters": q_revenues,
                    "year": fiscal_year
                }
            })
            
        except Exception as e:
            logger.error(f"Error calculating flag #39: {e}")
            flags.append(self._get_default_flag(39, "Revenue Concentrated in Q4 (>40%)", 
                                               "Revenue Quality", "MEDIUM"))
        
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