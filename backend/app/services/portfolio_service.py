"""Portfolio service for CSV parsing and portfolio management."""

import io
import logging
from typing import Dict, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from app.models.analysis_result import AnalysisResult
from app.models.company import Company
from app.models.portfolio import Holding
from app.schemas.portfolio import HoldingCreate

logger = logging.getLogger(__name__)

BROKER_FORMATS = {
    'zerodha': {'symbol': 'symbol', 'quantity': 'quantity', 'avg_price': 'average_price'},
    'groww': {'symbol': 'stock_name', 'quantity': 'qty', 'avg_price': 'avg_cost'},
    'upstox': {'symbol': 'symbol', 'quantity': 'quantity', 'avg_price': 'buy_avg'},
    'generic': {'symbol': 'Symbol', 'quantity': 'Quantity', 'avg_price': 'Avg Price'},
}


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
        latest_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.company_id == company_id
        ).order_by(AnalysisResult.created_at.desc()).first()

        if latest_analysis:
            flags_count = sum(1 for f in latest_analysis.red_flags if f.is_triggered)
            risk_data[str(company_id)] = {
                'risk_score': latest_analysis.overall_risk_score,
                'risk_level': latest_analysis.risk_level,
                'flags_count': flags_count,
            }
        else:
            risk_data[str(company_id)] = {'risk_score': None, 'risk_level': None, 'flags_count': None}

    return risk_data


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
