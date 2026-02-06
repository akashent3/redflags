"""Base classes and utilities for red flag detection."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.models.red_flag import FlagCategory, FlagSeverity

logger = logging.getLogger(__name__)


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
    page_references: List[int]
    extracted_data: Dict  # Source data used for detection
    detection_method: str  # 'rule_based', 'llm', 'hybrid'


class RedFlagBase:
    """Base class for all red flag detectors."""

    def __init__(self):
        """Initialize red flag with metadata."""
        self.flag_number: int = 0
        self.flag_name: str = ""
        self.category: FlagCategory = FlagCategory.AUDITOR
        self.severity: FlagSeverity = FlagSeverity.MEDIUM
        self.description: str = ""

    def check(self, data: Dict) -> RedFlagResult:
        """
        Check if this red flag is triggered.

        Args:
            data: Dictionary containing:
                - sections: Dict mapping section names to extracted text
                - financial_data: Dict with extracted financial metrics
                - extraction_result: Full PDF extraction result

        Returns:
            RedFlagResult with detection outcome

        Raises:
            NotImplementedError: Must be overridden in subclass
        """
        raise NotImplementedError(
            f"RedFlag {self.flag_number} ({self.flag_name}) must implement check() method"
        )

    # Helper calculation methods

    @staticmethod
    def calculate_cagr(values: List[float], years: int) -> float:
        """
        Calculate Compound Annual Growth Rate.

        Args:
            values: List of values in chronological order
            years: Number of years in period

        Returns:
            CAGR as decimal (e.g., 0.15 = 15%)
        """
        if len(values) < 2 or values[0] == 0 or values[0] is None:
            return 0.0

        try:
            cagr = pow(values[-1] / values[0], 1 / years) - 1
            return cagr
        except (ValueError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        """
        Calculate simple growth rate between two periods.

        Args:
            current: Current period value
            previous: Previous period value

        Returns:
            Growth rate as decimal (e.g., 0.20 = 20% growth)
        """
        if previous == 0 or previous is None:
            return 0.0

        try:
            growth = (current - previous) / previous
            return growth
        except (ValueError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def calculate_ratio(numerator: float, denominator: float) -> float:
        """
        Safe ratio calculation with zero-division handling.

        Args:
            numerator: Numerator value
            denominator: Denominator value

        Returns:
            Ratio value, or 0.0 if denominator is zero
        """
        if denominator == 0 or denominator is None:
            return 0.0

        try:
            return numerator / denominator
        except (ValueError, ZeroDivisionError, TypeError):
            return 0.0

    @staticmethod
    def extract_value(data: Dict, *keys, default=0.0) -> float:
        """
        Safely extract nested value from dictionary.

        Args:
            data: Dictionary to extract from
            *keys: Path to value (e.g., 'financial_data', 'profit_loss', 'revenue')
            default: Default value if key not found

        Returns:
            Extracted value or default

        Example:
            revenue = extract_value(data, 'financial_data', 'profit_loss', 'revenue', 'value')
        """
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, {})
            else:
                return default

        # Handle case where current is a dict with 'value' key
        if isinstance(current, dict) and 'value' in current:
            return float(current.get('value', default))

        # Try to convert to float
        try:
            return float(current) if current else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_percentage(value: float) -> float:
        """
        Convert decimal to percentage (0.15 -> 15.0).

        Args:
            value: Decimal value

        Returns:
            Percentage value
        """
        return value * 100.0

    def create_not_triggered_result(self, reason: str = "") -> RedFlagResult:
        """
        Create a RedFlagResult for when flag is not triggered.

        Args:
            reason: Optional reason why flag was not triggered

        Returns:
            RedFlagResult with is_triggered=False
        """
        return RedFlagResult(
            flag_number=self.flag_number,
            flag_name=self.flag_name,
            category=self.category,
            severity=self.severity,
            is_triggered=False,
            confidence_score=0.0,
            evidence_text=reason if reason else "No red flag detected",
            page_references=[],
            extracted_data={},
            detection_method="rule_based",
        )

    def create_triggered_result(
        self,
        evidence: str,
        confidence: float = 90.0,
        page_refs: List[int] = None,
        extracted_data: Dict = None,
        detection_method: str = "rule_based",
    ) -> RedFlagResult:
        """
        Create a RedFlagResult for when flag is triggered.

        Args:
            evidence: Evidence text explaining why flag triggered
            confidence: Confidence score (0-100)
            page_refs: List of page numbers with evidence
            extracted_data: Source data used for detection
            detection_method: Detection method used

        Returns:
            RedFlagResult with is_triggered=True
        """
        return RedFlagResult(
            flag_number=self.flag_number,
            flag_name=self.flag_name,
            category=self.category,
            severity=self.severity,
            is_triggered=True,
            confidence_score=confidence,
            evidence_text=evidence,
            page_references=page_refs or [],
            extracted_data=extracted_data or {},
            detection_method=detection_method,
        )
