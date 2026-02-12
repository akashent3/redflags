"""Standalone models for red flags - no database dependency."""

import enum
from dataclasses import dataclass, field
from typing import Dict, List


class FlagSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FlagCategory(str, enum.Enum):
    AUDITOR = "Auditor"
    CASH_FLOW = "Cash Flow"
    RELATED_PARTY = "Related Party"
    PROMOTER = "Promoter"
    GOVERNANCE = "Governance"
    BALANCE_SHEET = "Balance Sheet"
    REVENUE = "Revenue Quality"
    TEXTUAL = "Textual Analysis"


@dataclass
class RedFlagResult:
    """Result of a red flag check."""
    flag_number: int
    flag_name: str
    category: FlagCategory
    severity: FlagSeverity
    is_triggered: bool
    confidence_score: float  # 0-100
    evidence_text: str
    page_references: List[int] = field(default_factory=list)
    extracted_data: Dict = field(default_factory=dict)
    detection_method: str = "rule_based"
