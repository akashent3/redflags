"""JSON schema definitions matching the current RedFlags database structure."""

from typing import List, Dict, Any
from datetime import datetime


def create_analysis_output(
    company_name: str,
    annual_reports: List[Dict],
    risk_score: int,
    risk_level: str,
    category_scores: Dict[str, int],
    red_flags: List[Dict],
    financial_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create the final JSON output matching the current database schema.
    
    Schema matches:
    - companies table
    - annual_reports table
    - analysis_results table
    - red_flags table
    
    Returns:
        Dict following the exact structure of current RedFlags app
    """
    return {
        "company": {
            "name": company_name,
            "analysis_date": datetime.now().isoformat()
        },
        "annual_reports": annual_reports,
        "analysis_result": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "category_scores": category_scores,
            "flags_triggered_count": sum(1 for flag in red_flags if flag["is_triggered"]),
            "analyzed_at": datetime.now().isoformat()
        },
        "red_flags": red_flags,
        "financial_data": financial_data
    }


def create_red_flag_result(
    flag_number: int,
    flag_name: str,
    category: str,
    severity: str,
    is_triggered: bool,
    confidence_score: float,
    evidence_text: str,
    page_references: List[int],
    extracted_data: Dict[str, Any],
    detection_method: str = "llm"
) -> Dict[str, Any]:
    """
    Create a red flag result matching the red_flags table schema.
    
    Args:
        flag_number: 1-54
        flag_name: Human-readable flag name
        category: AUDITOR, CASH_FLOW, RELATED_PARTY, PROMOTER, 
                 GOVERNANCE, BALANCE_SHEET, REVENUE, TEXTUAL
        severity: CRITICAL, HIGH, MEDIUM, LOW
        is_triggered: Whether the flag was detected
        confidence_score: 0-100
        evidence_text: Supporting evidence from the document
        page_references: List of page numbers where evidence found
        extracted_data: Raw data used for detection
        detection_method: 'llm', 'rule_based', or 'hybrid'
    """
    return {
        "flag_number": flag_number,
        "flag_name": flag_name,
        "category": category,
        "severity": severity,
        "is_triggered": is_triggered,
        "confidence_score": round(confidence_score, 2),
        "evidence_text": evidence_text,
        "page_references": page_references,
        "extracted_data": extracted_data,
        "detection_method": detection_method
    }


# Category mappings
CATEGORIES = {
    "AUDITOR": {"weight": 0.20, "flags": list(range(1, 9))},
    "CASH_FLOW": {"weight": 0.18, "flags": list(range(9, 17))},
    "RELATED_PARTY": {"weight": 0.15, "flags": list(range(17, 24))},
    "PROMOTER": {"weight": 0.15, "flags": list(range(24, 30))},
    "GOVERNANCE": {"weight": 0.12, "flags": list(range(30, 37))},
    "BALANCE_SHEET": {"weight": 0.10, "flags": list(range(37, 44))},
    "REVENUE": {"weight": 0.05, "flags": list(range(44, 49))},
    "TEXTUAL": {"weight": 0.05, "flags": list(range(49, 55))}
}

# Severity point mappings
SEVERITY_POINTS = {
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3
}

# Risk level thresholds
RISK_LEVELS = [
    (0, 20, "LOW"),
    (20, 40, "MODERATE"),
    (40, 60, "ELEVATED"),
    (60, 80, "HIGH"),
    (80, 100, "CRITICAL")
]
