"""Portfolio service for CSV parsing, portfolio management, and real-time prices."""

import io
import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.company import Company
from app.models.portfolio import Holding
from app.schemas.portfolio import HoldingCreate
from app.services.finedge_client import finedge_client

logger = logging.getLogger(__name__)

BROKER_FORMATS = {
    'zerodha': {'symbol': 'symbol', 'quantity': 'quantity', 'avg_price': 'average_price'},
    'groww': {'symbol': 'stock_name', 'quantity': 'qty', 'avg_price': 'avg_cost'},
    'upstox': {'symbol': 'symbol', 'quantity': 'quantity', 'avg_price': 'buy_avg'},
    'generic': {'symbol': 'Symbol', 'quantity': 'Quantity', 'avg_price': 'Avg Price'},
}


def load_symbol_mapping() -> Dict[str, str]:
    """Load symbol mapping from JSON file."""
    mapping_file = Path(__file__).parent.parent.parent / "data" / "symbol_mapping.json"
    
    if mapping_file.exists():
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load symbol mapping: {e}")
            return {}
    else:
        logger.warning(f"Symbol mapping file not found at {mapping_file}")
        return {}


# Load symbol mapping at module level
SYMBOL_MAPPING = load_symbol_mapping()


def map_broker_symbol(broker_symbol: str) -> str:
    """
    Map broker symbol to FinEdge API symbol.
    
    Args:
        broker_symbol: Symbol from Zerodha/Upstox/etc (e.g., "NSE:RELIANCE" or "RELIANCE")
        
    Returns:
        Mapped symbol for FinEdge API
    """
    # Clean symbol (remove exchange prefix if exists)
    clean_symbol = broker_symbol.split(":")[-1].strip().upper()
    
    # Try to map using symbol_mapping.json
    if clean_symbol in SYMBOL_MAPPING:
        return SYMBOL_MAPPING[clean_symbol]
    
    # Fallback: return cleaned symbol as-is
    return clean_symbol


def get_real_time_price(symbol: str) -> Optional[Dict]:
    """
    Get real-time price data for a symbol from FinEdge API.
    
    Returns:
        {
            "current_price": 2500.50,
            "change": 25.30,
            "change_percent": 1.02,
            "open": 2490.00,
            "high": 2510.00,
            "low": 2485.00,
            "volume": 1234567,
            "last_updated": "2025-02-16T10:30:00"
        }
    """
    try:
        # Map symbol if needed
        mapped_symbol = map_broker_symbol(symbol)
        
        # Fetch live quote from FinEdge
        quote = finedge_client.get_live_quote(mapped_symbol)
        
        if not quote:
            return None
        
        return {
            "current_price": quote.get("current_price"),
            "change_percent": quote.get("change_percent"),
            "high52": quote.get("high52"),
            "low52": quote.get("low52"),
            "volume": quote.get("volume"),
            "market_cap": quote.get("market_cap"),
            "trade_time": quote.get("trade_time"),
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch real-time price for {symbol}: {e}")
        return None


def detect_broker_format(df: pd.DataFrame) -> str:
    """Detect CSV format by matching column names."""
    columns = set(df.columns.str.lower().str.strip())
    for broker, mapping in BROKER_FORMATS.items():
        required_cols = set(v.lower() for v in mapping.values())
        if required_cols.issubset(columns):
            return broker
    return 'generic'


def parse_portfolio_csv(file_content: bytes) -> List[HoldingCreate]:
    """Parse CSV and return standardized holdings."""
    df = pd.read_csv(io.BytesIO(file_content))
    if df.empty:
        raise ValueError("CSV file is empty")

    broker = detect_broker_format(df)
    mapping = BROKER_FORMATS[broker]
    holdings = []

    for idx, row in df.iterrows():
        try:
            symbol_col = quantity_col = price_col = None
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower == mapping['symbol'].lower():
                    symbol_col = col
                elif col_lower == mapping['quantity'].lower():
                    quantity_col = col
                elif col_lower == mapping['avg_price'].lower():
                    price_col = col

            if not all([symbol_col, quantity_col, price_col]):
                continue

            symbol = str(row[symbol_col]).strip().upper()
            quantity = int(float(row[quantity_col]))
            avg_price = float(row[price_col])

            if symbol and symbol != 'NAN' and quantity > 0 and avg_price > 0:
                holdings.append(HoldingCreate(symbol=symbol, quantity=quantity, avg_price=avg_price))
        except:
            continue

    if not holdings:
        raise ValueError("No valid holdings found in CSV")
    return holdings


def match_symbols_to_companies(db: Session, holdings: List[HoldingCreate]) -> Tuple[Dict, List[str]]:
    """Match symbols to companies. Returns (matched_dict, unmatched_list)."""
    matched = {}
    unmatched = []

    for holding in holdings:
        company = db.query(Company).filter(
            (Company.nse_symbol == holding.symbol) | (Company.bse_code == holding.symbol)
        ).first()

        if company:
            matched[holding.symbol] = {'company': company, 'holding': holding}
        else:
            unmatched.append(holding.symbol)

    return matched, unmatched


def get_risk_scores(db: Session, company_ids: List[str]) -> Dict[str, dict]:
    """Fetch latest risk scores for companies."""
    risk_data = {}

    for company_id in company_ids:
        # Join via AnnualReport — AnalysisResult has no direct company_id field
        latest_analysis = db.query(AnalysisResult).join(
            AnnualReport, AnalysisResult.report_id == AnnualReport.id
        ).filter(
            AnnualReport.company_id == company_id
        ).order_by(AnalysisResult.analyzed_at.desc()).first()

        if latest_analysis:
            # flags_triggered_count is stored directly on AnalysisResult
            risk_data[str(company_id)] = {
                'risk_score': latest_analysis.risk_score,
                'risk_level': latest_analysis.risk_level,
                'flags_count': latest_analysis.flags_triggered_count,
                'latest_analysis_id': str(latest_analysis.id),
            }
        else:
            risk_data[str(company_id)] = {'risk_score': None, 'risk_level': None, 'flags_count': None, 'latest_analysis_id': None}

    return risk_data


def get_latest_analysis_id_for_company(db: Session, company_id) -> Optional[str]:
    """Fetch the latest analysis ID for a company (via AnnualReport join)."""
    try:
        latest = db.query(AnalysisResult).join(
            AnnualReport, AnalysisResult.report_id == AnnualReport.id
        ).filter(
            AnnualReport.company_id == company_id
        ).order_by(AnalysisResult.analyzed_at.desc()).first()
        return str(latest.id) if latest else None
    except Exception:
        return None


def calculate_portfolio_metrics(holdings: List[Holding]) -> dict:
    """Calculate aggregate portfolio metrics."""
    total_investment = sum(float(h.investment_value) for h in holdings)
    risk_scores = [h.risk_score for h in holdings if h.risk_score is not None]
    average_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else None
    high_risk_count = sum(1 for h in holdings if h.risk_score and h.risk_score >= 60)

    return {
        'total_investment': total_investment,
        'average_risk_score': average_risk_score,
        'high_risk_count': high_risk_count,
    }